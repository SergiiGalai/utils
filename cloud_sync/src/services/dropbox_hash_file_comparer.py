import hashlib
from logging import Logger
from src.services.file_comparer import FileComparer
from src.stores.models import CloudFileMetadata, LocalFileMetadata

class DropboxHashFileComparer(FileComparer):
   _DROPBOX_HASH_CHUNK_SIZE = 4*1024*1024

   def __init__(self, logger: Logger):
      self._logger = logger

   def _are_equal_by_content(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata):
      local_hash = self._compute_dropbox_hash(local_md.local_path)
      cloud_hash = cloud_md.content_hash
      return local_hash == cloud_hash

   #implementation of https://www.dropbox.com/developers/reference/content-hash
   def _compute_dropbox_hash(self, filePath:str) -> str:
      with open(filePath, 'rb') as f:
         block_hashes = b''
         while True:
            chunk = f.read(self._DROPBOX_HASH_CHUNK_SIZE)
            if not chunk:
               break
            block_hashes += hashlib.sha256(chunk).digest()
         return hashlib.sha256(block_hashes).hexdigest()
