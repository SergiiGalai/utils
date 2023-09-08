import unittest
from unittest.mock import Mock
import logging
from src.sync.mapping.subfolder_mapper import SubfolderMapper
from src.sync.stores.models import CloudFolderMetadata


class SubfolderMapperTests(unittest.TestCase):
    _FOLDER_NAME = 'Sub'
    _CLOUD_FOLDER_PATH = '/root/Sub'
    _CLOUD_LOWER_FOLDER_PATH = '/root/sub'
    _DEFAULT_CLOUD_ROOT = '/root'

    def setUp(self):
        logger = Mock(logging.Logger)
        self.sut = SubfolderMapper(logger)

    def test_empty_when_no_subfolders(self):
        # act
        actual = self.sut.map_cloud_to_local(self._DEFAULT_CLOUD_ROOT, [], [])
        # assert
        self.assertSetEqual(actual, set())

    def test_one_item_when_local_and_cloud_folders_match(self):
        local_folder = self.__create_local_folder()
        cloud_folder = self.__create_cloud_folder()
        # act
        actual = self.sut.map_cloud_to_local(self._DEFAULT_CLOUD_ROOT, [cloud_folder], [local_folder])
        # assert
        self.assertSetEqual(actual, set([self._CLOUD_FOLDER_PATH]))

    def test_merged_items_when_local_and_cloud_have_differnt_folders(self):
        local_folder1 = self.__create_local_folder('dir1')
        local_folder2 = self.__create_local_folder('Dir2')
        cloud_folder = self.__create_cloud_folder()
        # act
        actual = self.sut.map_cloud_to_local(self._DEFAULT_CLOUD_ROOT, [cloud_folder], [local_folder1, local_folder2])
        # assert
        self.assertSetEqual(actual, set([self._CLOUD_FOLDER_PATH, '/root/dir1', '/root/Dir2']))

    @staticmethod
    def __create_cloud_folder(name=_FOLDER_NAME,
                              lower_path=_CLOUD_LOWER_FOLDER_PATH,
                              display_path=_CLOUD_FOLDER_PATH):
        return CloudFolderMetadata(lower_path, name, lower_path, display_path)

    @staticmethod
    def __create_local_folder(display_path=_FOLDER_NAME):
        return display_path
