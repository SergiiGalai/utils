from logging import Logger
import posixpath
import time
import os
from datetime import datetime
import unicodedata
from src.sync.stores.common.path_helper import PathHelper
from src.sync.stores.local.path_provider import PathProvider
from src.sync.stores.models import LocalFileMetadata, LocalFolderMetadata


class SystemFileProvider:

    def __init__(self, path_provider: PathProvider, logger: Logger):
        self._path_provider = path_provider
        self._logger = logger

    def get_files(self, parent_cloud_path: str, file_names: list[str]) -> list[LocalFileMetadata]:
        cloud_paths = list(self.__name_to_cloud_path(f, parent_cloud_path) for f in file_names)
        result = list(self.get_file(path) for path in cloud_paths)
        self._logger.debug('result={}'.format(result))
        return result

    def get_file(self, file_cloud_path: str) -> LocalFileMetadata:
        local_path = self._path_provider.get_absolute_path(file_cloud_path)
        name = os.path.basename(local_path)
        size = os.path.getsize(local_path)
        modified_time = os.path.getmtime(local_path)
        client_modified = datetime(*time.gmtime(modified_time)[:6])
        return LocalFileMetadata(name, file_cloud_path, client_modified, size, local_path)

    def __name_to_cloud_path(self, name: str, parent_cloud_path: str) -> str:
        normalized_name = unicodedata.normalize('NFC', name)
        return PathHelper.start_with_slash(self.__join_path(parent_cloud_path, normalized_name))

    def __join_path(self, path1: str, path2: str) -> str:
        relative_path = PathHelper.strip_starting_slash(path2)
        result = posixpath.join(path1, relative_path)
        self._logger.debug('result={}'.format(result))
        return result

    def get_folders(self, parent_cloud_path: str, folder_names: list[str]) -> list[LocalFolderMetadata]:
        cloud_paths = list(self.__name_to_cloud_path(f, parent_cloud_path) for f in folder_names)
        result = list(self.__get_folder(path) for path in cloud_paths)
        self._logger.debug('result={}'.format(result))
        return result

    def __get_folder(self, cloud_path: str) -> LocalFolderMetadata:
        local_path = self._path_provider.get_absolute_path(cloud_path)
        name = os.path.basename(local_path)
        return LocalFolderMetadata(name, cloud_path, local_path)
