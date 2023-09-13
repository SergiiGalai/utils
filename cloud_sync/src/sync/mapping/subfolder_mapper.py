from logging import Logger
from src.sync.stores.models import CloudFolderMetadata, LocalFolderMetadata


class SubfolderMapper:
    def __init__(self, logger: Logger):
        self._logger = logger

    def map_cloud_to_local(self,
                           cloud_folders: list[CloudFolderMetadata],
                           local_folders: list[LocalFolderMetadata]) -> set[str]:
        local_dict = self.__to_local_folder_dict(local_folders)
        cloud_dict = self.__to_cloud_folder_dict(cloud_folders)
        return self.__union_folders(cloud_dict, local_dict)

    def __to_local_folder_dict(self, folders: list[LocalFolderMetadata]) -> dict[str, str]:
        return {folder.cloud_path.lower(): folder.cloud_path for folder in folders}

    def __to_cloud_folder_dict(self, folders: list[CloudFolderMetadata]) -> dict[str, str]:
        return {folder.path_lower: folder.cloud_path for folder in folders}

    def __union_folders(self, cloud: dict[str, str], local: dict[str, str]) -> set[str]:
        union_keys = set(cloud.keys()).union(local.keys())
        union_list = set(map(lambda key: cloud[key] if key in cloud else local[key], union_keys))
        return union_list
