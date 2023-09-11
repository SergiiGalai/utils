from abc import abstractmethod
from logging import Logger
from src.configs.config import StorageConfig
from src.sync.comparison.file_content_comparer import FileContentComparer
from src.sync.comparison.file_store_content_comparer import FileStoreContentComparer
from src.sync.comparison.dropbox_hash_file_comparer import DropboxHashFileComparer
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.dropbox.file_store import DropboxStore
from src.sync.stores.gdrive.file_store_v2 import GdriveStore
from src.sync.stores.gdrive.subfolder_file_store import GdriveSubfolderFileStore
from src.sync.stores.local.file_store import LocalFileStore


class StorageStrategy:
    @abstractmethod
    def create_file_content_comparer(self) -> FileContentComparer:
        raise NotImplementedError

    @abstractmethod
    def create_cloud_store(self) -> CloudStore:
        raise NotImplementedError


class DropboxStorageStrategy(StorageStrategy):
    def __init__(self, config: StorageConfig, logger: Logger):
        self._config = config
        self._logger = logger

    def create_file_content_comparer(self) -> FileContentComparer:
        return DropboxHashFileComparer(self._logger)

    def create_cloud_store(self) -> CloudStore:
        return DropboxStore(self._config, self._logger)


class GdriveStorageStrategy(StorageStrategy):
    def __init__(self, config: StorageConfig, localStore: LocalFileStore, logger: Logger):
        self._config = config
        self._logger = logger
        self._localStore = localStore
        store = GdriveStore(config, logger)
        self._cloudStore = GdriveSubfolderFileStore(store, logger)

    def create_file_content_comparer(self) -> FileContentComparer:
        return FileStoreContentComparer(self._localStore, self._cloudStore, self._logger)

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
                raise NotImplementedError(f'Not supported value {config.storage_name}')