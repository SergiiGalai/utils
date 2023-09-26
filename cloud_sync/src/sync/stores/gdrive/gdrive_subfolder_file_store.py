from logging import Logger
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.common import path_helper
from src.sync.stores.gdrive.gdrive_api_v2_store import GdriveApiV2Store
from src.sync.stores.models import CloudFolderMetadata, ListCloudFolderResult, LocalFileMetadata


class GdriveSubfolderFileStore(CloudStore):
    def __init__(self, store: GdriveApiV2Store, logger: Logger):
        self._logger = logger
        self._store = store

    def list_folder(self, cloud_path: str) -> ListCloudFolderResult:
        self._logger.debug('cloud_path={}'.format(cloud_path))
        folder_key = ''
        result = self._store.list_folder('', '')
        folder_dict = GdriveSubfolderFileStore.__to_cloud_dict(result.folders)
        self._logger.debug('dictionary={}'.format(folder_dict))

        for path_part in self.__split_path(cloud_path):
            if path_part == '':
                continue
            folder_key += path_helper.start_with_slash(path_part.lower())
            if folder_key in folder_dict:
                folder: CloudFolderMetadata = folder_dict[folder_key]
                self._logger.debug('next folder=`{}` id=`{}`'.format(folder.cloud_path, folder.id))
                result = self._store.list_folder(folder.id, folder.cloud_path)
                folder_dict = GdriveSubfolderFileStore.__to_cloud_dict(result.folders)
        return result

    @staticmethod
    def __to_cloud_dict(folders: list[CloudFolderMetadata]) -> dict[str, CloudFolderMetadata]:
        return {folder.cloud_path.lower(): folder for folder in folders}

    def __split_path(self, path: str) -> list[str]:
        parts = path.split('/')
        self._logger.debug(parts)
        return parts

    def read_content(self, id: str) -> bytes:
        self._logger.debug('id={}'.format(id))
        return self._store.read_content(id)

    def save(self, content: bytes, local_md: LocalFileMetadata, overwrite: bool):
        self._logger.debug('cloud_path={}'.format(local_md.cloud_path))
        self._store.save(content, local_md, overwrite)
