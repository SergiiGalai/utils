import datetime
import posixpath
from pydrive.drive import GoogleDriveFile
from logging import Logger
from src.sync.stores.common import path_helper

from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, CloudId, ListCloudFolderResult


# ? https://developers.google.com/drive/api/reference/rest/v2/files
class GoogleDriveFileConverter:
    def __init__(self, logger: Logger):
        self._logger = logger

    def convert_GoogleDriveFiles_to_FileMetadatas(self,
                                                  gFiles: list[GoogleDriveFile],
                                                  folder_cloud_path: str) -> ListCloudFolderResult:
        result = ListCloudFolderResult()
        for entry in gFiles:
            entry: GoogleDriveFile = entry
            self._logger.debug("title=`%s` type=%s id=%s folder=%s",
                entry['title'], entry['mimeType'], entry['id'], folder_cloud_path)
            if GoogleDriveFileConverter.__isFolder(entry):
                gfolder = self.convert_GoogleDriveFile_to_CloudFolderMetadata(entry, folder_cloud_path)
                result.folders.append(gfolder)
            else:
                parent_id = entry['parents'][0]['id']
                file = self.convert_GoogleDriveFile_to_CloudFile(entry, CloudId(parent_id, folder_cloud_path))
                result.files.append(file)
        return result

    @staticmethod
    def __isFolder(entry):
        return entry['mimeType'] == 'application/vnd.google-apps.folder'

    def convert_GoogleDriveFile_to_CloudFile(self,
                                             gFile: GoogleDriveFile,
                                             parent: CloudId) -> CloudFileMetadata:
        # self._logger.debug('file: %s', gFile)
        parent_path = path_helper.start_with_slash(parent.cloud_path)
        file_size = 0 if gFile['mimeType'] == 'application/vnd.google-apps.shortcut' else int(gFile['fileSize'])
        modified = datetime.datetime.strptime(gFile['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
        file_name = gFile['title']
        file_cloud_path = posixpath.join(parent_path, gFile['title'])
        return CloudFileMetadata(file_name, file_cloud_path, modified, file_size, gFile['id'],
                                 parent, '0')

    def convert_GoogleDriveFile_to_CloudFolderMetadata(self,
                                                       gFolder: GoogleDriveFile,
                                                       parent_folder_path: str) -> CloudFolderMetadata:
        # self._logger.debug('file: %s', gFile)
        parent_folder_path = path_helper.start_with_slash(parent_folder_path)
        cloud_folder_path = posixpath.join(parent_folder_path, gFolder['title'])
        lower_folder_path = cloud_folder_path.lower()
        return CloudFolderMetadata(gFolder['id'], gFolder['title'], lower_folder_path, cloud_folder_path)
