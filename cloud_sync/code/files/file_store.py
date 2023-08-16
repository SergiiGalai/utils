import time
import os
import pathlib
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from logging import Logger
from code.configs.config import Config

@dataclass
class FileMetadata:
    name: str
    path: str
    client_modified: datetime
    size: int

class FileStore:
    def __init__(self, conf: Config, logger: Logger):
        self.dry_run = conf.dry_run
        self.root_path = conf.local_dir
        self.logger = logger

    def save(self, dbox_path: str, content, client_modified):
        file_path = self.get_absolute_path(dbox_path)
        if self.dry_run:
            self.logger.info('dry run mode. Skip saving file {}'.format(file_path))
        else:
            base_path = os.path.dirname(file_path)
            self.__try_create_local_folder(base_path)
            with open(file_path, 'wb') as f:
                f.write(content)
            self.__set_modification_time(file_path, self.__datetime_utc_to_local(client_modified))
            self.logger.debug('saved file {}...'.format(file_path))

    def __try_create_local_folder(self, path: str):
        if self.dry_run:
            self.logger.info('Dry Run mode. path {}'.format(path))
        else:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def __set_modification_time(self, file_path: str, modified: datetime):
        if self.dry_run:
            self.logger.info('Dry Run mode. file_path {}, modified={}'.format(os.path.basename(file_path), modified))
        else:
            self.logger.debug('file_path={}, modified={}'.format(file_path, modified))
            atime = os.stat(file_path).st_atime
            mtime = modified.timestamp()
            os.utime(file_path, times=(atime, mtime))

    def get_absolute_path(self, dbox_path: str) -> str:
        relative_db_path = dbox_path[1:] if dbox_path.startswith('/') else dbox_path
        result = pathlib.PurePath( self.root_path ).joinpath( relative_db_path )
        self.logger.debug('result={}'.format(result))
        return str(result)

    @staticmethod
    def __datetime_utc_to_local(utc_dt) -> datetime:
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def list_folder(self, dbox_path: str):
        path = self.get_absolute_path(dbox_path)
        self.logger.debug('path={}'.format(path))
        if pathlib.Path(path).exists():
            root, dirs, files = next(os.walk(path))
            normalizedFiles = [unicodedata.normalize('NFC', f) for f in files]
            self.logger.debug('files={}'.format(normalizedFiles))
            return root, dirs, normalizedFiles
        return path, [], []

    def read(self, full_path: str):
        md = self.get_metadata(full_path)
        with open(full_path, 'rb') as f:
            content = f.read()
        return content, md

    @staticmethod
    def get_metadata(full_path: str) -> FileMetadata:
        name = os.path.basename(full_path)
        mtime = os.path.getmtime(full_path)
        client_modified = datetime(*time.gmtime(mtime)[:6])
        size = os.path.getsize(full_path)
        return FileMetadata(name, full_path, client_modified, size)
