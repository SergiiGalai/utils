import datetime
import unittest
from unittest.mock import Mock
import logging
from pydrive.drive import GoogleDriveFile

from src.sync.stores.gdrive.file_converter import GoogleDriveFileConverter
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata


class GoogleDriveFileConverterTests(unittest.TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self.sut = GoogleDriveFileConverter(logger)

    def test_2_files_when_converterd_gfiles_with_2_files_in_the_root(self):
        gFile1 = self.__create_drive_file(id='1', name='f1.pdf')
        gFile2 = self.__create_drive_file(id='2', name='F2.pdf')
        expected1 = self.__create_cloud_file('/f1.pdf', 'f1.pdf', '1')
        expected2 = self.__create_cloud_file('/F2.pdf', 'F2.pdf', '2')
        # act
        actual = self.sut.convert_GoogleDriveFiles_to_FileMetadatas([gFile1, gFile2])
        # assert
        self.assertEqual(actual.folders, [])
        self.assertEqual(actual.files, [expected1, expected2])

    def test_2_files_when_converterd_gfiles_with_2_files_in_the_subfolder(self):
        gFile1 = self.__create_drive_file(id='1', name='f1.pdf')
        gFile2 = self.__create_drive_file(id='2', name='F2.pdf')
        expected1 = self.__create_cloud_file('/Root/Subpath/f1.pdf', 'f1.pdf', '1')
        expected2 = self.__create_cloud_file('/Root/Subpath/F2.pdf', 'F2.pdf', '2')
        # act
        actual = self.sut.convert_GoogleDriveFiles_to_FileMetadatas([gFile1, gFile2], '/Root/Subpath')
        # assert
        self.assertEqual(actual.folders, [])
        self.assertEqual(actual.files, [expected1, expected2])

    def test_CloudFileMetadata_when_converted_gfile_with_empty_cloud_path(self):
        gFile = self.__create_drive_file()
        expected = self.__create_cloud_file('/File1.pdf')
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFile(gFile)
        # assert
        self.assertEqual(actual, expected)

    def test_CloudFileMetadata_when_converted_gfile_with_slash_as_cloud_path(self):
        gFile = self.__create_drive_file()
        expected = self.__create_cloud_file('/File1.pdf')
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFile(gFile, '/')
        # assert
        self.assertEqual(actual, expected)

    def test_CloudFileMetadata_when_converted_gfile_with_subpath(self):
        gFile = self.__create_drive_file()
        expected = self.__create_cloud_file('/Root/File1.pdf')
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFile(gFile, '/Root')
        # assert
        self.assertEqual(actual, expected)

    def test_CloudFileMetadata_when_converted_gfile_with_level2_subpath(self):
        gFile = self.__create_drive_file()
        expected = self.__create_cloud_file('/Root/sub2/File1.pdf')
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFile(gFile, '/Root/sub2')
        # assert
        self.assertEqual(actual, expected)

    def test_CloudFileMetadata_with_null_file_size_when_gfile_is_a_shortcut(self):
        gFile = self.__create_drive_file('application/vnd.google-apps.shortcut')
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFile(gFile)
        # assert
        self.assertEqual(actual.size, 0)

    def test_CloudFolderMetadata_when_gFolder_passed(self):
        gFile = self.__create_drive_folder()
        expected = self.__create_cloud_folder()
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFolderMetadata(gFile, '/Root')
        # assert
        self.assertEqual(actual, expected)

    DEFAULT_ID = '1C7Vb'
    FILE_NAME = 'File1.pdf'
    ROOT_PATH = '/Root'

    @staticmethod
    def __create_drive_file(mimeType='application/pdf', name=FILE_NAME, id=DEFAULT_ID):
        return GoogleDriveFile(metadata={
            'id': id, 'title': name,
            'modifiedDate': '2023-08-15T14:27:44.000Z',
            'mimeType': mimeType, 'fileSize': '12345'})

    @staticmethod
    def __create_cloud_file(cloud_path='/Root/File1.pdf', name=FILE_NAME, id=DEFAULT_ID):
        return CloudFileMetadata(name, cloud_path,
                                 datetime.datetime(2023, 8, 15, 14, 27, 44),
                                 12345, id, '0')

    @staticmethod
    def __create_drive_folder(name='Subpath', id=DEFAULT_ID):
        return GoogleDriveFile(metadata={
            'id': id, 'title': name,
            'mimeType': 'application/vnd.google-apps.folder'})

    @staticmethod
    def __create_cloud_folder(name='Subpath', lower_path='/root/subpath', cloud_path='/Root/Subpath', id=DEFAULT_ID):
        return CloudFolderMetadata(id, name, lower_path, cloud_path)
