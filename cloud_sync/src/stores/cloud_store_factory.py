from src.configs.config import StorageConfig
from src.stores.dropbox_store import DropboxStore
from src.stores.gdrive_store import GdriveStore
from logging import Logger

class CloudStoreFactory:
   def __init__(self, logger: Logger):
      self.logger = logger

   def create(self, config: StorageConfig):
      match config.storage_name:
         case 'DROPBOX':
            self.logger.debug('creating DropboxStore')
            return DropboxStore(config, self.logger)
         case 'GDRIVE':
            self.logger.debug('creating GdriveStore')
            return GdriveStore(config, self.logger)
         case _:
            self.logger.error('Not supported storage name selected in configuration')
            raise NotImplementedError
