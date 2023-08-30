from logging import Logger
from src.configs.config import StorageConfig
from src.services.content_file_comparer import ContentFileComparer
from src.services.dropbox_hash_file_comparer import DropboxHashFileComparer
from src.services.file_comparer import FileComparer
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore

class FileComparerFactory:
   def __init__(self, localStore: LocalFileStore, cloudStore: CloudStore, logger: Logger):
      self._localStore = localStore
      self._cloudStore = cloudStore
      self._logger = logger

   def create(self, config: StorageConfig) -> FileComparer:
      match config.storage_name:
         case 'DROPBOX':
            self._logger.debug('creating DropboxFileComparer')
            return DropboxHashFileComparer(self._logger)
         case 'GDRIVE':
            self._logger.debug('creating ContentFileComparer')
            return ContentFileComparer(self._localStore, self._cloudStore, self._logger)
         case _:
            self._logger.error('No supported file comparer for the current storage configuration')
            raise NotImplementedError(f'Not supported value {config.storage_name}')
