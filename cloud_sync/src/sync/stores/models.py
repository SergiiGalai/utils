from dataclasses import dataclass
from datetime import datetime


@dataclass
class CloudFolderMetadata:
    id: str
    name: str
    path_lower: str
    cloud_path: str


@dataclass
class FileMetadata:
    name: str
    cloud_path: str
    client_modified: datetime
    size: int


@dataclass
class CloudFileMetadata(FileMetadata):
    id: str
    content_hash: str


@dataclass
class LocalFileMetadata(FileMetadata):
    local_path: str


class ListCloudFolderResult:
    def __init__(self, files: list[CloudFileMetadata] = [], folders: list[CloudFolderMetadata] = []):
        self.files = list[CloudFileMetadata]() if files == [] else files
        self.folders = list[CloudFolderMetadata]() if folders == [] else folders


class ListLocalFolderResult:
    def __init__(self, files: list[LocalFileMetadata] = [], folders: list[str] = []):
        self.files = list[LocalFileMetadata]() if files == [] else files
        self.folders = list[str]() if folders == [] else folders
