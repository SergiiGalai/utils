import posixpath
from logging import Logger
from src.sync.stores.models import CloudFolderMetadata


class SubfolderMapper:
    def __init__(self, logger: Logger):
        self._logger = logger

    def map_cloud_to_local(self,
                           cloud_root: str,
                           cloud_folders: list[CloudFolderMetadata],
                           local_folders: list[str]) -> set[str]:
        local_dict = self.__to_local_folder_dict(cloud_root, local_folders)
        cloud_dict = self.__to_cloud_folder_dict(cloud_folders)
        return self.__union_folders(cloud_dict, local_dict)

    def __to_local_folder_dict(self, cloud_root: str, folders: list[str]) -> dict[str, str]:
        folder_paths = list(posixpath.join(cloud_root, folder) for folder in folders)
        folder_paths_filtered = filter(lambda name: not name.startswith('.'), folder_paths)
        return {path.lower(): path for path in folder_paths_filtered}

    def __to_cloud_folder_dict(self, folders: list[CloudFolderMetadata]) -> dict[str, str]:
        return {folder.path_lower: folder.cloud_path for folder in folders}

    def __union_folders(self, cloud: dict[str, str], local: dict[str, str]) -> set[str]:
        union_keys = set(cloud.keys()).union(local.keys())
        union_list = set(map(lambda key: cloud[key] if key in cloud else local[key], union_keys))
        return union_list
