import mimetypes


class MimeTypeProvider:

    def __init__(self):
        mimetypes.init()

    def get_by_extension(self, file_extension: str) -> str:
        return mimetypes.types_map.get(file_extension.lower(), 'text/plain')
