from abc import abstractmethod
from typing import Protocol

from src.stores.local_file_store import LocalFileMetadata
from src.stores.models import CloudFileMetadata, CloudFolderMetadata

class CloudStore(Protocol):
   @abstractmethod
   def list_folder(self, cloud_path: str) -> tuple[str, list[CloudFolderMetadata], list[CloudFileMetadata]]: raise NotImplementedError

   @abstractmethod
   def read(self, id: str) -> tuple[object, CloudFileMetadata]: raise NotImplementedError

   @abstractmethod
   def save(self, cloud_path: str, content, local_md: LocalFileMetadata, overwrite: bool) -> object: raise NotImplementedError


