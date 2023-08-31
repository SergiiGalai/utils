from abc import abstractmethod
from logging import Logger
from enum import Enum
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, LocalFileMetadata

class FileComparison(Enum):
   EQUAL_BY_METADATA = 1
   EQUAL_BY_CONTENT = 2
   DIF_BY_NAME = 3
   DIF_BY_SIZE = 4
   DIF_BY_DATE = 5

class FileComparer:
   def __init__(self, localStore: LocalFileStore, cloudStore: CloudStore, logger: Logger):
      self._localStore = localStore
      self._cloudStore = cloudStore
      self._logger = logger

   def are_equal(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> FileComparison:
      cloud_path = cloud_md.cloud_path
      comparison_by_md = self._are_equal_by_metadata(local_md, cloud_md)
      match comparison_by_md:
         case FileComparison.EQUAL_BY_METADATA:
            self._logger.info('file {} already the same [by metadata]. Skip'.format(cloud_path))
         case FileComparison.DIF_BY_DATE:
            self._logger.info('file {} exists with different stats. Comparing files by content'.format(cloud_path))
            if self._are_equal_by_content(local_md, cloud_md):
               self._logger.info('file {} already the same [by content]. Skip'.format(cloud_path))
               return FileComparison.EQUAL_BY_CONTENT
            self._logger.info('Local and cloud file {} is different'.format(cloud_path))
         case _:
            self._logger.info('Local and cloud file {} is different'.format(cloud_path))
      return comparison_by_md

   def _are_equal_by_metadata(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> FileComparison:
      if local_md.name != cloud_md.name:
         self._logger.info('file diff by name: local={}, remote={}'.format(local_md.name, cloud_md.name))
         return FileComparison.DIF_BY_NAME
      if local_md.size != cloud_md.size:
         self._logger.info('file={} diff by size: local={}, remote={}'.format(local_md.name, local_md.size, cloud_md.size))
         return FileComparison.DIF_BY_SIZE
      if local_md.client_modified != cloud_md.client_modified:
         self._logger.info('file={} diff by date: local={}, remote={}'.format(local_md.name, local_md.client_modified, cloud_md.client_modified))
         return FileComparison.DIF_BY_DATE
      return FileComparison.EQUAL_BY_METADATA

   @abstractmethod
   def _are_equal_by_content(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata): raise NotImplementedError
