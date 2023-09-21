import datetime
from unittest import TestCase
from unittest.mock import Mock
import logging
from src.sync.mapping.file_mapper import FileMapper
from src.sync.models import FileSyncAction
from src.sync.file_sync_action_provider import FileSyncActionProvider
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class TestFileMapper(TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self._sync_action_provider = Mock(FileSyncActionProvider)
        self._sut = FileMapper(self._sync_action_provider, logger)

    def test_empty_lists_when_files_match(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file()
        # act
        actual = self._sut.map_cloud_to_local([cloud_file], [local_file])
        assert actual.download == []
        assert actual.upload == []

    def test_file_to_upload_when_no_file_in_the_cloud(self):
        local_file = self.__create_local_file()
        # act
        actual = self._sut.map_cloud_to_local([], [local_file])
        assert actual.download == []
        assert actual.upload == [local_file]

    def test_file_to_download_when_no_file_locally(self):
        cloud_file = self.__create_cloud_file()
        # act
        actual = self._sut.map_cloud_to_local([cloud_file], [])
        assert actual.download == [cloud_file]
        assert actual.upload == []

    def test_empty_lists_when_different_files_but_skip_action(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(3)
        self._sync_action_provider.get_sync_action.return_value = FileSyncAction.SKIP
        # act
        actual = self._sut.map_cloud_to_local([cloud_file], [local_file])
        assert actual.download == []
        assert actual.upload == []

    def test_empty_lists_when_different_files_but_conflict_action(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file(3)
        self._sync_action_provider.get_sync_action.return_value = FileSyncAction.CONFLICT
        # act
        actual = self._sut.map_cloud_to_local([cloud_file], [local_file])
        assert actual.download == []
        assert actual.upload == []

    def test_file_to_download_when_files_equal_but_download_action(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file()
        self._sync_action_provider.get_sync_action.return_value = FileSyncAction.DOWNLOAD
        # act
        actual = self._sut.map_cloud_to_local([cloud_file], [local_file])
        assert actual.download == [cloud_file]
        assert actual.upload == []

    def test_file_to_upload_when_files_equal_but_upload_action(self):
        local_file = self.__create_local_file()
        cloud_file = self.__create_cloud_file()
        self._sync_action_provider.get_sync_action.return_value = FileSyncAction.UPLOAD
        # act
        actual = self._sut.map_cloud_to_local([cloud_file], [local_file])
        assert actual.download == []
        assert actual.upload == [local_file]

    def test_files_to_download_when_local_files_with_the_same_name_in_different_folders_do_not_exist(self):
        cloud_file_root = self.__create_cloud_file()
        cloud_file_subfolder = self.__create_cloud_file(cloud_file_path='/Sub/2/f.txt')
        # act
        actual = self._sut.map_cloud_to_local([cloud_file_root, cloud_file_subfolder], [])
        assert actual.download == [cloud_file_root, cloud_file_subfolder]
        assert actual.upload == []

    def test_files_to_upload_when_cloud_files_with_the_same_name_in_different_folders_do_not_exist(self):
        local_file_root = self.__create_local_file()
        local_file_subfolder = self.__create_local_file(
            cloud_file_path='/Sub/2/f.txt',
            local_file_path='c:\\path\\sub\\2\\f.txt')
        # act
        actual = self._sut.map_cloud_to_local([], [local_file_root, local_file_subfolder])
        assert actual.download == []
        assert actual.upload == [local_file_root, local_file_subfolder]

    @staticmethod
    def __create_local_file(modified_day=1, size=2000,
                            cloud_file_path='/Sub/f.txt',
                            local_file_path='C:\\Path\\CloudRoot\\sub\\f.txt'):
        return LocalFileMetadata(
            'f.txt', cloud_file_path,
            datetime.datetime(2023, 8, modified_day, 20, 14, 14),
            size, local_file_path,
            'application/unknown')

    @staticmethod
    def __create_cloud_file(modified_day=1, size=2000,
                            cloud_file_path='/Sub/f.txt'):
        return CloudFileMetadata(
            'f.txt', cloud_file_path,
            datetime.datetime(2023, 8, modified_day, 20, 14, 14),
            size, cloud_file_path, '123321')
