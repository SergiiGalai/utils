from logging import Logger
from src.configs.storage_config import StorageConfig
from src.sync.mapping.file_mapper import FileMapper
from src.sync.mapping.subfolder_mapper import SubfolderMapper
from src.sync.models import MapFolderResult
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.local.local_file_store import LocalFileStore
from src.sync.stores.models import ListCloudFolderResult, ListLocalFolderResult


class RecursiveFolderMapper:
    def __init__(self,
                 local_store: LocalFileStore,
                 cloud_store: CloudStore,
                 file_mapper: FileMapper,
                 subfolder_mapper: SubfolderMapper,
                 config: StorageConfig,
                 logger: Logger):
        self._config = config
        self._logger = logger
        self._local_store = local_store
        self._cloud_store = cloud_store
        self._file_mapper = file_mapper
        self._subfolder_mapper = subfolder_mapper

    def map_folder(self, cloud_path: str) -> MapFolderResult:
        self._logger.info('cloud_path={}'.format(cloud_path))
        local_folder, cloud_folder = self.__list_store_folder(cloud_path)
        result = self._file_mapper.map_cloud_to_local(cloud_folder.files, local_folder.files)
        if self._config.recursive:
            if self.__are_folders_present(cloud_folder, local_folder):
                sub_folders = self._subfolder_mapper.map_cloud_to_local(cloud_folder.folders, local_folder.folders)
                self.__map_subfolders(sub_folders, result)
            else:
                self._logger.debug('skipping. no subfolders')
        else:
            self._logger.info('skipping subfolders because of configuration')
        return result

    def __list_store_folder(self, cloud_path: str) -> tuple[ListLocalFolderResult, ListCloudFolderResult]:
        local_result = self._local_store.list_folder(cloud_path)
        cloud_result = self._cloud_store.list_folder(cloud_path)
        return local_result, cloud_result

    def __are_folders_present(self, cloud: ListCloudFolderResult, local: ListLocalFolderResult):
        return cloud.folders != [] or local.folders != []

    def __map_subfolders(self, sub_folders: set[str], result: MapFolderResult):
        for sub_folder in sub_folders:
            sub_folder_result = self.map_folder(sub_folder)
            result.extend(sub_folder_result)
