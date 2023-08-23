import contextlib
import time
import dropbox
from logging import Logger
from src.configs.config import StorageConfig
from src.stores.cloud_store import CloudStore
from src.stores.models import CloudFileMetadata, CloudFolderMetadata
from src.stores.local_file_store import LocalFileMetadata

class DropboxStore(CloudStore):
    def __init__(self, conf: StorageConfig, logger: Logger):
        self._dbx = dropbox.Dropbox(conf.token)
        self._dry_run = conf.dry_run
        self._logger = logger

    def list_folder(self, cloud_path):
        self._logger.debug('list path: {}'.format(cloud_path))
        cloud_dirs = list()
        cloud_files = list()
        try:
            with stopwatch('list_folder', self._logger):
                res = self._dbx.files_list_folder(cloud_path)
        except dropbox.exceptions.ApiError:
            self._logger.warning('Folder listing failed for {} -- assumed empty'.format(cloud_path))
        else:
            for entry in res.entries:
                self._logger.debug("entry path_display=`{}`".format(entry.path_display))
                if self.__isFile(entry):
                    cloud_files.append(self.__to_CloudFileMetadata(entry))
                else:
                    cloud_dirs.append(self.__to_CloudFolderMetadata(entry))
        return cloud_path, cloud_dirs, cloud_files

    def __isFile(self, entry):
        return isinstance(entry, dropbox.files.FileMetadata)

    def __to_CloudFileMetadata(self, dbx_md: dropbox.files.FileMetadata)-> CloudFileMetadata:
        #self.logger.debug('file: {}'.format(dbx_md))
        return CloudFileMetadata(dbx_md.name, dbx_md.path_display, dbx_md.client_modified, dbx_md.size)

    def __to_CloudFolderMetadata(self, dbx_dir)-> CloudFolderMetadata:
        #self.logger.debug('folder: {}'.format(dbx_dir))
        return CloudFolderMetadata(dbx_dir.path_lower, dbx_dir.path_display)
    
    def read(self, cloud_path: str):
        self._logger.debug('cloud_path={}'.format(cloud_path))
        with stopwatch('download', self._logger):
            try:
                dbx_md, response = self._dbx.files_download(cloud_path)
                cloud_file_md = self.__to_CloudFileMetadata(dbx_md)
                self._logger.debug('{} bytes; md: {}'.format(len(response.content), cloud_file_md.name))
                return response, cloud_file_md
            except dropbox.exceptions.HttpError:
                self._logger.exception("*** Dropbox HTTP Error")
                return None

    def save(self, cloud_path: str, content, local_md: LocalFileMetadata, overwrite: bool):
        self._logger.debug('cloud_path={}'.format(cloud_path))
        write_mode = (dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add)
        with stopwatch('upload %d bytes' % len(content), self._logger):
            if self._dry_run:
                self._logger.info('Dry run mode. Skip uploading {} (modified:{}) using {}'
                    .format(cloud_path, local_md.client_modified, write_mode))
            else:
                try:
                    res = self._dbx.files_upload(content, cloud_path, write_mode, client_modified=local_md.client_modified, mute=True)
                    self._logger.debug('Uploaded as {}'.format(res.name))
                    return res
                except dropbox.exceptions.ApiError:
                    self._logger.exception('*** API error')
                    return None

@contextlib.contextmanager
def stopwatch(message: str, logger: Logger):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logger.debug('Total elapsed time for {}: {:.3f}'.format(message, t1 - t0))
