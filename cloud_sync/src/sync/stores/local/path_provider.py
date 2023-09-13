from src.configs.config import StorageConfig

import pathlib
from logging import Logger

from src.sync.stores.common.path_helper import PathHelper



class PathProvider:
    def __init__(self, config: StorageConfig, logger: Logger):
        self._root_path = config.local_dir
        self._logger = logger

    def get_absolute_path(self, cloud_path='') -> str:
        relative_path = PathHelper.strip_starting_slash(cloud_path)
        result = pathlib.PurePath(self._root_path).joinpath(relative_path)
        self._logger.debug('result={}'.format(result))
        return str(result)
