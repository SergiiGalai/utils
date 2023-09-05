from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from logging import Logger
from src.configs.config import StorageConfig
from src.stores.cloud_store import CloudStore
from src.stores.gdrive_file_converter import GoogleDriveFileConverter
from src.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult, LocalFileMetadata

#https://pythonhosted.org/PyDrive/pydrive.html#pydrive.files.GoogleDriveFile
#https://developers.google.com/drive/api/guides/search-files
class GdriveStore(CloudStore):
   def __init__(self, conf: StorageConfig, logger: Logger):
      self._dry_run = conf.dry_run
      self._logger = logger
      self._gdrive = None
      self._converter = GoogleDriveFileConverter(logger)

   def list_folder(self, cloud_path: str) -> ListCloudFolderResult:
      self._logger.debug('cloud_path={}'.format(cloud_path))
      self.__setup_gdrive()

      sub_path = ''
      result = self.__list_folder('', sub_path)
      folder_dict = {folder.cloud_path.lower(): folder for folder in result.folders}
      self._logger.debug('dictionary={}'.format(folder_dict))

      for part in self.__split_path(cloud_path):
         if part == '': continue
         key = part.lower()
         sub_path += '/' + part
         if key in folder_dict:
            cloudFolder : CloudFolderMetadata = folder_dict[key]
            self._logger.debug('next folder=`{}` id=`{}`'.format(cloudFolder.cloud_path, cloudFolder.id))
            result = self.__list_folder(cloudFolder.id, sub_path)
            folder_dict = {folder.cloud_path.lower(): folder for folder in result.folders}
      return result

   def __list_folder(self, folder_id:str, cloud_path:str) -> ListCloudFolderResult:
      query = "'root' in parents and trashed=false" if folder_id == '' else "parents in '{}' and trashed=false".format(folder_id)
      file_list = self._gdrive.ListFile({'q': query}).GetList()
      return self._converter.convert_GoogleDriveFiles_to_FileMetadatas(file_list, cloud_path)

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
      gauth.Authorize()
      return GoogleDrive(gauth)

   def read(self, id: str) -> tuple[bytes, CloudFileMetadata]:
      self._logger.debug('id={}'.format(id))
      self.__setup_gdrive()

      metadata = dict(id = id)
      google_file = self._gdrive.CreateFile(metadata)
      google_file.GetContentFile( filename= id )
      content_bytes = google_file.content    # BytesIO
      bytes = content_bytes.read()
      #TODO add cloud path
      return bytes, self._converter.convert_GoogleDriveFile_to_CloudFileMetadata(google_file)

   def save(self, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
      self._logger.debug('cloud_path={}'.format(local_md.cloud_path))
      self.__setup_gdrive()
      #TODO use overwrite argument
      #TODO upload to subfolder

      #folder_id = folder['id']
      #metadata = dict(title = local_md.name, parents = [{'id': folder_id}])
      metadata = dict(title = local_md.name)
      google_file = self._gdrive.CreateFile(metadata)
      google_file.SetContentString(content)
      try:
         google_file.Upload()
      finally:
         google_file.content.close()
