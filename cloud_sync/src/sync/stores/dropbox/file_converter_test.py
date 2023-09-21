import datetime
from unittest import TestCase
from unittest.mock import Mock
import logging
import dropbox

from src.sync.stores.dropbox.file_converter import DropboxFileConverter
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata


class TestDropboxFileConverter(TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self._sut = DropboxFileConverter(logger)

    def test_2_files_when_converterd_gfiles_with_2_files_in_the_root(self):
        dbx_file1 = self.__create_DropboxFile('f1.pdf', '/f1.pdf', '/f1.pdf')
        dbx_file2 = self.__create_DropboxFile('F2.pdf', '/F2.pdf', '/f2.pdf')
        expected1 = self.__create_CloudFile('f1.pdf', '/f1.pdf', '/f1.pdf')
        expected2 = self.__create_CloudFile('F2.pdf', '/F2.pdf', '/f2.pdf')
        # act
        actual = self._sut.convert_dropbox_entries_to_cloud([dbx_file1, dbx_file2])
        assert actual.folders == []
        assert actual.files == [expected1, expected2]

    def test_2_files_when_converterd_gfiles_with_2_files_in_the_subfolder(self):
        dbx_file1 = self.__create_DropboxFile('f1.pdf', '/Root/f1.pdf', '/root/f1.pdf')
        dbx_file2 = self.__create_DropboxFile('F2.pdf', '/Root/F2.pdf', '/root/f2.pdf')
        expected1 = self.__create_CloudFile('f1.pdf', '/Root/f1.pdf', '/root/f1.pdf')
        expected2 = self.__create_CloudFile('F2.pdf', '/Root/F2.pdf', '/root/f2.pdf')
        # act
        actual = self._sut.convert_dropbox_entries_to_cloud([dbx_file1, dbx_file2])
        assert actual.folders == []
        assert actual.files == [expected1, expected2]

    def test_result_contains_converted_dropbox_file(self):
        dbx_md = self.__create_DropboxFile()
        expected = self.__create_CloudFile()
        # act
        actual = self._sut.convert_DropboxFile_to_CloudFile(dbx_md)
        assert actual == expected

    def test_result_contains_converted_dropbox_folder(self):
        dbx_dir = self.__create_DropboxFolder()
        expected = self.__create_CloudFolder()
        # act
        actual = self._sut.convert_DropboxFolder_to_CloudFolder(dbx_dir)
        assert actual == expected

    DEFAULT_NAME = 'File1.pdf'
    DEFAULT_PATH_DISPLAY = '/Root/File1.pdf'
    DEFAULT_PATH_LOWER = '/root/file1.pdf'

    @staticmethod
    def __create_DropboxFile(name=DEFAULT_NAME, path_display=DEFAULT_PATH_DISPLAY, path_lower=DEFAULT_PATH_LOWER):
        result = Mock(dropbox.files.FileMetadata) # type: ignore
        result.id = 'id:AABBCC'
        result.name = name
        result.path_display = path_display
        result.path_lower = path_lower
        result.client_modified = datetime.datetime(2017, 6, 13, 20, 16, 8)
        result.content_hash = '1234567890'
        result.size = 12345
        return result

    @staticmethod
    def __create_CloudFile(name=DEFAULT_NAME,
                           cloud_path=DEFAULT_PATH_DISPLAY, path_lower=DEFAULT_PATH_LOWER):
        return CloudFileMetadata(
            name, cloud_path,
            datetime.datetime(2017, 6, 13, 20, 16, 8), 12345,
            path_lower, '1234567890')

    @staticmethod
    def __create_DropboxFolder(name='SubPath', path_display='/Root/SubPath', path_lower='/root/subpath'):
        result = Mock(dropbox.files.FolderMetadata) # type: ignore
        result.id = 'id:AABBCC'
        result.path_display = path_display
        result.path_lower = path_lower
        result.name = name
        return result

    @staticmethod
    def __create_CloudFolder(name='SubPath', cloud_path='/Root/SubPath', path_lower='/root/subpath'):
        return CloudFolderMetadata(path_lower, name, path_lower, cloud_path)
