import os
import time
from datetime import datetime
from logging import Logger


class SystemFileReader:

    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    def get_size(self, full_path: str) -> int:
        return os.path.getsize(full_path)

    def get_modified_time(self, full_path: str) -> datetime:
        modified_time = os.path.getmtime(full_path)
        return datetime(*time.gmtime(modified_time)[:6])
