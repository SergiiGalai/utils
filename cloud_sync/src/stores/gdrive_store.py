from pydrive.drive import GoogleDrive, GoogleDriveFile, GoogleDriveFileList
from pydrive.auth import GoogleAuth
from logging import Logger
from src.configs.config import StorageConfig
from src.stores.cloud_store import CloudStore
from src.stores.models import CloudFileMetadata, CloudFolderMetadata
from src.stores.local_file_store import LocalFileMetadata

class GdriveStore(CloudStore):
   def __init__(self, conf: StorageConfig, logger: Logger):
      self._dry_run = conf.dry_run
      self._logger = logger
      self._gdrive = None

   def __get_gdrive(self):
      # Authenticate request
      gauth = GoogleAuth()
      gauth.LocalWebserverAuth()
      return GoogleDrive(gauth)

   def __setup_gdrive(self):
      if self._gdrive == None:
         self._gdrive = self.__get_gdrive()

   def list_folder(self, cloud_path):
      self._logger.debug('list path: {}'.format(cloud_path))
      self.__setup_gdrive()
      cloud_dirs = list()
      cloud_files = list()

      queryString = "'root' in parents and trashed=false"
      #queryString = "parents in title='Docs'"
      file_list = self._gdrive.ListFile({'q': queryString}).GetList()
      for entry in file_list:
         self._logger.debug("title=`{}` type=`{}` id=`{}`".format(entry['title'], entry['mimeType'], entry['id']))
         if self.__isFolder(entry):
            cloud_dirs.append(self.__to_CloudFolderMetadata(entry))
         else:
            cloud_files.append(self.__to_CloudFileMetadata(entry))
      return cloud_path, cloud_dirs, cloud_files

   def __isFolder(self, entry):
      return entry['mimeType'] == 'application/vnd.google-apps.folder'

   def __to_CloudFileMetadata(self, gFile: GoogleDriveFile)-> CloudFileMetadata:
      #self.logger.debug('file: {}'.format(gFile))
      fileSize = None if gFile['mimeType'] == 'application/vnd.google-apps.shortcut' else gFile['fileSize']
      return CloudFileMetadata(gFile['id'], gFile['title'], gFile['modifiedDate'], fileSize)

   def __to_CloudFolderMetadata(self, gFolder: GoogleDriveFile)-> CloudFolderMetadata:
      #self.logger.debug('folder: {}'.format(gFolder))
      return CloudFolderMetadata(gFolder['id'], gFolder['title'])
   
   def read(self, cloud_path: str):
      self._logger.debug('cloud_path={}'.format(cloud_path))
      self.__setup_gdrive()

   def save(self, cloud_path: str, content, local_md: LocalFileMetadata, overwrite: bool):
      self._logger.debug('cloud_path={}'.format(cloud_path))
      self.__setup_gdrive()
