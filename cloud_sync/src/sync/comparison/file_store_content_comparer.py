from logging import Logger
from src.stores.cloud_store import CloudStore
from src.sync.comparison.file_content_comparer import FileContentComparer
from src.stores.local.file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, LocalFileMetadata


class FileStoreContentComparer(FileContentComparer):
    def __init__(self, local_store: LocalFileStore, cloud_store: CloudStore, logger: Logger):
        self._local_store = local_store
        self._cloud_store = cloud_store
        self._logger = logger

    def are_equal(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> bool:
        local_content, _ = self._local_store.read(local_md.cloud_path)
        cloud_content, _ = self._cloud_store.read(cloud_md.id)
        return cloud_content == local_content
