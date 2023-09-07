import posixpath
from logging import Logger
from src.configs.config import StorageConfig
from src.sync.file_sync_action_provider import FileSyncAction, FileSyncActionProvider
from src.sync.models import MapFolderResult
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.local.file_store import LocalFileStore
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult, ListLocalFolderResult, LocalFileMetadata


class FolderMapper:
    def __init__(self,
                 local_store: LocalFileStore,
                 cloud_store: CloudStore,
                 file_sync_action_provider: FileSyncActionProvider,
                 config: StorageConfig,
                 logger: Logger):
        self._recursive = config.recursive
        self._logger = logger
        self._local_store = local_store
        self._cloud_store = cloud_store
        self._file_sync_action_provider = file_sync_action_provider

    def map_folder(self, cloud_path: str) -> MapFolderResult:
        self._logger.info('cloud_path={}'.format(cloud_path))
        local_result, cloud_result = self.__list_store_folder(cloud_path)
        result = self.__map_cloud_files_to_local(local_result.files, cloud_result.files)
        if self._recursive:
            sub_folders = self.__map_cloud_folders_to_local(local_result.folders, cloud_path, cloud_result.folders)
            for sub_folder in sub_folders:
                sub_folder_result = self.map_folder(sub_folder)
                result.extend(sub_folder_result)
        else:
            self._logger.info('skipping subfolders because of configuration')
        return result

    def __list_store_folder(self, cloud_path: str) -> tuple[ListLocalFolderResult, ListCloudFolderResult]:
        local_result = self._local_store.list_folder(cloud_path)
        cloud_result = self._cloud_store.list_folder(cloud_path)
        return local_result, cloud_result

    def __map_cloud_files_to_local(self,
                                   local_list: list[LocalFileMetadata],
                                   cloud_list: list[CloudFileMetadata]) -> MapFolderResult:
        result = MapFolderResult()
        local_dict = self.__to_local_dict(local_list)
        cloud_dict = self.__to_cloud_dict(cloud_list)
        for key, cloud_file in cloud_dict.items():
            local_file = local_dict.get(key)
            if local_file is None:
                self.__add_to_download(cloud_file, result)
            else:
                self.__add_by_comparison(local_file, cloud_file, result)
        for key, local_file in local_dict.items():
            if key not in cloud_dict:
                self.__add_to_upload(local_file, result)
        return result

    def __to_local_dict(self, files: list[LocalFileMetadata]) -> dict[str, LocalFileMetadata]:
        return {md.cloud_path.lower(): md for md in files}

    def __to_cloud_dict(self, files: list[CloudFileMetadata]) -> dict[str, CloudFileMetadata]:
        return {md.cloud_path.lower(): md for md in files}

    def __add_to_download(self, cloud_md: CloudFileMetadata, result: MapFolderResult):
        self._logger.info('file does NOT exist locally - {} => download list'.format(cloud_md.cloud_path))
        result.add_download(cloud_md)

    def __add_to_upload(self, local_md: LocalFileMetadata, result: MapFolderResult):
        self._logger.info('file does NOT exist in the cloud - {} => upload list'.format(local_md.local_path))
        result.add_upload(local_md)

    def __add_by_comparison(self,
                            local_md: LocalFileMetadata,
                            cloud_md: CloudFileMetadata,
                            result: MapFolderResult):
        self._logger.debug('file exists locally - {}'.format(local_md.cloud_path))
        file_action = self._file_sync_action_provider.get_sync_action(local_md, cloud_md)
        match file_action:
            case FileSyncAction.UPLOAD:
                result.add_upload(local_md)
            case FileSyncAction.DOWNLOAD:
                result.add_download(cloud_md)

    def __map_cloud_folders_to_local(self,
                                     local_folders: list[str],
                                     cloud_root: str,
                                     cloud_folders: list[CloudFolderMetadata]) -> list[str]:
        local_dict = self.__to_local_folder_dict(cloud_root, local_folders)
        cloud_dict = self.__to_cloud_folder_dict(cloud_folders)
        return self.__union_folders(cloud_dict, local_dict)

    def __to_local_folder_dict(self, cloud_root: str, folders: list[str]) -> dict[str, str]:
        folder_paths = list(posixpath.join(cloud_root, folder) for folder in folders)
        folder_paths_filtered = filter(lambda name: not name.startswith('.'), folder_paths)
        return {path.lower(): path for path in folder_paths_filtered}

    def __to_cloud_folder_dict(self, folders: list[CloudFolderMetadata]) -> dict[str, str]:
        return {folder.path_lower: folder.cloud_path for folder in folders}

    def __union_folders(self, cloud: dict[str, str], local: dict[str, str]) -> list[str]:
        union_keys = set(cloud.keys()).union(local.keys())
        union_list = list(map(lambda key: cloud[key] if key in cloud else local[key], union_keys))
        return union_list
