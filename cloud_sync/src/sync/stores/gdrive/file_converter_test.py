import logging
import pytest
from unittest.mock import Mock
from pydrive.drive import GoogleDriveFile

from src.sync.stores.gdrive.file_converter import GoogleDriveFileConverter
from tests.file_metadata import create_cloud_file, create_cloud_folder

class TestGoogleDriveFileConverter:

    @pytest.fixture
    def sut(self):
        logger = Mock(logging.Logger)
        return GoogleDriveFileConverter(logger)

    def test_2_files_when_converterd_gfiles_with_2_files_in_the_root(self, sut: GoogleDriveFileConverter):
        gFile1 = self.__create_drive_file(id='1', name='f1.pdf')
        gFile2 = self.__create_drive_file(id='2', name='F2.pdf')
        expected1 = self.__create_cloud_file('/f1.pdf', 'f1.pdf', '1')
        expected2 = self.__create_cloud_file('/F2.pdf', 'F2.pdf', '2')
        # act
        actual = sut.convert_GoogleDriveFiles_to_FileMetadatas([gFile1, gFile2])
        assert actual.folders == []
        assert actual.files == [expected1, expected2]

    def test_2_files_when_converterd_gfiles_with_2_files_in_the_subfolder(self, sut: GoogleDriveFileConverter):
        gFile1 = self.__create_drive_file(id='1', name='f1.pdf')
        gFile2 = self.__create_drive_file(id='2', name='F2.pdf')
        expected1 = self.__create_cloud_file('/Root/Subpath/f1.pdf', 'f1.pdf', '1')
        expected2 = self.__create_cloud_file('/Root/Subpath/F2.pdf', 'F2.pdf', '2')
        # act
        actual = sut.convert_GoogleDriveFiles_to_FileMetadatas([gFile1, gFile2], '/Root/Subpath')
        assert actual.folders == []
        assert actual.files == [expected1, expected2]

    def test_CloudFileMetadata_when_converted_gfile_with_empty_cloud_path(self, sut: GoogleDriveFileConverter):
        gFile = self.__create_drive_file()
        expected = self.__create_cloud_file('/File1.pdf')
        # act
        actual = sut.convert_GoogleDriveFile_to_CloudFile(gFile)
        assert actual == expected

    def test_CloudFileMetadata_when_converted_gfile_with_slash_as_cloud_path(self, sut: GoogleDriveFileConverter):
        gFile = self.__create_drive_file()
        expected = self.__create_cloud_file('/File1.pdf')
        # act
        actual = sut.convert_GoogleDriveFile_to_CloudFile(gFile, '/')
        assert actual == expected

    def test_CloudFileMetadata_when_converted_gfile_with_subpath(self, sut: GoogleDriveFileConverter):
        gFile = self.__create_drive_file()
        expected = self.__create_cloud_file('/Root/File1.pdf')
        # act
        actual = sut.convert_GoogleDriveFile_to_CloudFile(gFile, '/Root')
        assert actual == expected

    def test_CloudFileMetadata_when_converted_gfile_with_level3_subpath(self, sut: GoogleDriveFileConverter):
        gFile = self.__create_drive_file()
        expected = self.__create_cloud_file('/Root/sub2/sub3/File1.pdf')
        # act
        actual = sut.convert_GoogleDriveFile_to_CloudFile(gFile, '/Root/sub2/sub3')
        assert actual == expected

    def test_CloudFileMetadata_with_null_file_size_when_gfile_is_a_shortcut(self, sut: GoogleDriveFileConverter):
        gFile = self.__create_drive_file('application/vnd.google-apps.shortcut')
        # act
        actual = sut.convert_GoogleDriveFile_to_CloudFile(gFile)
        assert actual.size == 0

    def test_CloudFolderMetadata_when_gFolder_passed(self, sut: GoogleDriveFileConverter):
        gFile = self.__create_drive_folder()
        expected = self.__create_cloud_folder()
        # act
        actual = sut.convert_GoogleDriveFile_to_CloudFolderMetadata(gFile, '/Root')
        assert actual == expected

    DEFAULT_ID = '1C7Vb'

    @staticmethod
    def __create_drive_file(mimeType='application/pdf', name='File1.pdf', id=DEFAULT_ID):
        return GoogleDriveFile(metadata={
            'id': id, 'title': name,
            'modifiedDate': '2023-08-01T20:14:14.000Z',
            'mimeType': mimeType, 'fileSize': '2000'})

    @staticmethod
    def __create_cloud_file(cloud_path='/Root/File1.pdf', name='File1.pdf', id=DEFAULT_ID):
        return create_cloud_file(cloud_path, name, id, hash='0')

    @staticmethod
    def __create_drive_folder(name='Subpath', id=DEFAULT_ID):
        return GoogleDriveFile(metadata={
            'id': id, 'title': name,
            'mimeType': 'application/vnd.google-apps.folder'})

    @staticmethod
    def __create_cloud_folder(name='Subpath', lower_path='/root/subpath', cloud_path='/Root/Subpath', id=DEFAULT_ID):
        return create_cloud_folder(cloud_path, lower_path, name, id)
