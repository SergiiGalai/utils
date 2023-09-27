from pydrive.drive import GoogleDrive, GoogleDriveFile
from pydrive.auth import GoogleAuth
from logging import Logger
from src.configs.storage_config import StorageConfig
from src.sync.stores.gdrive.gdrive_file_converter import GoogleDriveFileConverter
from src.sync.stores.models import CloudId, ListCloudFolderResult, LocalFileMetadata


# https://pythonhosted.org/PyDrive/pydrive.html#pydrive.files.GoogleDriveFile
# https://developers.google.com/drive/api/guides/search-files
class GdriveApiV2Store:
    def __init__(self, conf: StorageConfig, logger: Logger):
        self._dry_run = conf.dry_run
        self._logger = logger
        self._conf = conf
        self._gdrive: GoogleDrive | None = None
        self._converter = GoogleDriveFileConverter(logger)

    def list_folder(self, cloud_folder: CloudId) -> ListCloudFolderResult:
        self._logger.debug('cloud_folder=%s', cloud_folder)
        drive = self.__get_gdrive()
        query = GdriveApiV2Store.__get_query(cloud_folder.id)
        file_list = drive.ListFile({'q': query}).GetList()
        return self._converter.convert_GoogleDriveFiles_to_FileMetadatas(file_list, cloud_folder.cloud_path)

    @staticmethod
    def __get_query(folder_id: str) -> str:
        _ROOT_QUERY = "'root' in parents and trashed=false"
        _SUBFOLDER_QUERY = f"parents in '{folder_id}' and trashed=false"
        return _ROOT_QUERY if folder_id == '' else _SUBFOLDER_QUERY

    # https://pythonhosted.org/PyDrive/oauth.html
    def __get_gdrive(self) -> GoogleDrive:
        if self._gdrive == None:
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            gauth.Authorize()
            self._gdrive = GoogleDrive(gauth)
        return self._gdrive

    def read_content(self, id: str) -> bytes:
        self._logger.debug('id=%s', id)
        drive = self.__get_gdrive()
        metadata = dict(id=id)
        google_file = drive.CreateFile(metadata)
        google_file.FetchMetadata()
        bytes = GdriveApiV2Store.__get_file_content(google_file)
        return bytes

    @staticmethod
    def __get_file_content(file: GoogleDriveFile) -> bytes:
        file.FetchContent()
        content_bytes = file.content    # BytesIO
        bytes = content_bytes.read()
        return bytes

    def save(self, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
        self._logger.debug('cloud_path=%s', local_md.cloud_path)
        drive = self.__get_gdrive()
        # TODO upload to subfolder
        # TODO use overwrite argument

        metadata = GdriveApiV2Store.__to_gfile_name_metadata(local_md)
        google_file = drive.CreateFile(metadata)
        google_file.SetContentString(content)
        if self._dry_run:
            self._logger.info('Dry run mode. Skip uploading %s (modified:%s)',
                local_md.cloud_path, local_md.client_modified)
        else:
            try:
                google_file.Upload()
            finally:
                google_file.content.close()

    @staticmethod
    def __to_gfile_name_metadata(local: LocalFileMetadata) -> dict:
        return dict(title=local.name)

    @staticmethod
    def __to_gfile_metadata(local: LocalFileMetadata) -> dict:
        # folder_id = folder['id']
        folder_id = 'TODO'
        return dict(title=local.name,
                    parents=[{'id': folder_id}],
                    mimeType=local.mime_type)
