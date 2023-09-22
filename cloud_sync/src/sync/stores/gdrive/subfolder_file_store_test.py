from unittest import TestCase
from unittest.mock import MagicMock, Mock
import logging

from src.sync.stores.gdrive.file_store_api_v2 import GdriveApiV2FileStore
from src.sync.stores.gdrive.subfolder_file_store import GdriveSubfolderFileStore
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult
from tests.file_metadata import create_cloud_file


class TestGdriveSubfolderFileStore(TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self._store = Mock(GdriveApiV2FileStore)
        self._sut = GdriveSubfolderFileStore(self._store, logger)

    def test_file_when_list_sub_folder_which_does_not_exist_in_cloud(self):
        cloud_file = create_cloud_file()
        self.__mock_store_list_folder([cloud_file])
        # act
        actual = self._sut.list_folder('/Target')
        assert actual.files == [cloud_file]
        assert actual.folders == []

    def test_file_and_subfolder_when_list_root_cloud_folder(self):
        cloud_folder = self.__create_cloud_folder()
        cloud_file = create_cloud_file()
        self.__mock_store_list_folder([cloud_file], [cloud_folder])
        # act
        actual = self._sut.list_folder('/Target')
        assert actual.files == [cloud_file]
        assert actual.folders == [cloud_folder]

    def test_files_and_folders_when_list_target_non_root_folder(self):
        # arrange
        cloud_file_root =       create_cloud_file(cloud_path='/File1.pdf', id='idrf1')
        cloud_folder_sub =    self.__create_cloud_folder('/Sub', '/sub', 'Sub', 'SubFolderId')
        cloud_file_sub =        create_cloud_file(cloud_path='/Sub/File1.pdf', id='idf1')
        cloud_folder_sub1 =   self.__create_cloud_folder('/Sub/Sub1', '/sub/sub1', 'Sub1', 'Sub1FolderId')
        cloud_file_sub1 =       create_cloud_file(cloud_path='/Sub/Sub1/File1.pdf', id='idsubf1')
        cloud_folder_target = self.__create_cloud_folder('/Sub/Target', '/sub/target', 'Target', 'TargetFolderId')
        cloud_file_target =     create_cloud_file(cloud_path='/Sub/Target/File2.pdf', name='File2.pdf', id='idsubf2')
        cloud_folder_sub2 =   self.__create_cloud_folder('/Sub/Target/Sub2', '/sub/target/sub2' 'Sub2', 'Sub2FolderId')
        cloud_file_sub2 =       create_cloud_file(cloud_path='/Sub/Target/File2.pdf', name='File2.pdf', id='idsubf2')

        self._store.list_folder = MagicMock(side_effect=lambda *x: {
            ('', ''): ListCloudFolderResult([cloud_file_root], [cloud_folder_sub]),
            ('SubFolderId', '/Sub'): ListCloudFolderResult([cloud_file_sub], [cloud_folder_sub1, cloud_folder_target]),
            ('Sub1FolderId', '/Sub/Sub1'): ListCloudFolderResult([cloud_file_sub1], []),
            ('TargetFolderId', '/Sub/Target'): ListCloudFolderResult([cloud_file_target], [cloud_folder_sub2]),
            ('Sub2FolderId', '/Sub/Target/Sub2'): ListCloudFolderResult([cloud_file_sub2], []),
        }[x]) # type: ignore
        # act
        actual = self._sut.list_folder('/Sub/Target')
        assert actual.files == [cloud_file_target]
        assert actual.folders == [cloud_folder_sub2]

    @staticmethod
    def __create_cloud_folder(display_path='/Target',
                              lower_path='/target',
                              name='Target',
                              id='1C7Vb'):
        return CloudFolderMetadata(id, name, lower_path, display_path)
    
    def __mock_store_list_folder(self, files: list[CloudFileMetadata], folders: list[CloudFolderMetadata]=[]):
        result = ListCloudFolderResult()
        result.files = files
        result.folders = folders
        self._store.list_folder.return_value = result
