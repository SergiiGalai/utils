import datetime
import posixpath
from pydrive.drive import GoogleDriveFile
from logging import Logger

from src.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult

# ? https://developers.google.com/drive/api/reference/rest/v3/files
class GoogleDriveFileMapper:
   def __init__(self, logger: Logger):
      self._logger = logger

   def convert_GoogleDriveFiles_to_FileMetadatas(self, gFiles: list[GoogleDriveFile], folder_cloud_path:str = '') -> ListCloudFolderResult:
      result = ListCloudFolderResult()
      for entry in gFiles:
         entry: GoogleDriveFile = entry
         self._logger.debug("title=`{}` type=`{}` id=`{}`".format(entry['title'], entry['mimeType'], entry['id']))
         if self.__isFolder(entry):
            folder = self.convert_GoogleDriveFile_to_CloudFolderMetadata(entry)
            result.folders.append(folder)
         else:
            file = self.convert_GoogleDriveFile_to_CloudFileMetadata(entry, folder_cloud_path)
            result.files.append(file)
      return result

   def __isFolder(self, entry):
      return entry['mimeType'] == 'application/vnd.google-apps.folder'

   def convert_GoogleDriveFile_to_CloudFileMetadata(self, gFile: GoogleDriveFile, folder_cloud_path:str = '') -> CloudFileMetadata:
      #self.logger.debug('file: {}'.format(gFile))
      file_size = 0 if gFile['mimeType'] == 'application/vnd.google-apps.shortcut' else int(gFile['fileSize'])
      modified = datetime.datetime.strptime(gFile['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
      file_name = gFile['title']
      file_cloud_path = posixpath.join(folder_cloud_path, gFile['title'])
      return CloudFileMetadata(file_name, file_cloud_path, modified, file_size, gFile['id'], '0')

   def convert_GoogleDriveFile_to_CloudFolderMetadata(self, gFile: GoogleDriveFile) -> CloudFolderMetadata:
      #self.logger.debug('file: {}'.format(gFile))
      return CloudFolderMetadata(gFile['id'], gFile['title'], gFile['id'], gFile['title'])
