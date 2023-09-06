import time
import os
import pathlib
import posixpath
import unicodedata
from datetime import datetime, timezone
from logging import Logger
from src.stores.local.path_provider import PathProvider
from src.stores.models import CloudFileMetadata, ListLocalFolderResult, LocalFileMetadata

class LocalFileStore:
    def __init__(self, path_provider: PathProvider, logger: Logger):
        self._path_provider = path_provider
        self._logger = logger

    def list_folder(self, cloud_path: str) -> ListLocalFolderResult:
        full_folder_path = self._get_absolute_path(cloud_path)
        self._logger.debug('path={}'.format(full_folder_path))
        result = ListLocalFolderResult()

        if pathlib.Path(full_folder_path).exists():
            _, dir_names, file_names = next(os.walk(full_folder_path))
            file_paths = list(self._join_path(cloud_path, unicodedata.normalize('NFC', f)) for f in file_names)
            list_md = list(self._get_file_metadata(f) for f in file_paths)
            self._logger.debug('list_md={}'.format(list_md))
            result.folders = dir_names
            result.files = list_md
            return result

        self._logger.warn('path `{}` does not exist'.format(full_folder_path))
        return result

    def _get_absolute_path(self, cloud_path='') -> str:
        return self._path_provider.get_absolute_path(cloud_path)

    def read(self, cloud_path: str) -> tuple[bytes, LocalFileMetadata]:
        md = self._get_file_metadata(cloud_path)
        with open(md.local_path, 'rb') as f:
            content = f.read()
        return content, md

    def _get_file_metadata(self, cloud_path: str) -> LocalFileMetadata:
        local_path = self._get_absolute_path(cloud_path)
        name = os.path.basename(local_path)
        mtime = os.path.getmtime(local_path)
        client_modified = datetime(*time.gmtime(mtime)[:6])
        size = os.path.getsize(local_path)
        return LocalFileMetadata(name, cloud_path, client_modified, size, local_path)

    def _join_path(self, path1: str, path2: str) -> str:
        relative_path = path2[1:] if path2.startswith('/') else path2
        result = posixpath.join(path1, relative_path)
        self._logger.debug('result={}'.format(result))
        return result

    def save(self, content: bytes, cloud_md: CloudFileMetadata):
        file_path = self._get_absolute_path(cloud_md.cloud_path)
        base_path = os.path.dirname(file_path)
        self._try_create_local_folder(base_path)
        with open(file_path, 'wb') as f:
            f.write(content)
        self._set_modification_time(file_path, self._datetime_utc_to_local(cloud_md.client_modified))
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
