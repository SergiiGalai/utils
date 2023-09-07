from abc import abstractmethod
from typing import Protocol

from src.sync.stores.models import CloudFileMetadata, ListCloudFolderResult, LocalFileMetadata


class CloudStore(Protocol):
    @abstractmethod
    def list_folder(self, cloud_path: str) -> ListCloudFolderResult:
        raise NotImplementedError

    @abstractmethod
    def read(self, id: str) -> tuple[bytes, CloudFileMetadata]:
        raise NotImplementedError

    @abstractmethod
    def save(self, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
        raise NotImplementedError
