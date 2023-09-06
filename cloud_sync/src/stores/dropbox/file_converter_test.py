import datetime
import unittest
from unittest.mock import Mock
import logging
import dropbox

from src.stores.dropbox.file_converter import DropboxFileConverter
from src.stores.models import CloudFileMetadata, CloudFolderMetadata


class DropboxFileConverterTests(unittest.TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self.sut = DropboxFileConverter(logger)

    def test_2_files_when_converterd_gfiles_with_2_files_in_the_root(self):
        dbx_file1 = self.__create_DropboxFile('f1.pdf', 'f1.pdf', 'f1.pdf')
        dbx_file2 = self.__create_DropboxFile('F2.pdf', 'F2.pdf', 'f2.pdf')
        expected1 = self.__create_CloudFile('f1.pdf', 'f1.pdf', 'f1.pdf')
        expected2 = self.__create_CloudFile('F2.pdf', 'F2.pdf', 'f2.pdf')
        # act
        actual = self.sut.convert_dropbox_entries_to_cloud([dbx_file1, dbx_file2])
        # assert
        self.assertEqual(actual.folders, [])
        self.assertEqual(actual.files, [expected1, expected2])

    def test_2_files_when_converterd_gfiles_with_2_files_in_the_subfolder(self):
        dbx_file1 = self.__create_DropboxFile('f1.pdf', '/Path/f1.pdf', '/path/f1.pdf')
        dbx_file2 = self.__create_DropboxFile('F2.pdf', '/Path/F2.pdf', '/path/f2.pdf')
        expected1 = self.__create_CloudFile('f1.pdf', '/Path/f1.pdf', '/path/f1.pdf')
        expected2 = self.__create_CloudFile('F2.pdf', '/Path/F2.pdf', '/path/f2.pdf')
        # act
        actual = self.sut.convert_dropbox_entries_to_cloud([dbx_file1, dbx_file2])
        # assert
        self.assertEqual(actual.folders, [])
        self.assertEqual(actual.files, [expected1, expected2])

    def test_result_contains_converted_dropbox_file(self):
        dbx_md = self.__create_DropboxFile()
        expected = self.__create_CloudFile()
        # act
        actual = self.sut.convert_DropboxFile_to_CloudFile(dbx_md)
        # assert
        self.assertEqual(actual, expected)

    def test_result_contains_converted_dropbox_folder(self):
        dbx_dir = self.__create_DropboxFolder()
        expected = self.__create_CloudFolder()
        # act
        actual = self.sut.convert_DropboxFolder_to_CloudFolder(dbx_dir)
        # assert
        self.assertEqual(actual, expected)

    DEFAULT_NAME = 'File1.pdf'
    DEFAULT_PATH_DISPLAY = '/Path/File1.pdf'
    DEFAULT_PATH_LOWER = '/path/file1.pdf'

    @staticmethod
    def __create_DropboxFile(name=DEFAULT_NAME, path_display=DEFAULT_PATH_DISPLAY, path_lower=DEFAULT_PATH_LOWER):
        result = Mock(dropbox.files.FileMetadata)
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
    def __create_DropboxFolder(name='SubPath', path_display='/Path/SubPath', path_lower='/path/subpath'):
        result = Mock(dropbox.files.FolderMetadata)
        result.id = 'id:AABBCC'
        result.path_display = path_display
        result.path_lower = path_lower
        result.name = name
        return result

    @staticmethod
    def __create_CloudFolder(name='SubPath', cloud_path='/Path/SubPath', path_lower='/path/subpath'):
        return CloudFolderMetadata(path_lower, name, path_lower, cloud_path)
