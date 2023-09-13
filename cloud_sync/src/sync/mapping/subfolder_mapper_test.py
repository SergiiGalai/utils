import unittest
from unittest.mock import Mock
import logging
from src.sync.mapping.subfolder_mapper import SubfolderMapper
from src.sync.stores.models import CloudFolderMetadata, LocalFolderMetadata


class SubfolderMapperTests(unittest.TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self.sut = SubfolderMapper(logger)

    def test_empty_when_no_subfolders(self):
        # act
        actual = self.sut.map_cloud_to_local([], [])
        # assert
        self.assertSetEqual(actual, set())

    def test_one_item_when_local_and_cloud_folders_match(self):
        local_folder = self.__create_local_folder()
        cloud_folder = self.__create_cloud_folder()
        # act
        actual = self.sut.map_cloud_to_local([cloud_folder], [local_folder])
        # assert
        self.assertSetEqual(actual, set(['/Target/Sub']))

    def test_merged_items_when_local_and_cloud_have_differnt_folders(self):
        local_folder1 = self.__create_local_folder('/Target/dir1', name='dir1')
        local_folder2 = self.__create_local_folder('/Target/Dir2', name='Dir2')
        cloud_folder = self.__create_cloud_folder()
        # act
        actual = self.sut.map_cloud_to_local([cloud_folder], [local_folder1, local_folder2])
        # assert
        self.assertSetEqual(actual, set(['/Target/Sub', '/Target/dir1', '/Target/Dir2']))

    _FOLDER_NAME = 'Sub'
    _CLOUD_FOLDER_PATH = '/Target/Sub'

    @staticmethod
    def __create_cloud_folder(cloud_path=_CLOUD_FOLDER_PATH,
                              lower_path='/target/sub',
                              name=_FOLDER_NAME) -> CloudFolderMetadata:
        return CloudFolderMetadata(lower_path, name, lower_path, cloud_path)

    @staticmethod
    def __create_local_folder(cloud_path=_CLOUD_FOLDER_PATH,
                              full_path='d:\\sync\\Target\\sub',
                              name=_FOLDER_NAME) -> LocalFolderMetadata:
        return LocalFolderMetadata(name, cloud_path, full_path)
