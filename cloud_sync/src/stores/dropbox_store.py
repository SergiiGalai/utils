import contextlib
import time
import dropbox
from logging import Logger
from src.configs.config import Config
from src.stores.local_file_store import LocalFileMetadata

class DropboxStore:
    def __init__(self, conf: Config, logger: Logger):
        self.dbx = dropbox.Dropbox(conf.token)
        self.dry_run = conf.dry_run
        self.logger = logger

    def list_folder(self, cloud_path):
        self.logger.debug('list path: {}'.format(cloud_path))
        dbx_dirs = list()
        dbx_files = list()
        try:
            with stopwatch('list_folder', self.logger):
                res = self.dbx.files_list_folder(cloud_path)
        except dropbox.exceptions.ApiError:
            self.logger.warning('Folder listing failed for {} -- assumed empty'.format(cloud_path))
        else:
            for entry in res.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    dbx_files.append(entry)
                else:
                    dbx_dirs.append(entry)
        self.logger.debug('files={}'.format(dbx_files))
        return cloud_path, dbx_dirs, dbx_files

    def read(self, cloud_path):
        self.logger.debug('cloud_path={}'.format(cloud_path))
        with stopwatch('download', self.logger):
            try:
                meta_data, response = self.dbx.files_download(cloud_path)
            except dropbox.exceptions.HttpError:
                self.logger.exception("*** Dropbox HTTP Error")
                return None
        self.logger.debug('{} bytes; md: {}'.format(len(response.content), meta_data.name))
        return response, meta_data

    def save(self, cloud_path: str, content, metadata: LocalFileMetadata, overwrite: bool):
        self.logger.debug('cloud_path={}'.format(cloud_path))
        write_mode = (dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add)
        with stopwatch('upload %d bytes' % len(content), self.logger):
            if self.dry_run:
                self.logger.info('Dry run mode. Skip uploading {} (modified:{}) using {}'
                    .format(cloud_path, metadata.client_modified, write_mode))
            else:
                try:
                    res = self.dbx.files_upload(content, cloud_path, write_mode, client_modified=metadata.client_modified, mute=True)
                    self.logger.debug('Uploaded as {}'.format(res.name))
                    return res
                except dropbox.exceptions.ApiError:
                    self.logger.exception('*** API error')
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
