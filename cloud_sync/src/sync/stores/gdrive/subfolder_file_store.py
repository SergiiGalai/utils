from logging import Logger
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.gdrive.file_store_v2 import GdriveStore
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult, LocalFileMetadata


class GdriveSubfolderFileStore(CloudStore):
    def __init__(self, store: GdriveStore, logger: Logger):
        self._logger = logger
        self._store = store

    def list_folder(self, cloud_path: str) -> ListCloudFolderResult:
        self._logger.debug('cloud_path={}'.format(cloud_path))
        folder_key = ''
        result = self._store.list_folder('', '')
        folder_dict = GdriveSubfolderFileStore.__to_cloud_dict(result.folders)
        self._logger.debug('dictionary={}'.format(folder_dict))

        for folder in self.__split_path(cloud_path):
            if folder == '':
                continue
            folder_key += GdriveSubfolderFileStore.__start_with_slash(folder.lower())
            if folder_key in folder_dict:
                cloud_folder: CloudFolderMetadata = folder_dict[folder_key]
                self._logger.debug('next folder=`{}` id=`{}`'.format(cloud_folder.cloud_path, cloud_folder.id))
                result = self._store.list_folder(cloud_folder.id, cloud_folder.cloud_path)
                folder_dict = GdriveSubfolderFileStore.__to_cloud_dict(result.folders)
        return result

    @staticmethod
    def __to_cloud_dict(folders: list[CloudFolderMetadata]) -> dict[str, CloudFolderMetadata]:
        return {folder.cloud_path.lower(): folder for folder in folders}

    def __split_path(self, path: str) -> list[str]:
        parts = path.split('/')
        self._logger.debug(parts)
        return parts

    @staticmethod
    def __start_with_slash(path):
        return path if path.startswith('/') else '/' + path

    def read(self, id: str) -> tuple[bytes, CloudFileMetadata]:
        self._logger.debug('id={}'.format(id))
        return self._store.read(id)

    def save(self, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
        self._logger.debug('cloud_path={}'.format(local_md.cloud_path))
        self._store.save(content, local_md, overwrite)