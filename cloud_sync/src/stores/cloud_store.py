from abc import abstractmethod
from typing import Protocol

from src.stores.local_file_store import LocalFileMetadata

class CloudStore(Protocol):
   @abstractmethod
   def list_folder(self, cloud_path): raise NotImplementedError

   @abstractmethod
   def read(self, id: str): raise NotImplementedError

   @abstractmethod
   def save(self, cloud_path: str, content, local_md: LocalFileMetadata, overwrite: bool): raise NotImplementedError


