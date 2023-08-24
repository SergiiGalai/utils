from logging import Logger

from src.stores.models import CloudFileMetadata, CloudFolderMetadata

class FileMapper:
   def __init__(self, logger: Logger):
      self._logger = logger

   def convert_GoogleDriveFile_to_CloudFileMetadata(self, gFile) -> CloudFileMetadata:
      #self.logger.debug('file: {}'.format(gFile))
      fileSize = None if gFile['mimeType'] == 'application/vnd.google-apps.shortcut' else gFile['fileSize']
      return CloudFileMetadata(gFile['id'], gFile['title'], gFile['title'], gFile['modifiedDate'], fileSize)

   def convert_GoogleDriveFile_to_CloudFolderMetadata(self, gFile) -> CloudFolderMetadata:
      #self.logger.debug('file: {}'.format(gFile))
      return CloudFolderMetadata(gFile['id'], gFile['title'], gFile['id'], gFile['title'])
