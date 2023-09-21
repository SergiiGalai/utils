import mimetypes
from logging import Logger


class MimeTypeProvider:

    def __init__(self, logger: Logger):
        self._logger = logger
        mimetypes.init()

    def get_by_extension(self, file_extension: str) -> str:
        return mimetypes.types_map.get(file_extension.lower(), 'text/plain')
