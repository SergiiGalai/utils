import contextlib
import time
import dropbox
from logging import Logger
from src.configs.storage_config import StorageConfig
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.dropbox.dropbox_file_converter import DropboxFileConverter
from src.sync.stores.models import ListCloudFolderResult, LocalFileMetadata


# dropbox files https://dropbox-sdk-python.readthedocs.io/en/latest/api/files.html
class DropboxStore(CloudStore):
    def __init__(self, conf: StorageConfig, logger: Logger):
        self._config = conf
        self._logger = logger
        self._dbx = dropbox.Dropbox(conf.token)
        self._converter = DropboxFileConverter(logger)

    def list_folder(self, cloud_path: str) -> ListCloudFolderResult:
        self._logger.debug('list path: %s', cloud_path)
        try:
            with stopwatch('list_folder', self._logger):
                res = self._dbx.files_list_folder(cloud_path)
        except dropbox.exceptions.ApiError:  # type: ignore
            self._logger.warning('Folder listing failed for %s -- assumed empty', cloud_path)
        else:
            return self._converter.convert_dropbox_entries_to_cloud(res.entries)  # type: ignore
        return ListCloudFolderResult()

    def read_content(self, cloud_path: str) -> bytes:
        self._logger.debug('cloud_path=%s', cloud_path)
        with stopwatch('download', self._logger):
            try:
                _, response = self._dbx.files_download(cloud_path)  # type: ignore
                self._logger.debug('%d bytes; path: %s', len(response.content), cloud_path)
                return response.content
            except dropbox.exceptions.HttpError:  # type: ignore
                self._logger.exception("*** Dropbox HTTP Error")
                raise NotImplementedError

    def save(self, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
        cloud_path = local_md.cloud_path
        self._logger.debug('cloud_path=%s', cloud_path)
        write_mode = (dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add)  # type: ignore
        with stopwatch('upload %d bytes' % len(content), self._logger):
            if self._config.dry_run:
                self._logger.info('Dry run mode. Skip uploading %s (modified:%s) using %s',
                    cloud_path, local_md.client_modified, write_mode)
            else:
                try:
                    res = self._dbx.files_upload(content, cloud_path, write_mode,
                                                 client_modified=local_md.client_modified, mute=True)
                    self._logger.debug('Uploaded as %s', res.name)  # type: ignore
                except dropbox.exceptions.ApiError:  # type: ignore
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
