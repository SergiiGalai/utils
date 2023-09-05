import dropbox
from logging import Logger
from src.stores.models import CloudFileMetadata, CloudFolderMetadata

#dropbox files https://dropbox-sdk-python.readthedocs.io/en/latest/api/files.html
class DropboxFileMapper:
   def __init__(self, logger: Logger):
      self._logger = logger

   def convert_dropbox_entries_to_FileMetadatas(self, dropbox_entries:list) -> tuple[list[CloudFolderMetadata], list[CloudFileMetadata]]:
      dirs = list[CloudFolderMetadata]()
      files = list[CloudFileMetadata]()
      for entry in dropbox_entries:
         self._logger.debug("entry path_display=`{}`, name={}".format(entry.path_display, entry.name))
         if self.__isFile(entry):
            cloud_file: CloudFileMetadata = self.convert_DropboxFileMetadata_to_CloudFileMetadata(entry)
            files.append(cloud_file)
         else:
            cloud_dir: CloudFolderMetadata = self.convert_DropboxFolderMetadata_to_CloudFolderMetadata(entry)
            dirs.append(cloud_dir)
      return dirs, files

   def __isFile(self, entry):
      return isinstance(entry, dropbox.files.FileMetadata)

   #dropbox content hash: https://www.dropbox.com/developers/reference/content-hash
   def convert_DropboxFileMetadata_to_CloudFileMetadata(self, dbx_md: dropbox.files.FileMetadata) -> CloudFileMetadata:
      #self.logger.debug('file: {}'.format(dbx_md))
      return CloudFileMetadata(dbx_md.name, dbx_md.path_display, dbx_md.client_modified, dbx_md.size, dbx_md.path_lower, dbx_md.content_hash)

   def convert_DropboxFolderMetadata_to_CloudFolderMetadata(self, dbx_dir: dropbox.files.FolderMetadata) -> CloudFolderMetadata:
      #self.logger.debug('folder: {}'.format(dbx_dir))
      return CloudFolderMetadata(dbx_dir.path_lower, dbx_dir.name, dbx_dir.path_lower, dbx_dir.path_display)
