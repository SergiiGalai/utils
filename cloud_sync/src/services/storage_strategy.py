from abc import abstractmethod
from logging import Logger
from src.configs.config import StorageConfig
from src.stores.gdrive.content_file_comparer import ContentFileComparer
from src.stores.dropbox.dropbox_hash_file_comparer import DropboxHashFileComparer
from src.stores.file_comparer import FileComparer
from src.stores.cloud_store import CloudStore
from src.stores.dropbox.file_store import DropboxStore
from src.stores.gdrive.file_store_v2 import GdriveStore
from src.stores.local.file_store import LocalFileStore


class StorageStrategy:
    @abstractmethod
    def create_file_comparer(self) -> FileComparer: raise NotImplementedError

    @abstractmethod
    def create_cloud_store(self) -> CloudStore: raise NotImplementedError


class DropboxStorageStrategy(StorageStrategy):
    def __init__(self, config: StorageConfig, logger: Logger):
        self._config = config
        self._logger = logger

    def create_file_comparer(self) -> FileComparer:
        return DropboxHashFileComparer(self._logger)

    def create_cloud_store(self) -> CloudStore:
        return DropboxStore(self._config, self._logger)


class GdriveStorageStrategy(StorageStrategy):
    def __init__(self, config: StorageConfig, localStore: LocalFileStore, logger: Logger):
        self._config = config
        self._logger = logger
        self._localStore = localStore
        self._cloudStore = GdriveStore(config, logger)

    def create_file_comparer(self) -> FileComparer:
        return ContentFileComparer(self._localStore, self._cloudStore, self._logger)

    def create_cloud_store(self) -> CloudStore:
        return self._cloudStore


class StorageStrategyFactory:
    def __init__(self, localStore: LocalFileStore, logger: Logger):
        self._localStore = localStore
        self._logger = logger

    def create(self, config: StorageConfig) -> StorageStrategy:
        match config.storage_name:
            case 'DROPBOX':
                self._logger.debug('creating DropboxStorageStrategy')
                return DropboxStorageStrategy(config, self._logger)
            case 'GDRIVE':
                self._logger.debug('creating GdriveStorageStrategy')
                return GdriveStorageStrategy(config, self._localStore, self._logger)
            case _:
                self._logger.error('Not supported storage configuration')
                raise NotImplementedError(
                    f'Not supported value {config.storage_name}')
