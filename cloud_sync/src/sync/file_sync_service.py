from logging import Logger
from src.configs.config import StorageConfig
from src.sync.mapping.recursive_folder_mapper import RecursiveFolderMapper
from src.sync.models import MapFolderResult
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.local.file_store import LocalFileStore
from src.sync.stores.local.path_provider import PathProvider
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class FileSyncronizationService:
    def __init__(self,
                 local_store: LocalFileStore,
                 cloud_store: CloudStore,
                 folder_mapper: RecursiveFolderMapper,
                 path_provider: PathProvider,
                 config: StorageConfig,
                 logger: Logger):
        self._logger = logger
        self._path_provider = path_provider
        self._local_store = local_store
        self._cloud_store = cloud_store
        self._folder_mapper = folder_mapper
        self._logger.debug(config)

    @property
    def local_root(self) -> str:
        return self._path_provider.get_absolute_path()

    def map_folder(self, cloud_path: str) -> MapFolderResult:
        self._logger.info('cloud_path={}'.format(cloud_path))
        return self._folder_mapper.map_folder(cloud_path)

    def download_files(self, cloud_files: list[CloudFileMetadata]):
        for cloud_file in cloud_files:
            cloud_path = cloud_file.cloud_path
            self._logger.info('downloading {} => {} ...'.format(
                cloud_path, self._path_provider.get_absolute_path(cloud_path)))
            content, cloud_md = self._cloud_store.read(cloud_file.id)
            self._logger.debug('downloaded file: {}'.format(cloud_md))
            self._local_store.save(content, cloud_md)

    def upload_files(self, local_files: list[LocalFileMetadata]):
        for local_file in local_files:
            cloud_path = local_file.cloud_path
            self._logger.info('uploading {} => {} ...'.format(local_file.local_path, cloud_path))
            content, local_md = self._local_store.read(cloud_path)
            self._cloud_store.save(content, local_md, overwrite=True)