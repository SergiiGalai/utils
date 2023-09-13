import os
import pathlib
from datetime import datetime, timezone
from logging import Logger
from src.sync.stores.local.system_file_provider import SystemFileProvider
from src.sync.stores.local.path_provider import PathProvider
from src.sync.stores.models import CloudFileMetadata, ListLocalFolderResult, LocalFileMetadata


class LocalFileStore:
    def __init__(self, path_provider: PathProvider, logger: Logger):
        self._path_provider = path_provider
        self._logger = logger
        self._file_provider = SystemFileProvider(path_provider, logger)

    def list_folder(self, cloud_path: str) -> ListLocalFolderResult:
        full_folder_path = self._get_absolute_path(cloud_path)
        self._logger.debug('path={}'.format(full_folder_path))
        result = ListLocalFolderResult()

        if pathlib.Path(full_folder_path).exists():
            _, dir_names, file_names = next(os.walk(full_folder_path))
            result.files = self._file_provider.get_files(cloud_path, file_names)
            result.folders = self._file_provider.get_folders(cloud_path, dir_names)
            return result

        self._logger.warn('path `{}` does not exist'.format(full_folder_path))
        return result

    def _get_absolute_path(self, cloud_path='') -> str:
        return self._path_provider.get_absolute_path(cloud_path)

    def read(self, cloud_path: str) -> tuple[bytes, LocalFileMetadata]:
        md = self._file_provider.get_file(cloud_path)
        with open(md.full_path, 'rb') as f:
            content = f.read()
        return content, md

    def save(self, content: bytes, cloud_md: CloudFileMetadata):
        file_path = self._get_absolute_path(cloud_md.cloud_path)
        base_path = os.path.dirname(file_path)
        self._try_create_local_folder(base_path)
        with open(file_path, 'wb') as f:
            f.write(content)
        self._set_modification_time(
            file_path, self._datetime_utc_to_local(cloud_md.client_modified))
        self._logger.debug('saved file {}...'.format(file_path))

    def _try_create_local_folder(self, path: str):
        self._logger.info('ensure {} path is exist or create'.format(path))
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def _set_modification_time(self, file_path: str, modified: datetime):
        self._logger.debug('file_path={}, modified={}'.format(file_path, modified))
        atime = os.stat(file_path).st_atime
        mtime = modified.timestamp()
        os.utime(file_path, times=(atime, mtime))

    @staticmethod
    def _datetime_utc_to_local(utc_dt) -> datetime:
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
