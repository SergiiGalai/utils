import datetime
from unittest.mock import Mock
import logging
import dropbox
import pytest

from src.sync.stores.dropbox.dropbox_file_converter import DropboxFileConverter
from tests.file_metadata import create_cloud_file, create_cloud_folder


@pytest.fixture
def sut():
    logger = Mock(logging.Logger)
    return DropboxFileConverter(logger)


def test_2_files_when_converterd_gfiles_with_2_files_in_the_root(sut: DropboxFileConverter):
    dbx_file1 = __create_DropboxFile('/f1.pdf', 'f1.pdf', '/f1.pdf')
    dbx_file2 = __create_DropboxFile('/F2.pdf', 'F2.pdf', '/f2.pdf')
    expected1 = create_cloud_file('/f1.pdf', 'f1.pdf', '/f1.pdf')
    expected2 = create_cloud_file('/F2.pdf', 'F2.pdf', '/f2.pdf')
    # act
    actual = sut.convert_dropbox_entries_to_cloud([dbx_file1, dbx_file2])
    assert actual.folders == []
    assert actual.files == [expected1, expected2]


def test_2_files_when_converterd_gfiles_with_2_files_in_the_subfolder(sut: DropboxFileConverter):
    dbx_file1 = __create_DropboxFile('/Root/f1.pdf', 'f1.pdf', '/root/f1.pdf')
    dbx_file2 = __create_DropboxFile('/Root/F2.pdf', 'F2.pdf', '/root/f2.pdf')
    expected1 = create_cloud_file('/Root/f1.pdf', 'f1.pdf', '/root/f1.pdf')
    expected2 = create_cloud_file('/Root/F2.pdf', 'F2.pdf', '/root/f2.pdf')
    # act
    actual = sut.convert_dropbox_entries_to_cloud([dbx_file1, dbx_file2])
    assert actual.folders == []
    assert actual.files == [expected1, expected2]


def test_result_contains_converted_dropbox_file(sut: DropboxFileConverter):
    dbx_md = __create_DropboxFile('/Root/f.pdf', 'f.pdf', '/root/f.pdf')
    expected = create_cloud_file('/Root/f.pdf', 'f.pdf', '/root/f.pdf')
    # act
    actual = sut.convert_DropboxFile_to_CloudFile(dbx_md)
    assert actual == expected


def test_result_contains_converted_dropbox_folder(sut: DropboxFileConverter):
    dbx_dir = __create_DropboxFolder('/Root/SubPath', '/root/subpath', 'SubPath')
    expected = create_cloud_folder('/Root/SubPath', '/root/subpath', 'SubPath', '/root/subpath')
    # act
    actual = sut.convert_DropboxFolder_to_CloudFolder(dbx_dir)
    assert actual == expected


def __create_DropboxFile(path_display, name, path_lower):
    result = Mock(dropbox.files.FileMetadata)  # type: ignore
    result.id = 'id:AABBCC'
    result.name = name
    result.path_display = path_display
    result.path_lower = path_lower
    result.client_modified = datetime.datetime(2023, 8, 1, 20, 14, 14)
    result.content_hash = '123'
    result.size = 2000
    return result


def __create_DropboxFolder(path_display, path_lower, name):
    result = Mock(dropbox.files.FolderMetadata)  # type: ignore
    result.id = 'id:AABBCC'
    result.path_display = path_display
    result.path_lower = path_lower
    result.name = name
    return result
