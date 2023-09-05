import contextlib
import time
import dropbox
from logging import Logger
from src.configs.config import StorageConfig
from src.stores.cloud_store import CloudStore
from src.stores.dropbox_file_mapper import DropboxFileMapper
from src.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult, LocalFileMetadata

#dropbox files https://dropbox-sdk-python.readthedocs.io/en/latest/api/files.html
class DropboxStore(CloudStore):
    def __init__(self, conf: StorageConfig, logger: Logger):
        self._dbx = dropbox.Dropbox(conf.token)
        self._dry_run = conf.dry_run
        self._logger = logger
        self._mapper = DropboxFileMapper(logger)

    def list_folder(self, cloud_path: str) -> ListCloudFolderResult:
        self._logger.debug('list path: {}'.format(cloud_path))
        try:
            with stopwatch('list_folder', self._logger):
                res = self._dbx.files_list_folder(cloud_path)
        except dropbox.exceptions.ApiError:
            self._logger.warning('Folder listing failed for {} -- assumed empty'.format(cloud_path))
        else:
            return self._mapper.convert_dropbox_entries_to_FileMetadatas(res.entries)
        return [], []

    def read(self, cloud_path: str) -> tuple[bytes, CloudFileMetadata]:
        self._logger.debug('cloud_path={}'.format(cloud_path))
        with stopwatch('download', self._logger):
            try:
                dbx_md, response = self._dbx.files_download(cloud_path)
                cloud_file_md = self._mapper.convert_DropboxFileMetadata_to_CloudFileMetadata(dbx_md)
                self._logger.debug('{} bytes; md: {}'.format(len(response.content), cloud_file_md.name))
                return response.content, cloud_file_md
            except dropbox.exceptions.HttpError:
                self._logger.exception("*** Dropbox HTTP Error")
                return None, None

    def save(self, cloud_path: str, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
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
                except dropbox.exceptions.ApiError:
                    self._logger.exception('*** API error')

@contextlib.contextmanager
def stopwatch(message: str, logger: Logger):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logger.debug('Total elapsed time for {}: {:.3f}'.format(message, t1 - t0))
