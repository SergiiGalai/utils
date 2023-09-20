from pydrive.drive import GoogleDrive, GoogleDriveFile
from pydrive.auth import GoogleAuth
from logging import Logger
from src.configs.config import StorageConfig
from src.sync.stores.gdrive.file_converter import GoogleDriveFileConverter
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult, LocalFileMetadata


# https://pythonhosted.org/PyDrive/pydrive.html#pydrive.files.GoogleDriveFile
# https://developers.google.com/drive/api/guides/search-files
class GdriveApiV2FileStore:
    def __init__(self, conf: StorageConfig, logger: Logger):
        self._dry_run = conf.dry_run
        self._logger = logger
        self._conf = conf
        self._gdrive: GoogleDrive | None = None
        self._converter = GoogleDriveFileConverter(logger)

    def list_folder(self, folder_id: str, cloud_path: str) -> ListCloudFolderResult:
        self._logger.debug('cloud_path={}'.format(cloud_path))
        drive = self.__get_gdrive()
        _ROOT_QUERY = "'root' in parents and trashed=false"
        _SUBFOLDER_QUERY = "parents in '{}' and trashed=false".format(folder_id)
        query = _ROOT_QUERY if folder_id == '' else _SUBFOLDER_QUERY
        file_list = drive.ListFile({'q': query}).GetList()
        return self._converter.convert_GoogleDriveFiles_to_FileMetadatas(file_list, cloud_path)

    # https://pythonhosted.org/PyDrive/oauth.html
    def __get_gdrive(self) -> GoogleDrive:
        if self._gdrive == None:
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            gauth.Authorize()
            self._gdrive = GoogleDrive(gauth)
        return self._gdrive

    def read(self, id: str) -> tuple[bytes, CloudFileMetadata]:
        self._logger.debug('id={}'.format(id))
        drive = self.__get_gdrive()
        metadata = dict(id=id)
        google_file = drive.CreateFile(metadata)
        google_file.FetchMetadata()
        bytes = self.__get_file_content(google_file)
        return bytes, self._converter.convert_GoogleDriveFile_to_CloudFile(google_file)

    def __get_file_content(self, file: GoogleDriveFile) -> bytes:
        file.FetchContent()
        content_bytes = file.content    # BytesIO
        bytes = content_bytes.read()
        return bytes

    def save(self, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
        self._logger.debug('cloud_path={}'.format(local_md.cloud_path))
        drive = self.__get_gdrive()
        # TODO use overwrite argument
        # TODO upload to subfolder

        # folder_id = folder['id']
        # metadata = dict(title = local_md.name, parents = [{'id': folder_id}])
        metadata = dict(title=local_md.name)
        google_file = drive.CreateFile(metadata)
        google_file.SetContentString(content)
        if self._dry_run:
            self._logger.info('Dry run mode. Skip uploading {} (modified:{})'.format(
                local_md.cloud_path, local_md.client_modified))
        else:
            try:
                google_file.Upload()
            finally:
                google_file.content.close()
