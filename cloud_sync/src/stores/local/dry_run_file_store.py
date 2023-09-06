import os
from datetime import datetime
from logging import Logger
from src.configs.config import StorageConfig
from src.stores.local.path_provider import PathProvider
from src.stores.local.file_store import LocalFileStore
from src.stores.models import CloudFileMetadata

class DryRunLocalFileStore(LocalFileStore):
   def __init__(self, config: StorageConfig, pathProvider: PathProvider, logger: Logger):
      super().__init__(pathProvider, logger)
      self._dry_run = config.dry_run
      self._logger = logger

   def save(self, content: bytes, cloud_md: CloudFileMetadata):
      if self._dry_run:
         file_path = self._get_absolute_path(cloud_md.cloud_path)
         self._logger.warn('dry run mode. Skip saving file {}'.format(file_path))
      else:
         super().save(content, cloud_md)

   def _try_create_local_folder(self, path: str):
      if self._dry_run:
         self._logger.warn('Dry Run mode. path {}'.format(path))
      else:
         super()._try_create_local_folder(path)

   def _set_modification_time(self, file_path: str, modified: datetime):
      if self._dry_run:
         self._logger.warn('Dry Run mode. file_path {}, modified={}'.format(os.path.basename(file_path), modified))
      else:
         super()._set_modification_time(file_path, modified)
