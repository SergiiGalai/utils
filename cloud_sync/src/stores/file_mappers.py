import dropbox
import datetime
from pydrive.drive import GoogleDriveFile
from logging import Logger

from src.stores.models import CloudFileMetadata, CloudFolderMetadata

class GoogleDriveFileMapper:
   def __init__(self, logger: Logger):
      self._logger = logger

   def convert_GoogleDriveFile_to_CloudFileMetadata(self, gFile: GoogleDriveFile) -> CloudFileMetadata:
      #self.logger.debug('file: {}'.format(gFile))
      fileSize = 0 if gFile['mimeType'] == 'application/vnd.google-apps.shortcut' else int(gFile['fileSize'])
      modified = datetime.datetime.strptime(gFile['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
      return CloudFileMetadata(gFile['id'], gFile['title'], gFile['title'], modified, fileSize)

   def convert_GoogleDriveFile_to_CloudFolderMetadata(self, gFile: GoogleDriveFile) -> CloudFolderMetadata:
      #self.logger.debug('file: {}'.format(gFile))
      return CloudFolderMetadata(gFile['id'], gFile['title'], gFile['id'], gFile['title'])

class DropboxFileMapper:
   def __init__(self, logger: Logger):
      self._logger = logger

   def convert_DropboxFileMetadata_to_CloudFileMetadata(self, dbx_md: dropbox.files.FileMetadata) -> CloudFileMetadata:
      #self.logger.debug('file: {}'.format(dbx_md))
      return CloudFileMetadata(dbx_md.path_display, dbx_md.name, dbx_md.path_display, dbx_md.client_modified, dbx_md.size)

   def convert_DropboxFolderMetadata_to_CloudFolderMetadata(self, dbx_dir: dropbox.files.FolderMetadata) -> CloudFolderMetadata:
      #self.logger.debug('folder: {}'.format(dbx_dir))
      return CloudFolderMetadata(dbx_dir.path_display, dbx_dir.name, dbx_dir.path_lower, dbx_dir.path_display)
