import contextlib
import os
import time
import unicodedata
import pathlib
import dropbox
from logging import Logger
from datetime import datetime, timezone
from posixpath import join as urljoin
from dataclasses import dataclass
from config import Config

@dataclass
class FileMetadata:
    name: str
    path: str
    client_modified: datetime
    size: int

class FileStore:
    def __init__(self, conf: Config, logger: Logger):
        self.dry_run = conf.dry_run
        self.root_path = conf.local_dir
        self.logger = logger

    def save(self, dbox_path: str, content, metadata: dropbox.files.FileMetadata):
        file_path = self.get_absolute_path(dbox_path)
        if self.dry_run:
            self.logger.info('dry run mode. Skip saving file {}'.format(file_path))
        else:
            base_path = os.path.dirname(file_path)
            self.__try_create_local_folder(base_path)
            with open(file_path, 'wb') as f:
                f.write(content)
            self.__set_modification_time(file_path, self.__datetime_utc_to_local(metadata.client_modified))
            self.logger.debug('saved file {}...'.format(file_path))

    def __try_create_local_folder(self, path: str):
        if self.dry_run:
            self.logger.info('Dry Run mode. path {}'.format(path))
        else:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def __set_modification_time(self, file_path: str, modified: datetime):
        if self.dry_run:
            self.logger.info('Dry Run mode. file_path {}, modified={}'.format(os.path.basename(file_path), modified))
        else:
            self.logger.debug('file_path={}, modified={}'.format(file_path, modified))
            atime = os.stat(file_path).st_atime
            mtime = modified.timestamp()
            os.utime(file_path, times=(atime, mtime))

    def get_absolute_path(self, dbox_path: str) -> str:
        relative_db_path = dbox_path[1:] if dbox_path.startswith('/') else dbox_path
        result = pathlib.PurePath( self.root_path ).joinpath( relative_db_path )
        self.logger.debug('result={}'.format(result))
        return str(result)

    @staticmethod
    def __datetime_utc_to_local(utc_dt) -> datetime:
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def list_folder(self, dbox_path: str):
        path = self.get_absolute_path(dbox_path)
        self.logger.debug('path={}'.format(path))
        if pathlib.Path(path).exists():
            root, dirs, files = next(os.walk(path))
            normalizedFiles = [unicodedata.normalize('NFC', f) for f in files]
            self.logger.debug('files={}'.format(normalizedFiles))
            return root, dirs, normalizedFiles
        return path, [], []

    def read(self, full_path: str):
        md = self.get_metadata(full_path)
        with open(full_path, 'rb') as f:
            content = f.read()
        return content, md

    @staticmethod
    def get_metadata(full_path: str) -> FileMetadata:
        name = os.path.basename(full_path)
        mtime = os.path.getmtime(full_path)
        client_modified = datetime(*time.gmtime(mtime)[:6])
        size = os.path.getsize(full_path)
        return FileMetadata(name, full_path, client_modified, size)

class DropboxStore:
    def __init__(self, conf: Config, logger: Logger):
        self.dbx = dropbox.Dropbox(conf.token)
        self.dry_run = conf.dry_run
        self.logger = logger

    def list_folder(self, dbox_path):
        self.logger.debug('list path: {}'.format(dbox_path))
        dirs = list()
        files = list()
        try:
            with stopwatch('list_folder', self.logger):
                res = self.dbx.files_list_folder(dbox_path)
        except dropbox.exceptions.ApiError:
            self.logger.warning('Folder listing failed for {} -- assumed empty'.format(dbox_path))
        else:
            for entry in res.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    files.append(entry)
                else:
                    dirs.append(entry)
        self.logger.debug('files={}'.format(files))
        return dbox_path, dirs, files

    def read(self, dbx_path):
        self.logger.debug('dbx_path={}'.format(dbx_path))
        with stopwatch('download', self.logger):
            try:
                meta_data, response = self.dbx.files_download(dbx_path)
            except dropbox.exceptions.HttpError:
                self.logger.exception("*** Dropbox HTTP Error")
                return None
        self.logger.debug('{} bytes; md: {}'.format(len(response.content), meta_data.name))
        return response, meta_data

    def save(self, dbx_path: str, content, metadata: FileMetadata, overwrite: bool):
        self.logger.debug('dbx_path={}'.format(dbx_path))
        write_mode = (dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add)
        with stopwatch('upload %d bytes' % len(content), self.logger):
            if self.dry_run:
                self.logger.info('Dry run mode. Skip uploading {} (modified:{}) using {}'
                    .format(dbx_path, metadata.client_modified, write_mode))
            else:
                try:
                    res = self.dbx.files_upload(content, dbx_path, write_mode, client_modified=metadata.client_modified, mute=True)
                    self.logger.debug('Uploaded as {}'.format(res.name))
                    return res
                except dropbox.exceptions.ApiError:
                    self.logger.exception('*** API error')
                    return None

class FileMapper:
    def __init__(self, fileStore: FileStore, dboxStore: DropboxStore, conf: Config, logger: Logger):
        self.fileStore = fileStore
        self.dboxStore = dboxStore
        self.recursive = conf.recursive
        self.logger = logger

    def map_recursive(self, dbox_path: str):
        self.logger.info('dbox_path={}'.format(dbox_path))
        local_root, local_dirs, local_files = self.fileStore.list_folder(dbox_path)
        dbx_root, dbx_dirs, dbx_files = self.dboxStore.list_folder(dbox_path)
        download_files, upload_files = self.__map_dropbox_files_to_local(local_root, local_files, dbx_root, dbx_files)
        if self.recursive:
            process_folders = self.__map_dropbox_folders_to_local(local_dirs, dbx_root, dbx_dirs)
            for dbox_folder in process_folders:
                download_sub, upload_sub = self.map_recursive(dbox_folder)
                download_files.extend(download_sub)
                upload_files.extend(upload_sub)
        else:
            self.logger.info('skipping subfolders because of configuration')
        return download_files, upload_files

    def __map_dropbox_files_to_local(self, local_root: str, local_files: list, dbx_root: str, dbx_files: list):
        upload_list = list()
        download_list = list()

        for dbx_file_md in dbx_files:
            name = dbx_file_md.name
            dbx_path = dbx_file_md.path_display
            local_path = self.fileStore.get_absolute_path(dbx_path)

            if name in local_files:
                self.logger.debug('file found locally - {}'.format(name))
                local_md = self.fileStore.get_metadata(local_path)
                if self.__are_equal_by_metadata(local_md, dbx_file_md):
                    self.logger.info('file {} already synced [by metadata]. Skip'.format(dbx_path))
                else:
                    self.logger.info('file {} exists with different stats. Downloading temporary'.format(dbx_path))
                    if self.__are_equal_by_content(local_path, dbx_path):
                        self.logger.info('file {} already synced [by content]. Skip'.format(dbx_path))
                    else:
                        if local_md.client_modified > dbx_file_md.client_modified:
                            self.logger.info('file {} has changed since last sync (dbx={} < local={}) => upload list'
                                .format(local_path, dbx_file_md.client_modified, local_md.client_modified))
                            upload_list.append(dbx_path)
                        else:
                            self.logger.info('file {} has changed since last sync (dbx={} > local={}) => download list'
                                .format(dbx_path, dbx_file_md.client_modified, local_md.client_modified))
                            download_list.append(dbx_path)
            else:
                self.logger.info('file NOT found locally - {} => download list'.format(dbx_path))
                download_list.append(dbx_path)

        dbx_names = list(map(lambda f: f.name, dbx_files))
        local_only = filter(lambda name: name not in dbx_names, local_files)
        for name in local_only:
            local_path = pathlib.PurePath(local_root).joinpath(name)
            self.logger.info('file NOT found on dropbox - {} => upload list'.format(local_path))
            dbx_path = urljoin(dbx_root, name)
            upload_list.append(dbx_path)

        return download_list, upload_list

    def __map_dropbox_folders_to_local(self, local_folders: list, dbx_root: str, dbx_folders: list):
        dbx_dict = dict(map(lambda f: (f.path_lower, f.path_display), dbx_folders))

        local_folder_paths = map(lambda name: urljoin(dbx_root, name), local_folders)
        local_folder_paths_filtered = filter(lambda name: not name.startswith('.'), local_folder_paths)
        local_dict = {v.lower(): v for v in local_folder_paths_filtered}

        union_keys = set(dbx_dict.keys()).union(local_dict.keys())
        union_list = list(map(lambda key: dbx_dict[key] if key in dbx_dict else local_dict[key], union_keys))
        return union_list

    def __are_equal_by_metadata(self, local_md: FileMetadata, dbox_file_md: dropbox.files.FileMetadata):
        equal_by_name = (local_md.name == dbox_file_md.name)
        equal_by_size = (local_md.size == dbox_file_md.size)
        equal_by_date = (local_md.client_modified == dbox_file_md.client_modified)
        if not equal_by_name:
            self.logger.info('files are not equal by name: local={}, remote={}'.format(local_md.name, dbox_file_md.name))
            return False
        if not equal_by_size:
            self.logger.info('file={} not equal by size: local={}, remote={}'.format(local_md.name, local_md.size, dbox_file_md.size))
            return False
        if not equal_by_date:
            self.logger.info('file={} not equal by date: local={}, remote={}'.format(local_md.name, local_md.client_modified, dbox_file_md.client_modified))
            return False
        return True

    def __are_equal_by_content(self, local_path: str, dbox_path: str):
        content_local, local_md = self.fileStore.read(local_path)
        response, dbox_md = self.dboxStore.read(dbox_path)
        return response.content == content_local

@contextlib.contextmanager
def stopwatch(message: str, logger: Logger):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logger.debug('Total elapsed time for {}: {:.3f}'.format(message, t1 - t0))
