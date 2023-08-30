import datetime
from pydrive.drive import GoogleDriveFile
from logging import Logger

from src.stores.models import CloudFileMetadata, CloudFolderMetadata

# ? https://developers.google.com/drive/api/reference/rest/v3/files
class GoogleDriveFileMapper:
   def __init__(self, logger: Logger):
      self._logger = logger

   def convert_GoogleDriveFile_to_CloudFileMetadata(self, gFile: GoogleDriveFile) -> CloudFileMetadata:
      #self.logger.debug('file: {}'.format(gFile))
      fileSize = 0 if gFile['mimeType'] == 'application/vnd.google-apps.shortcut' else int(gFile['fileSize'])
      modified = datetime.datetime.strptime(gFile['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
      return CloudFileMetadata(gFile['id'], gFile['title'], gFile['title'], modified, fileSize, '0')

   def convert_GoogleDriveFile_to_CloudFolderMetadata(self, gFile: GoogleDriveFile) -> CloudFolderMetadata:
      #self.logger.debug('file: {}'.format(gFile))
      return CloudFolderMetadata(gFile['id'], gFile['title'], gFile['id'], gFile['title'])
