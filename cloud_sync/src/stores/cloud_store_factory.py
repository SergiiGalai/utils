from src.configs.config import StorageConfig
from src.stores.dropbox_store import DropboxStore
from src.stores.gdrive_store import GdriveStore
from logging import Logger

class CloudStoreFactory:
   def __init__(self, logger: Logger):
      self._logger = logger

   def create(self, config: StorageConfig):
      match config.storage_name:
         case 'DROPBOX':
            self._logger.debug('creating DropboxStore')
            return DropboxStore(config, self._logger)
         case 'GDRIVE':
            self._logger.debug('creating GdriveStore')
            return GdriveStore(config, self._logger)
         case _:
            self._logger.error('Not supported storage name selected in configuration')
            raise NotImplementedError
