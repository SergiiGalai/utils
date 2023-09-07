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
        gFile1 = self._createGoogleDriveFile(id='1', name='f1.pdf')
        gFile2 = self._createGoogleDriveFile(id='2', name='F2.pdf')
        expected1 = self._createCloudFileMetadata('f1.pdf', 'f1.pdf', '1')
        expected2 = self._createCloudFileMetadata('F2.pdf', 'F2.pdf', '2')
        # act
        actual = self.sut.convert_GoogleDriveFiles_to_FileMetadatas([gFile1, gFile2])
        # assert
        self.assertEqual(actual.folders, [])
        self.assertEqual(actual.files, [expected1, expected2])

    def test_2_files_when_converterd_gfiles_with_2_files_in_the_subfolder(self):
        gFile1 = self._createGoogleDriveFile(id='1', name='f1.pdf')
        gFile2 = self._createGoogleDriveFile(id='2', name='F2.pdf')
        expected1 = self._createCloudFileMetadata('/folder/folder2/f1.pdf', 'f1.pdf', '1')
        expected2 = self._createCloudFileMetadata('/folder/folder2/F2.pdf', 'F2.pdf', '2')
        # act
        actual = self.sut.convert_GoogleDriveFiles_to_FileMetadatas([gFile1, gFile2], '/folder/folder2')
        # assert
        self.assertEqual(actual.folders, [])
        self.assertEqual(actual.files, [expected1, expected2])

    def test_CloudFileMetadata_when_converted_gfile_with_file_size(self):
        gFile = self._createGoogleDriveFile()
        expected = self._createCloudFileMetadata()
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFile(gFile)
        # assert
        self.assertEqual(actual, expected)

    def test_CloudFileMetadata_when_converted_gfile_with_root_subpath(self):
        gFile = self._createGoogleDriveFile()
        expected = self._createCloudFileMetadata('/File1.pdf')
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFile(gFile, '/')
        # assert
        self.assertEqual(actual, expected)

    def test_CloudFileMetadata_when_converted_gfile_with_subpath(self):
        gFile = self._createGoogleDriveFile()
        expected = self._createCloudFileMetadata('/sub/File1.pdf')
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFile(gFile, '/sub')
        # assert
        self.assertEqual(actual, expected)

    def test_CloudFileMetadata_when_converted_gfile_with_level2_subpath(self):
        gFile = self._createGoogleDriveFile()
        expected = self._createCloudFileMetadata('/sub/sub2/File1.pdf')
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFile(gFile, '/sub/sub2')
        # assert
        self.assertEqual(actual, expected)

    def test_CloudFileMetadata_with_null_file_size_when_gfile_is_a_shortcut(self):
        gFile = self._createGoogleDriveFile('application/vnd.google-apps.shortcut')
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFile(gFile)
        # assert
        self.assertEqual(actual.size, 0)

    def test_CloudFolderMetadata_when_gFolder_passed(self):
        gFile = self._createGoogleDriveFolder()
        expected = self._createCloudFolderMetadata()
        # act
        actual = self.sut.convert_GoogleDriveFile_to_CloudFolderMetadata(gFile)
        # assert
        self.assertEqual(actual, expected)

    DEFAULT_ID = '1C7Vb'
    DEFAULT_NAME = 'File1.pdf'

    @staticmethod
    def _createGoogleDriveFile(mimeType='application/pdf', name=DEFAULT_NAME, id=DEFAULT_ID):
        return GoogleDriveFile(metadata={
            'id': id, 'title': name,
            'modifiedDate': '2023-08-15T14:27:44.000Z',
            'mimeType': mimeType, 'fileSize': '12345'})

    @staticmethod
    def _createCloudFileMetadata(cloud_path=DEFAULT_NAME, name=DEFAULT_NAME, id=DEFAULT_ID):
        return CloudFileMetadata(name, cloud_path,
                                 datetime.datetime(2023, 8, 15, 14, 27, 44),
                                 12345, id, '0')

    @staticmethod
    def _createGoogleDriveFolder(name='Settings', id=DEFAULT_ID):
        return GoogleDriveFile(metadata={
            'id': id, 'title': name,
            'mimeType': 'application/vnd.google-apps.folder'})

    @staticmethod
    def _createCloudFolderMetadata(cloud_path='Settings', name='Settings', id=DEFAULT_ID):
        return CloudFolderMetadata(id, name, id, cloud_path)
