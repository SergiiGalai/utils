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

   def list_folder(self, cloud_path):
      self._logger.debug('cloud_path={}'.format(cloud_path))
      self.__setup_gdrive()

      cloud_dirs, cloud_files = self.__list_folder('')
      folder_dict = {dir.path_display.lower(): dir for dir in cloud_dirs}
      self._logger.debug('dictionary={}'.format(folder_dict))

      for part in self.__split_path(cloud_path):
         if part == '': continue
         key = part.lower()
         if key in folder_dict:
            cloudFolder : CloudFolderMetadata = folder_dict[key]
            self._logger.debug('next folder=`{}` id=`{}`'.format(part, cloudFolder.id))
            cloud_dirs, cloud_files = self.__list_folder(cloudFolder.id)
            folder_dict = {dir.path_display.lower(): dir for dir in cloud_dirs}

      return cloud_path, cloud_dirs, cloud_files

   def __list_folder(self, folder_id):
      query = "'root' in parents and trashed=false" if folder_id == '' else "parents in '{}' and trashed=false".format(folder_id)
      cloud_dirs = []
      cloud_files = []

      file_list = self._gdrive.ListFile({'q': query}).GetList()
      for entry in file_list:
         self._logger.debug("title=`{}` type=`{}` id=`{}`".format(entry['title'], entry['mimeType'], entry['id']))
         if self.__isFolder(entry):
            folder = self.__to_CloudFolderMetadata(entry)
            cloud_dirs.append(folder)
         else:
            file = self.__to_CloudFileMetadata(entry)
            cloud_files.append(file)
      return cloud_dirs, cloud_files

   def __split_path(self, path) -> list:
      parts = path.split('/')
      self._logger.debug(parts)
      return parts

   def __setup_gdrive(self):
      if self._gdrive == None:
         self._gdrive = self.__get_gdrive()

   def __get_gdrive(self):
      # Authenticate request
      gauth = GoogleAuth()
      gauth.LocalWebserverAuth()
      return GoogleDrive(gauth)

   def __isFolder(self, entry):
      return entry['mimeType'] == 'application/vnd.google-apps.folder'

   def __to_CloudFileMetadata(self, gFile: GoogleDriveFile)-> CloudFileMetadata:
      #self.logger.debug('file: {}'.format(gFile))
      fileSize = None if gFile['mimeType'] == 'application/vnd.google-apps.shortcut' else gFile['fileSize']
      return CloudFileMetadata(gFile['id'], gFile['title'], gFile['title'], gFile['modifiedDate'], fileSize)

   def __to_CloudFolderMetadata(self, gFolder: GoogleDriveFile)-> CloudFolderMetadata:
      #self.logger.debug('folder: {}'.format(gFolder))
      return CloudFolderMetadata(gFolder['id'], gFolder['title'], gFolder['id'], gFolder['title'])
   
   def read(self, id: str):
      self._logger.debug('id={}'.format(id))
      self.__setup_gdrive()

   def save(self, cloud_path: str, content, local_md: LocalFileMetadata, overwrite: bool):
      self._logger.debug('cloud_path={}'.format(cloud_path))
      self.__setup_gdrive()
