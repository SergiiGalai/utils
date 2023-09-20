import datetime
import posixpath
from pydrive.drive import GoogleDriveFile
from logging import Logger
from src.sync.stores.common.path_helper import PathHelper

from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult


# ? https://developers.google.com/drive/api/reference/rest/v2/files
class GoogleDriveFileConverter:
    def __init__(self, logger: Logger):
        self._logger = logger

    def convert_GoogleDriveFiles_to_FileMetadatas(self,
                                                  gFiles: list[GoogleDriveFile],
                                                  folder_cloud_path: str = '') -> ListCloudFolderResult:
        result = ListCloudFolderResult()
        for entry in gFiles:
            entry: GoogleDriveFile = entry
            self._logger.debug("title=`{}` type=`{}` id=`{}`".format(
                entry['title'], entry['mimeType'], entry['id']))
            if GoogleDriveFileConverter.__isFolder(entry):
                folder = self.convert_GoogleDriveFile_to_CloudFolderMetadata(entry, folder_cloud_path)
                result.folders.append(folder)
            else:
                file = self.convert_GoogleDriveFile_to_CloudFile(entry, folder_cloud_path)
                result.files.append(file)
        return result

    @staticmethod
    def __isFolder(entry):
        return entry['mimeType'] == 'application/vnd.google-apps.folder'

    def convert_GoogleDriveFile_to_CloudFile(self,
                                             gFile: GoogleDriveFile,
                                             parent_folder_path: str = '') -> CloudFileMetadata:
        # self.logger.debug('file: {}'.format(gFile))
        parent_folder_path = PathHelper.start_with_slash(parent_folder_path)
        file_size = 0 if gFile['mimeType'] == 'application/vnd.google-apps.shortcut' else int(gFile['fileSize'])
        modified = datetime.datetime.strptime(gFile['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
        file_name = gFile['title']
        file_cloud_path = posixpath.join(parent_folder_path, gFile['title'])
        return CloudFileMetadata(file_name, file_cloud_path, modified, file_size, gFile['id'], '0')

    def convert_GoogleDriveFile_to_CloudFolderMetadata(self,
                                                       gFolder: GoogleDriveFile,
                                                       parent_folder_path: str = '') -> CloudFolderMetadata:
        # self.logger.debug('file: {}'.format(gFile))
        parent_folder_path = PathHelper.start_with_slash(parent_folder_path)
        cloud_folder_path = posixpath.join(parent_folder_path, gFolder['title'])
        lower_folder_path = cloud_folder_path.lower()
        return CloudFolderMetadata(gFolder['id'], gFolder['title'], lower_folder_path, cloud_folder_path)
