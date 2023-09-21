from logging import Logger
import posixpath
import os
import unicodedata
from src.sync.stores.common.PathHelper import PathHelper
from src.sync.stores.local.mime_type_provider import MimeTypeProvider
from src.sync.stores.local.system_file_reader import SystemFileReader
from src.sync.stores.local.PathProvider import PathProvider
from src.sync.stores.models import LocalFileMetadata, LocalFolderMetadata


class FileMetadataProvider:

    def __init__(self, path_provider: PathProvider, file_reader: SystemFileReader, logger: Logger):
        self._path_provider = path_provider
        self._logger = logger
        self._file_reader = file_reader
        self._mime_provider = MimeTypeProvider(logger)

    def get_files(self, parent_cloud_path: str, file_names: list[str]) -> list[LocalFileMetadata]:
        cloud_paths = list(self.__name_to_cloud_path(f, parent_cloud_path) for f in file_names)
        result = list(self.get_file(path) for path in cloud_paths)
        self._logger.debug('result={}'.format(result))
        return result

    def get_file(self, file_cloud_path: str) -> LocalFileMetadata:
        local_path = self._path_provider.get_absolute_path(file_cloud_path)
        size = self._file_reader.get_size(local_path)
        client_modified = self._file_reader.get_modified_time(local_path)
        file_name = PathHelper.get_file_name(local_path)
        file_extension = PathHelper.get_file_extension(local_path)
        mime_type = self._mime_provider.get_by_extension(file_extension)
        return LocalFileMetadata(file_name, file_cloud_path, client_modified, size, local_path, mime_type)

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
