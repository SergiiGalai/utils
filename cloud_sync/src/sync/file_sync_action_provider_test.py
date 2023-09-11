import datetime
import unittest
from unittest.mock import Mock
import logging
from src.sync.file_sync_action_provider import FileSyncAction, FileSyncActionProvider
from src.sync.comparison.file_content_comparer import FileContentComparer
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class FileSyncActionProviderTests(unittest.TestCase):
    _LOCAL_FILE_PATH = 'C:\\Path\\CloudRoot\\sub\\f.txt'
    _CLOUD_FOLDER_PATH = '/Sub'
    _CLOUD_FILE_PATH = '/Sub/f.txt'
    _FILE_NAME = 'f.txt'
    _FILE_CONTENT = '111'

    def setUp(self):
        logger = Mock(logging.Logger)
        self._content_comparer = Mock(FileContentComparer)
        self.sut = FileSyncActionProvider(self._content_comparer, logger)

    def test_skip_when_files_match_by_metadata(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file()
        # act
        actual = self.sut.get_sync_action(local_file, cloud_file)
        self.assertEqual(actual, FileSyncAction.SKIP)

    def test_skip_when_files_match_by_metadata_and_different_by_content(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file()
        self.__mock_content_comparer(False)
        # act
        actual = self.sut.get_sync_action(local_file, cloud_file)
        self.assertEqual(actual, FileSyncAction.SKIP)

    def test_conflict_when_files_different_by_name(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(name='dif_name')
        # act
        actual = self.sut.get_sync_action(local_file, cloud_file)
        self.assertEqual(actual, FileSyncAction.CONFLICT)

    def test_conflict_when_files_different_by_size_but_equal_by_date(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(size=1000)
        # act
        actual = self.sut.get_sync_action(local_file, cloud_file)
        self.assertEqual(actual, FileSyncAction.CONFLICT)

    def test_download_when_files_different_by_size_and_cloud_file_is_newer(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(modified_day=2, size=1000)
        # act
        actual = self.sut.get_sync_action(local_file, cloud_file)
        self.assertEqual(actual, FileSyncAction.DOWNLOAD)

    def test_upload_when_files_different_by_size_and_local_file_is_newer(self):
        local_file = self.__create_local_file(modified_day=2, size=1000)
        cloud_file = self.__create_cloud_file()
        # act
        actual = self.sut.get_sync_action(local_file, cloud_file)
        self.assertEqual(actual, FileSyncAction.UPLOAD)

    def test_skip_when_files_equal_by_content_and_cloud_file_is_newer(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(modified_day=2)
        self.__mock_content_comparer(True)
        # act
        actual = self.sut.get_sync_action(local_file, cloud_file)
        self.assertEqual(actual, FileSyncAction.SKIP)

    def test_skip_when_files_equal_by_content_and_local_file_is_newer(self):
        local_file = self.__create_local_file(modified_day=2)
        cloud_file = self.__create_cloud_file()
        self.__mock_content_comparer(True)
        # act
        actual = self.sut.get_sync_action(local_file, cloud_file)
        self.assertEqual(actual, FileSyncAction.SKIP)

    def test_download_when_files_equal_by_content_and_cloud_file_is_newer(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(modified_day=2)
        self.__mock_content_comparer(False)
        # act
        actual = self.sut.get_sync_action(local_file, cloud_file)
        self.assertEqual(actual, FileSyncAction.DOWNLOAD)

    def test_upload_when_files_equal_by_content_and_local_file_is_newer(self):
        local_file = self.__create_local_file(modified_day=2)
        cloud_file = self.__create_cloud_file()
        self.__mock_content_comparer(False)
        # act
        actual = self.sut.get_sync_action(local_file, cloud_file)
        self.assertEqual(actual, FileSyncAction.UPLOAD)

    def __create_local_file(self, modified_day=1, size=2000, name=_FILE_NAME):
        return LocalFileMetadata(
            name, self._CLOUD_FILE_PATH,
            datetime.datetime(2023, 8, modified_day, 20, 14, 14),
            size, self._LOCAL_FILE_PATH)

    def __create_cloud_file(self, modified_day=1, size=2000, name=_FILE_NAME):
        return CloudFileMetadata(
            name, self._CLOUD_FILE_PATH,
            datetime.datetime(2023, 8, modified_day, 20, 14, 14),
            size, self._CLOUD_FILE_PATH, '123321')

    def __mock_content_comparer(self, are_equal: bool):
        self._content_comparer.are_equal = Mock(return_value=are_equal)