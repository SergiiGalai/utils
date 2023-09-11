from enum import Enum

from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class FileSyncAction(Enum):
    DOWNLOAD = 1
    UPLOAD = 2
    SKIP = 3
    CONFLICT = 4


class FileComparison(Enum):
    ERROR = 1
    EQUAL = 2
    DIF_BY_NAME = 3
    DIF_BY_SIZE = 4
    DIF_BY_DATE = 5


class MapFolderResult:
    def __init__(self, download: list[CloudFileMetadata] = [], upload: list[LocalFileMetadata] = []):
        self.__download = list[CloudFileMetadata]() if download == [] else download
        self.__upload = list[LocalFileMetadata]() if upload == [] else upload

    @property
    def upload(self): return self.__upload

    @property
    def download(self): return self.__download

    def add_upload(self, file: LocalFileMetadata):
        self.__upload.append(file)

    def add_download(self, file: CloudFileMetadata):
        self.__download.append(file)

    def extend(self, source: "MapFolderResult"):
        self.__upload.extend(source.upload)
        self.__download.extend(source.download)