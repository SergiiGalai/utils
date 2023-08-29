from pydrive.drive import GoogleDrive, GoogleDriveFile
from pydrive.auth import GoogleAuth
from logging import Logger
from src.configs.config import StorageConfig
from src.stores.cloud_store import CloudStore
from src.stores.file_mappers import GoogleDriveFileMapper
from src.stores.models import CloudFileMetadata, CloudFolderMetadata, LocalFileMetadata

#https://pythonhosted.org/PyDrive/pydrive.html#pydrive.files.GoogleDriveFile
#https://developers.google.com/drive/api/guides/search-files
class GdriveStore(CloudStore):
   def __init__(self, conf: StorageConfig, logger: Logger):
      self._dry_run = conf.dry_run
      self._logger = logger
      self._gdrive = None
      self._mapper = GoogleDriveFileMapper(logger)

   def list_folder(self, cloud_path: str) -> tuple[list[CloudFolderMetadata], list[CloudFileMetadata]]:
      self._logger.debug('cloud_path={}'.format(cloud_path))
      self.__setup_gdrive()

      cloud_dirs, cloud_files = self.__list_folder('')
      folder_dict = {dir.cloud_path.lower(): dir for dir in cloud_dirs}
      self._logger.debug('dictionary={}'.format(folder_dict))

      for part in self.__split_path(cloud_path):
         if part == '': continue
         key = part.lower()
         if key in folder_dict:
            cloudFolder : CloudFolderMetadata = folder_dict[key]
            self._logger.debug('next folder=`{}` id=`{}`'.format(part, cloudFolder.id))
            cloud_dirs, cloud_files = self.__list_folder(cloudFolder.id)
            folder_dict = {dir.cloud_path.lower(): dir for dir in cloud_dirs}

      return cloud_dirs, cloud_files

   def __list_folder(self, folder_id) -> tuple[list[CloudFolderMetadata], list[CloudFileMetadata]]:
      query = "'root' in parents and trashed=false" if folder_id == '' else "parents in '{}' and trashed=false".format(folder_id)
      cloud_dirs = list[CloudFolderMetadata]()
      cloud_files = list[CloudFileMetadata]()

      file_list = self._gdrive.ListFile({'q': query}).GetList()
      for entry in file_list:
         entry: GoogleDriveFile = entry
         self._logger.debug("title=`{}` type=`{}` id=`{}`".format(entry['title'], entry['mimeType'], entry['id']))
         if self.__isFolder(entry):
            folder: CloudFolderMetadata = self._mapper.convert_GoogleDriveFile_to_CloudFolderMetadata(entry)
            cloud_dirs.append(folder)
         else:
            file: CloudFileMetadata = self._mapper.convert_GoogleDriveFile_to_CloudFileMetadata(entry)
            cloud_files.append(file)
      return cloud_dirs, cloud_files

   def __split_path(self, path: str) -> list[str]:
      parts = path.split('/')
      self._logger.debug(parts)
      return parts

   def __setup_gdrive(self):
      if self._gdrive == None:
         self._gdrive = self.__get_gdrive()

   #https://pythonhosted.org/PyDrive/oauth.html
   def __get_gdrive(self) -> GoogleDrive:
      gauth = GoogleAuth()
      gauth.LocalWebserverAuth()
      return GoogleDrive(gauth)

   def __isFolder(self, entry):
      return entry['mimeType'] == 'application/vnd.google-apps.folder'

   def read(self, id: str) -> tuple[bytes, CloudFileMetadata]:
      self._logger.debug('id={}'.format(id))
      self.__setup_gdrive()

   def save(self, cloud_path: str, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
      self._logger.debug('cloud_path={}'.format(cloud_path))
      self.__setup_gdrive()
