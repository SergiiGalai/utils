import datetime
import unittest
from unittest.mock import Mock
import logging

from src.sync.stores.gdrive.file_store_v2 import GdriveStore
from src.sync.stores.gdrive.subfolder_file_store import GdriveSubfolderFileStore
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult


class GdriveSubfolderFileStoreTests(unittest.TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self._store = Mock(GdriveStore)
        self.sut = GdriveSubfolderFileStore(self._store, logger)

    def test_file_when_list_root_folder(self):
        cloud_file = self.__create_cloud_file()
        self.__mock_store_list_folder([cloud_file])
        # act
        actual = self.sut.list_folder('')
        # assert
        self.assertEqual(actual.files, [cloud_file])
        self.assertEqual(actual.folders, [])

    def test_file_when_list_sub_folder_which_does_not_exist_in_cloud(self):
        cloud_file = self.__create_cloud_file()
        self.__mock_store_list_folder([cloud_file])
        # act
        actual = self.sut.list_folder(self._CLOUD_ROOT)
        # assert
        self.assertEqual(actual.files, [cloud_file])
        self.assertEqual(actual.folders, [])

    def test_file_and_folder_when_list_root_cloud_folder(self):
        cloud_file = self.__create_cloud_file()
        cloud_folder = self.__create_cloud_folder()
        self.__mock_store_list_folder([cloud_file], [cloud_folder])
        # act
        actual = self.sut.list_folder(self._CLOUD_ROOT)
        # assert
        self.assertEqual(actual.files, [cloud_file])
        self.assertEqual(actual.folders, [cloud_folder])

    _FILE_ID = '1C7Vb'
    _CLOUD_ROOT = '/Root'

    @staticmethod
    def __create_cloud_file(cloud_path='/Root/File1.pdf', name='File1.pdf', id=_FILE_ID):
        return CloudFileMetadata(name, cloud_path,
                                 datetime.datetime(2023, 8, 15, 14, 27, 44),
                                 12345, id, '0')

    @staticmethod
    def __create_cloud_folder(name='Root',
                              lower_path='/root',
                              display_path=_CLOUD_ROOT,
                              id=_FILE_ID):
        return CloudFolderMetadata(id, name, lower_path, display_path)
    
    def __mock_store_list_folder(self, files: list[CloudFileMetadata], folders: list[CloudFolderMetadata]=[]):
        result = ListCloudFolderResult()
        result.files = files
        result.folders = folders
        self._store.list_folder = Mock(return_value=result)
