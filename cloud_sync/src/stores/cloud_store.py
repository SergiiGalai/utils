from abc import abstractmethod
from typing import Protocol

from src.stores.models import CloudFileMetadata, CloudFolderMetadata, LocalFileMetadata

class CloudStore(Protocol):
   @abstractmethod
   def list_folder(self, cloud_path: str) -> tuple[list[CloudFolderMetadata], list[CloudFileMetadata]]: raise NotImplementedError

   @abstractmethod
   def read(self, id: str) -> tuple[bytes, CloudFileMetadata]: raise NotImplementedError

   @abstractmethod
   def save(self, cloud_path: str, content: bytes, local_md: LocalFileMetadata, overwrite: bool): raise NotImplementedError
