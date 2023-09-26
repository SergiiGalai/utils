from abc import abstractmethod
from typing import Protocol

from src.sync.stores.models import ListCloudFolderResult, LocalFileMetadata


class CloudStore(Protocol):
    @abstractmethod
    def list_folder(self, cloud_path: str) -> ListCloudFolderResult:
        raise NotImplementedError

    @abstractmethod
    def read_content(self, id: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def save(self, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
        raise NotImplementedError
