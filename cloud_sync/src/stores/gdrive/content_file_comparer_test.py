import datetime
import unittest
from unittest.mock import Mock
import logging
from src.stores.gdrive.content_file_comparer import ContentFileComparer
from src.stores.file_comparer import FileAction, FileComparison
from src.stores.cloud_store import CloudStore
from src.stores.local.file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, LocalFileMetadata


class ContentFileComparerTests(unittest.TestCase):
    _LOCAL_FILE_PATH = 'C:\\Path\\CloudRoot\\sub\\f.txt'
    _CLOUD_FOLDER_PATH = '/Sub'
    _CLOUD_FILE_PATH = '/Sub/f.txt'
    _FILE_NAME = 'f.txt'
    _FILE_CONTENT = '111'

    def setUp(self):
        logger = Mock(logging.Logger)
        self._local_store = Mock(LocalFileStore)
        self._cloud_store = Mock(CloudStore)
        self.sut = ContentFileComparer(
            self._local_store, self._cloud_store, logger)

    def test_skip_when_files_match_by_metadata(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file()
        # act
        actual = self.sut.get_file_action(local_file, cloud_file)
        self.assertEqual(actual, FileAction.SKIP)

    def test_skip_when_files_match_by_metadata_and_different_by_content(self):
        local_file = self.__create_local_file()
        self.__mock_local_read(local_file)
        cloud_file = self.__create_cloud_file()
        self.__mock_cloud_read(cloud_file, '222')
        # act
        actual = self.sut.get_file_action(local_file, cloud_file)
        self.assertEqual(actual, FileAction.SKIP)

    def test_conflict_when_files_different_by_name(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(name='dif_name')
        # act
        actual = self.sut.get_file_action(local_file, cloud_file)
        self.assertEqual(actual, FileAction.CONFLICT)

    def test_conflict_when_files_different_by_size_but_equal_by_date(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(size=1000)
        # act
        actual = self.sut.get_file_action(local_file, cloud_file)
        self.assertEqual(actual, FileAction.CONFLICT)

    def test_download_when_files_different_by_size_and_cloud_file_is_newer(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(modified_day=2, size=1000)
        # act
        actual = self.sut.get_file_action(local_file, cloud_file)
        self.assertEqual(actual, FileAction.DOWNLOAD)

    def test_upload_when_files_different_by_size_and_local_file_is_newer(self):
        local_file = self.__create_local_file(modified_day=2, size=1000)
        cloud_file = self.__create_cloud_file()
        # act
        actual = self.sut.get_file_action(local_file, cloud_file)
        self.assertEqual(actual, FileAction.UPLOAD)

    def test_skip_when_files_equal_by_content_and_cloud_file_is_newer(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(modified_day=2)
        self.__mock_local_read(local_file)
        self.__mock_cloud_read(cloud_file)
        # act
        actual = self.sut.get_file_action(local_file, cloud_file)
        self.assertEqual(actual, FileAction.SKIP)

    def test_skip_when_files_equal_by_content_and_local_file_is_newer(self):
        local_file = self.__create_local_file(modified_day=2)
        cloud_file = self.__create_cloud_file()
        self.__mock_local_read(local_file)
        self.__mock_cloud_read(cloud_file)
        # act
        actual = self.sut.get_file_action(local_file, cloud_file)
        self.assertEqual(actual, FileAction.SKIP)

    def test_download_when_files_equal_by_content_and_cloud_file_is_newer(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(modified_day=2)
        self.__mock_local_read(local_file)
        self.__mock_cloud_read(cloud_file, 'another_content')
        # act
        actual = self.sut.get_file_action(local_file, cloud_file)
        self.assertEqual(actual, FileAction.DOWNLOAD)

    def test_upload_when_files_equal_by_content_and_local_file_is_newer(self):
        local_file = self.__create_local_file(modified_day=2)
        cloud_file = self.__create_cloud_file()
        self.__mock_local_read(local_file)
        self.__mock_cloud_read(cloud_file, 'another_content')
        # act
        actual = self.sut.get_file_action(local_file, cloud_file)
        self.assertEqual(actual, FileAction.UPLOAD)

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

    def __mock_cloud_read(self, file: CloudFileMetadata, content=_FILE_CONTENT):
        self._cloud_store.read = Mock(return_value=(content, file))

    def __mock_local_read(self, file: LocalFileMetadata, content=_FILE_CONTENT):
        self._local_store.read = Mock(return_value=(content, file))
