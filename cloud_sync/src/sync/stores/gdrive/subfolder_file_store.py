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
        sub_path = ''
        result = self._store.list_folder('', sub_path)
        folder_dict = self.__to_cloud_dict(result.folders)
        self._logger.debug('dictionary={}'.format(folder_dict))

        for folder in self.__split_path(cloud_path):
            if folder == '':
                continue
            folder_key = folder.lower()
            sub_path += '/' + folder
            if folder_key in folder_dict:
                cloudFolder: CloudFolderMetadata = folder_dict[folder_key]
                self._logger.debug('next folder=`{}` id=`{}`'.format(
                    cloudFolder.cloud_path, cloudFolder.id))
                result = self._store.list_folder(cloudFolder.id, sub_path)
                folder_dict = self.__to_cloud_dict(result.folders)
        return result

    def __to_cloud_dict(self, folders: list[CloudFolderMetadata]) -> dict[str, CloudFolderMetadata]:
        return {folder.cloud_path.lower(): folder for folder in folders}

    def __split_path(self, path: str) -> list[str]:
        parts = path.split('/')
        self._logger.debug(parts)
        return parts

    def read(self, id: str) -> tuple[bytes, CloudFileMetadata]:
        self._logger.debug('id={}'.format(id))
        return self._store.read(id)

    def save(self, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
        self._logger.debug('cloud_path={}'.format(local_md.cloud_path))
        self._store.save(content, local_md, overwrite)
