import hashlib
from logging import Logger
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.local.local_file_store import LocalFileStore
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class FileContentComparer:
    def are_equal(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> bool:
        raise NotImplementedError


class FileStoreContentComparer(FileContentComparer):
    def __init__(self, local_store: LocalFileStore, cloud_store: CloudStore, logger: Logger):
        self._local_store = local_store
        self._cloud_store = cloud_store
        self._logger = logger

    def are_equal(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> bool:
        local_content = self._local_store.read_content(local_md.cloud_path)
        cloud_content = self._cloud_store.read_content(cloud_md.id)
        return cloud_content == local_content


class DropboxHashComparer(FileContentComparer):
    _DROPBOX_HASH_CHUNK_SIZE = 4*1024*1024

    def __init__(self, logger: Logger):
        self._logger = logger

    def are_equal(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> bool:
        local_hash = self._compute_dropbox_hash(local_md.full_path)
        cloud_hash = cloud_md.content_hash
        return local_hash == cloud_hash

    # implementation of https://www.dropbox.com/developers/reference/content-hash
    def _compute_dropbox_hash(self, filePath: str) -> str:
        with open(filePath, 'rb') as f:
            block_hashes = b''
            while True:
                chunk = f.read(self._DROPBOX_HASH_CHUNK_SIZE)
                if not chunk:
                    break
                block_hashes += hashlib.sha256(chunk).digest()
            return hashlib.sha256(block_hashes).hexdigest()
