import pathlib
from logging import Logger
from src.configs.config import StorageConfig
from src.sync.stores.common import path_helper


class PathProvider:
    def __init__(self, config: StorageConfig, logger: Logger):
        self._root_path = config.local_dir
        self._logger = logger

    def get_absolute_path(self, cloud_path='') -> str:
        relative_path = path_helper.strip_starting_slash(cloud_path)
        result = pathlib.PurePath(self._root_path).joinpath(relative_path)
        self._logger.debug('result={}'.format(result))
        return str(result)
