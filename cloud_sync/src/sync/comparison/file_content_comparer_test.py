from unittest import TestCase
from unittest.mock import Mock
import logging
from src.sync.comparison.file_content_comparer import FileStoreContentComparer
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.local.local_file_store import LocalFileStore
from tests.file_metadata import create_local_file, create_cloud_file


class TestFileStoreContentComparer(TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self._cloud_store = Mock(CloudStore)
        self._local_store = Mock(LocalFileStore)
        self._sut = FileStoreContentComparer(self._local_store, self._cloud_store, logger)

    def test_not_equal_when_files_different_by_content(self):
        local_file = create_local_file()
        self.__mock_local_read()
        cloud_file = create_cloud_file()
        self.__mock_cloud_read('222')
        # act
        actual = self._sut.are_equal(local_file, cloud_file)
        assert actual == False

    def test_equal_when_files_have_the_same_content(self):
        local_file = create_local_file()
        self.__mock_local_read()
        cloud_file = create_cloud_file()
        self.__mock_cloud_read()
        # act
        actual = self._sut.are_equal(local_file, cloud_file)
        assert actual == True

    _FILE_CONTENT = '111'

    def __mock_cloud_read(self, content=_FILE_CONTENT):
        self._cloud_store.read_content.return_value = content

    def __mock_local_read(self, content=_FILE_CONTENT):
        self._local_store.read_content.return_value = content
