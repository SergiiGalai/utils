import pathlib
import dropbox
from posixpath import join as urljoin
from logging import Logger
from config import Config
from dropbox_store import DropboxStore
from file_store import FileStore, FileMetadata

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
