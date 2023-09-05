from logging import Logger
from src.services.file_comparer import FileComparer
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, LocalFileMetadata

class ContentFileComparer(FileComparer):
   def __init__(self, localStore: LocalFileStore, cloudStore: CloudStore, logger: Logger) -> None:
      self._localStore = localStore
      self._cloudStore = cloudStore
      self._logger = logger

   def _are_equal_by_content(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata):
      local_content, _ = self._localStore.read(local_md.cloud_path)
      cloud_content, _ = self._cloudStore.read(cloud_md.id)
      return cloud_content == local_content
