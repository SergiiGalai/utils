import logging
import pytest
from unittest.mock import Mock
from pydrive.drive import GoogleDriveFile

from src.sync.stores.gdrive.gdrive_file_converter import GoogleDriveFileConverter
from src.sync.stores.models import CloudId
from tests.file_metadata import create_cloud_file, create_cloud_folder

_ROOT_FOLDER = CloudId('folderId1', '/')

@pytest.fixture
def sut():
    logger = Mock(logging.Logger)
    return GoogleDriveFileConverter(logger)

def test_2_files_when_converterd_gfiles_with_2_files_in_the_root(sut: GoogleDriveFileConverter):
    gFile1 = __create_drive_file(id='1', name='f1.pdf')
    gFile2 = __create_drive_file(id='2', name='F2.pdf')
    expected1 = __create_cloud_file('/f1.pdf', 'f1.pdf', '1', _ROOT_FOLDER)
    expected2 = __create_cloud_file('/F2.pdf', 'F2.pdf', '2', _ROOT_FOLDER)
    # act
    actual = sut.convert_GoogleDriveFiles_to_FileMetadatas([gFile1, gFile2], '/')
    assert actual.folders == []
    assert actual.files == [expected1, expected2]

def test_2_files_when_converterd_gfiles_with_2_files_in_the_subfolder(sut: GoogleDriveFileConverter):
    gFile1 = __create_drive_file(id='1', name='f1.pdf', folder_id='dir2')
    gFile2 = __create_drive_file(id='2', name='F2.pdf', folder_id='dir2')
    folder = CloudId('dir2', '/Root/Subpath')
    expected1 = __create_cloud_file('/Root/Subpath/f1.pdf', 'f1.pdf', '1', folder)
    expected2 = __create_cloud_file('/Root/Subpath/F2.pdf', 'F2.pdf', '2', folder)
    # act
    actual = sut.convert_GoogleDriveFiles_to_FileMetadatas([gFile1, gFile2], '/Root/Subpath')
    assert actual.folders == []
    assert actual.files == [expected1, expected2]

def test_CloudFileMetadata_when_converted_gfile_with_empty_cloud_path(sut: GoogleDriveFileConverter):
    gFile = __create_drive_file()
    expected = __create_cloud_file('/File1.pdf', folder=_ROOT_FOLDER)
    # act
    actual = sut.convert_GoogleDriveFile_to_CloudFile(gFile, _ROOT_FOLDER)
    assert actual == expected

def test_CloudFileMetadata_when_converted_gfile_with_slash_as_cloud_path(sut: GoogleDriveFileConverter):
    gFile = __create_drive_file()
    folder = CloudId('folderId1', '/')
    expected = __create_cloud_file('/File1.pdf', folder=folder)
    # act
    actual = sut.convert_GoogleDriveFile_to_CloudFile(gFile, folder)
    assert actual == expected

def test_CloudFileMetadata_when_converted_gfile_with_subpath(sut: GoogleDriveFileConverter):
    gFile = __create_drive_file()
    folder=CloudId('folderId1', '/Root')
    expected = __create_cloud_file('/Root/File1.pdf', folder=folder)
    # act
    actual = sut.convert_GoogleDriveFile_to_CloudFile(gFile, folder)
    assert actual == expected

def test_CloudFileMetadata_when_converted_gfile_with_level3_subpath(sut: GoogleDriveFileConverter):
    gFile = __create_drive_file()
    folder=CloudId('folderSub3Id', '/Root/sub2/sub3')
    expected = __create_cloud_file('/Root/sub2/sub3/File1.pdf', folder=folder)
    # act
    actual = sut.convert_GoogleDriveFile_to_CloudFile(gFile, folder)
    assert actual == expected

def test_CloudFileMetadata_with_null_file_size_when_gfile_is_a_shortcut(sut: GoogleDriveFileConverter):
    gFile = __create_drive_file(mimeType='application/vnd.google-apps.shortcut')
    # act
    actual = sut.convert_GoogleDriveFile_to_CloudFile(gFile, _ROOT_FOLDER)
    assert actual.size == 0

def test_CloudFolderMetadata_when_gFolder_passed(sut: GoogleDriveFileConverter):
    gFile = __create_drive_folder('Subpath', 'FolderId1')
    expected = create_cloud_folder('/Root/Subpath', '/root/subpath', 'Subpath', 'FolderId1')
    # act
    actual = sut.convert_GoogleDriveFile_to_CloudFolderMetadata(gFile, '/Root')
    assert actual == expected


@staticmethod
def __create_drive_file(name='File1.pdf', id='fileId1', mimeType='application/pdf', folder_id=_ROOT_FOLDER.id):
    return GoogleDriveFile(metadata={
        'id': id, 'title': name,
        'modifiedDate': '2023-08-01T20:14:14.000Z',
        'mimeType': mimeType,
        'fileSize': '2000',
        'parents':[
            {'id': folder_id}
        ]
    })

@staticmethod
def __create_cloud_file(cloud_path='/Root/File1.pdf', name='File1.pdf', fileId='fileId1',
                        folder=CloudId('RootId', '/Root')):
    return create_cloud_file(cloud_path, name, fileId, folder, hash='0')

@staticmethod
def __create_drive_folder(name, id):
    return GoogleDriveFile(metadata={
        'id': id, 'title': name,
        'mimeType': 'application/vnd.google-apps.folder'
    })
