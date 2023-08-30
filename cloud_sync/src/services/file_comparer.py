from abc import abstractmethod
from logging import Logger
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, LocalFileMetadata

class FileComparer:
   def __init__(self, localStore: LocalFileStore, cloudStore: CloudStore, logger: Logger):
      self._localStore = localStore
      self._cloudStore = cloudStore
      self._logger = logger

   def are_equal(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata):
      cloud_path = cloud_md.cloud_path
      if self._are_equal_by_metadata(local_md, cloud_md):
         self._logger.info('file {} already the same [by metadata]. Skip'.format(cloud_path))
         return True

      self._logger.info('file {} exists with different stats. Comparing files by content'.format(cloud_path))
      if self._are_equal_by_content(local_md, cloud_md):
         self._logger.info('file {} already the same [by content]. Skip'.format(cloud_path))
         return True

      self._logger.info('Local and cloud file {} is different'.format(cloud_path))
      return False

   def _are_equal_by_metadata(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata):
      equal_by_name = (local_md.name == cloud_md.name)
      equal_by_size = (local_md.size == cloud_md.size)
      equal_by_date = (local_md.client_modified == cloud_md.client_modified)
      if not equal_by_name:
         self._logger.info('file diff by name: local={}, remote={}'.format(local_md.name, cloud_md.name))
         return False
      if not equal_by_size:
         self._logger.info('file={} diff by size: local={}, remote={}'.format(local_md.name, local_md.size, cloud_md.size))
         return False
      if not equal_by_date:
         self._logger.info('file={} diff by date: local={}, remote={}'.format(local_md.name, local_md.client_modified, cloud_md.client_modified))
         return False
      return True

   @abstractmethod
   def _are_equal_by_content(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata): raise NotImplementedError
