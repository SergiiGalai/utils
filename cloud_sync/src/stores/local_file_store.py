import time
import os
import pathlib
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from logging import Logger
from src.configs.config import StorageConfig

@dataclass
class LocalFileMetadata:
    name: str
    path: str
    client_modified: datetime
    size: int

class LocalFileStore:
    def __init__(self, config: StorageConfig, logger: Logger):
        self._dry_run = config.dry_run
        self._root_path = config.local_dir
        self._logger = logger

    def list_folder(self, cloud_path: str):
        path = self.get_absolute_path(cloud_path)
        self._logger.debug('path={}'.format(path))

        if pathlib.Path(path).exists():
            root, dirs, files = next(os.walk(path))
            normalizedFiles = [unicodedata.normalize('NFC', f) for f in files]
            self._logger.debug('files={}'.format(normalizedFiles))
            return root, dirs, normalizedFiles

        self._logger.warn('path `{}` does not exist'.format(path))
        return path, [], []

    def read(self, full_path: str):
        md = self.get_file_metadata(full_path)
        with open(full_path, 'rb') as f:
            content = f.read()
        return content, md

    @staticmethod
    def get_file_metadata(full_path: str) -> LocalFileMetadata:
        name = os.path.basename(full_path)
        mtime = os.path.getmtime(full_path)
        client_modified = datetime(*time.gmtime(mtime)[:6])
        size = os.path.getsize(full_path)
        return LocalFileMetadata(name, full_path, client_modified, size)

    def get_absolute_path(self, cloud_path: str) -> str:
        relative_db_path = cloud_path[1:] if cloud_path.startswith('/') else cloud_path
        result = pathlib.PurePath( self._root_path ).joinpath( relative_db_path )
        self._logger.debug('result={}'.format(result))
        return str(result)
    
    def save(self, cloud_path: str, content, client_modified):
        file_path = self.get_absolute_path(cloud_path)
        if self._dry_run:
            self._logger.info('dry run mode. Skip saving file {}'.format(file_path))
        else:
            base_path = os.path.dirname(file_path)
            self.__try_create_local_folder(base_path)
            with open(file_path, 'wb') as f:
                f.write(content)
            self.__set_modification_time(file_path, self.__datetime_utc_to_local(client_modified))
            self._logger.debug('saved file {}...'.format(file_path))

    def __try_create_local_folder(self, path: str):
        if self._dry_run:
            self._logger.info('Dry Run mode. path {}'.format(path))
        else:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def __set_modification_time(self, file_path: str, modified: datetime):
        if self._dry_run:
            self._logger.info('Dry Run mode. file_path {}, modified={}'.format(os.path.basename(file_path), modified))
        else:
            self._logger.debug('file_path={}, modified={}'.format(file_path, modified))
            atime = os.stat(file_path).st_atime
            mtime = modified.timestamp()
            os.utime(file_path, times=(atime, mtime))

    @staticmethod
    def __datetime_utc_to_local(utc_dt) -> datetime:
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
