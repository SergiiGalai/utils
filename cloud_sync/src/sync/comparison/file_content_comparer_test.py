import datetime
from unittest import TestCase
from unittest.mock import Mock
import logging
from src.sync.comparison.file_content_comparer import FileStoreContentComparer
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.local.local_file_store import LocalFileStore
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata

class TestFileStoreContentComparer(TestCase):
    _CLOUD_FILE_PATH = '/Sub/f.txt'
    _FILE_CONTENT = '111'

    def setUp(self):
        logger = Mock(logging.Logger)
        self._cloud_store = Mock(CloudStore)
        self._local_store = Mock(LocalFileStore)
        self._sut = FileStoreContentComparer(self._local_store, self._cloud_store, logger)

    def test_not_equal_when_files_different_by_content(self):
        local_file = self.__create_local_file()
        self.__mock_local_read(local_file)
        cloud_file = self.__create_cloud_file()
        self.__mock_cloud_read(cloud_file, '222')
        # act
        actual = self._sut.are_equal(local_file, cloud_file)
        assert actual == False

    def test_equal_when_files_have_the_same_content(self):
        local_file = self.__create_local_file()
        self.__mock_local_read(local_file)
        cloud_file = self.__create_cloud_file()
        self.__mock_cloud_read(cloud_file)
        # act
        actual = self._sut.are_equal(local_file, cloud_file)
        assert actual == True

    def __create_local_file(self):
        return LocalFileMetadata(
            'f.txt', self._CLOUD_FILE_PATH,
            datetime.datetime(2023, 2, 1, 20, 0, 0),
            2000, 'C:\\Path\\CloudRoot\\sub\\f.txt',
            'application/unknown')

    def __create_cloud_file(self):
        return CloudFileMetadata(
            'f.txt', self._CLOUD_FILE_PATH,
            datetime.datetime(2023, 2, 1, 20, 0, 0),
            2000, self._CLOUD_FILE_PATH, '123321')

    def __mock_cloud_read(self, file: CloudFileMetadata, content=_FILE_CONTENT):
        self._cloud_store.read.return_value = (content, file)

    def __mock_local_read(self, file: LocalFileMetadata, content=_FILE_CONTENT):
        self._local_store.read.return_value = (content, file)
