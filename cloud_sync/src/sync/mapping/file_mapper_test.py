import datetime
import unittest
from unittest.mock import Mock
import logging
from src.sync.mapping.file_mapper import FileMapper
from src.sync.models import FileSyncAction
from src.sync.file_sync_action_provider import FileSyncActionProvider
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class FileMapperTests(unittest.TestCase):
    _LOCAL_FILE_PATH = 'C:\\Path\\CloudRoot\\sub\\f.txt'
    _CLOUD_FOLDER_PATH = '/Sub'
    _CLOUD_FILE_PATH = '/Sub/f.txt'
    _FILE_NAME = 'f.txt'
    _FILE_CONTENT = '111'

    def setUp(self):
        logger = Mock(logging.Logger)
        self._sync_action_provider = Mock(FileSyncActionProvider)
        self.sut = FileMapper(self._sync_action_provider, logger)

    def test_empty_lists_when_local_and_cloud_files_match(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file()
        # act
        actual = self.sut.map_cloud_to_local([cloud_file], [local_file])
        # assert
        self.assertListEqual(actual.download, [])
        self.assertListEqual(actual.upload, [])

    def test_file_to_download_when_local_storage_has_no_file(self):
        cloud_file = self.__create_cloud_file()
        # act
        actual = self.sut.map_cloud_to_local([cloud_file], [])
        # assert
        self.assertListEqual(actual.download, [cloud_file])
        self.assertListEqual(actual.upload, [])

    def test_empty_lists_when_both_files_exist_and_file_comparer_returns_skip(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(3)
        self._sync_action_provider.get_sync_action = Mock(return_value=FileSyncAction.SKIP)
        # act
        actual = self.sut.map_cloud_to_local([cloud_file], [local_file])
        # assert
        self.assertListEqual(actual.download, [])
        self.assertListEqual(actual.upload, [])

    def test_empty_lists_when_both_files_exist_and_file_comparer_returns_conflict(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(3)
        self._sync_action_provider.get_sync_action = Mock(return_value=FileSyncAction.CONFLICT)
        # act
        actual = self.sut.map_cloud_to_local([cloud_file], [local_file])
        # assert
        self.assertListEqual(actual.download, [])
        self.assertListEqual(actual.upload, [])

    def test_file_to_download_when_both_files_exist_and_file_comparer_returns_download(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file()
        self._sync_action_provider.get_sync_action = Mock(return_value=FileSyncAction.DOWNLOAD)
        # act
        actual = self.sut.map_cloud_to_local([cloud_file], [local_file])
        # assert
        self.assertListEqual(actual.download, [cloud_file])
        self.assertListEqual(actual.upload, [])

    def test_file_to_upload_when_both_files_present_and_file_comparer_returns_upload(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file()
        self._sync_action_provider.get_sync_action = Mock(return_value=FileSyncAction.UPLOAD)
        # act
        actual = self.sut.map_cloud_to_local([cloud_file], [local_file])
        # assert
        self.assertListEqual(actual.download, [])
        self.assertListEqual(actual.upload, [local_file])

    def test_files_to_download_when_local_files_with_the_same_name_in_different_folders_do_not_exist(self):
        cloud_file_root = self.__create_cloud_file()
        cloud_file_subfolder = self.__create_cloud_file(cloud_file_path='/Sub/2/f.txt')
        cloud_list = [cloud_file_root, cloud_file_subfolder]
        # act
        actual = self.sut.map_cloud_to_local(cloud_list, [])
        # assert
        self.assertListEqual(
            actual.download, [cloud_file_root, cloud_file_subfolder])
        self.assertListEqual(actual.upload, [])

    def test_files_to_upload_when_cloud_files_with_the_same_name_in_different_folders_do_not_exist(self):
        local_file_root = self.__create_local_file()
        local_file_subfolder = self.__create_local_file(
            cloud_file_path='/Sub/2/f.txt', local_file_path='c:\\path\\sub\\2\\f.txt')
        local_list = [local_file_root, local_file_subfolder]
        # act
        actual = self.sut.map_cloud_to_local([], local_list)
        # assert
        self.assertListEqual(actual.download, [])
        self.assertListEqual(actual.upload, [local_file_root, local_file_subfolder])

    def test_file_to_upload_when_no_file_in_the_cloud(self):
        local_file = self.__create_local_file()
        # act
        actual = self.sut.map_cloud_to_local([], [local_file])
        # assert
        self.assertListEqual(actual.download, [])
        self.assertListEqual(actual.upload, [local_file])

    def __create_local_file(self, modified_day=1, size=2000,
                            cloud_file_path=_CLOUD_FILE_PATH, local_file_path=_LOCAL_FILE_PATH):
        return LocalFileMetadata(
            self._FILE_NAME, cloud_file_path,
            datetime.datetime(2023, 8, modified_day, 20, 14, 14),
            size, local_file_path)

    def __create_cloud_file(self, modified_day=1, size=2000, cloud_file_path=_CLOUD_FILE_PATH):
        return CloudFileMetadata(
            self._FILE_NAME, cloud_file_path,
            datetime.datetime(2023, 8, modified_day, 20, 14, 14),
            size, cloud_file_path, '123321')