import dropbox
from logging import Logger
from src.sync.stores.common.path_helper import get_folder_path
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult


# dropbox files https://dropbox-sdk-python.readthedocs.io/en/latest/api/files.html
class DropboxFileConverter:

    def __init__(self, logger: Logger):
        self._logger = logger

    def convert_dropbox_entries_to_cloud(self, dropbox_entries: list) -> ListCloudFolderResult:
        result = ListCloudFolderResult()
        for entry in dropbox_entries:
            self._logger.debug("entry path_display=`%s`, name=%s", entry.path_display, entry.name)
            if DropboxFileConverter.__isFolder(entry):
                cloud_folder = self.convert_DropboxFolder_to_CloudFolder(entry)
                result.folders.append(cloud_folder)
            else:
                cloud_file = self.convert_DropboxFile_to_CloudFile(entry)
                result.files.append(cloud_file)
        return result

    @staticmethod
    def __isFolder(entry):
        return isinstance(entry, dropbox.files.FolderMetadata)  # type: ignore

    # dropbox content hash: https://www.dropbox.com/developers/reference/content-hash
    def convert_DropboxFile_to_CloudFile(self, dbx_md: dropbox.files.FileMetadata) -> CloudFileMetadata:  # type: ignore
        # self._logger.debug('file: %s', dbx_md)
        folder_path = get_folder_path(dbx_md.path_display)
        return CloudFileMetadata(dbx_md.name, dbx_md.path_display,
                                 dbx_md.client_modified, dbx_md.size,
                                 dbx_md.path_lower, folder_path, dbx_md.content_hash)

    def convert_DropboxFolder_to_CloudFolder(self, dbx_dir: dropbox.files.FolderMetadata) -> CloudFolderMetadata:  # type: ignore
        # self._logger.debug('folder: %s', dbx_dir)
        return CloudFolderMetadata(dbx_dir.path_lower, dbx_dir.name,
                                   dbx_dir.path_lower, dbx_dir.path_display)
