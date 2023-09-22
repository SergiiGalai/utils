from unittest import TestCase
from unittest.mock import Mock
import logging
from src.sync.file_sync_action_provider import FileSyncAction, FileSyncActionProvider
from src.sync.comparison.file_content_comparer import FileContentComparer
from tests.file_metadata import create_local_file, create_cloud_file


class TestFileSyncActionProvider(TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self._content_comparer = Mock(FileContentComparer)
        self._sut = FileSyncActionProvider(self._content_comparer, logger)
        self._local_file = create_local_file()
        self._cloud_file = create_cloud_file()

    def test_skip_when_files_equal_by_metadata(self):
        actual = self._sut.get_sync_action(self._local_file, self._cloud_file)
        assert actual == FileSyncAction.SKIP

    def test_skip_when_files_equal_by_metadata_but_different_by_content(self):
        self.__mock_content_comparer(False)
        actual = self._sut.get_sync_action(self._local_file, self._cloud_file)
        assert actual == FileSyncAction.SKIP

    def test_conflict_when_files_different_by_name(self):
        cloud_file = create_cloud_file(name='dif_name')
        actual = self._sut.get_sync_action(self._local_file, cloud_file)
        assert actual == FileSyncAction.CONFLICT

    def test_conflict_when_files_different_by_size_but_equal_by_date(self):
        cloud_file = create_cloud_file(size=1000)
        actual = self._sut.get_sync_action(self._local_file, cloud_file)
        assert actual == FileSyncAction.CONFLICT

    def test_download_when_files_different_by_size_and_cloud_file_is_newer(self):
        cloud_file = create_cloud_file(modified_day=2, size=1000)
        actual = self._sut.get_sync_action(self._local_file, cloud_file)
        assert actual == FileSyncAction.DOWNLOAD

    def test_upload_when_files_different_by_size_and_local_file_is_newer(self):
        local_file = create_local_file(modified_day=2, size=1000)
        actual = self._sut.get_sync_action(local_file, self._cloud_file)
        assert actual == FileSyncAction.UPLOAD

    def test_skip_when_files_equal_by_content_and_cloud_file_is_newer(self):
        cloud_file = create_cloud_file(modified_day=2)
        self.__mock_content_comparer(True)
        # act
        actual = self._sut.get_sync_action(self._local_file, cloud_file)
        assert actual == FileSyncAction.SKIP

    def test_skip_when_files_equal_by_content_and_local_file_is_newer(self):
        local_file = create_local_file(modified_day=2)
        self.__mock_content_comparer(True)
        # act
        actual = self._sut.get_sync_action(local_file, self._cloud_file)
        assert actual == FileSyncAction.SKIP

    def test_download_when_files_equal_by_content_and_cloud_file_is_newer(self):
        cloud_file = create_cloud_file(modified_day=2)
        self.__mock_content_comparer(False)
        # act
        actual = self._sut.get_sync_action(self._local_file, cloud_file)
        assert actual == FileSyncAction.DOWNLOAD

    def test_upload_when_files_equal_by_content_and_local_file_is_newer(self):
        local_file = create_local_file(modified_day=2)
        self.__mock_content_comparer(False)
        # act
        actual = self._sut.get_sync_action(local_file, self._cloud_file)
        assert actual == FileSyncAction.UPLOAD

    def __mock_content_comparer(self, are_equal: bool):
        self._content_comparer.are_equal.return_value = are_equal
