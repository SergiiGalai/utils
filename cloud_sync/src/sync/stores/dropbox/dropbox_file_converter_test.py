import datetime
from unittest.mock import Mock
import logging
import dropbox
import pytest

from src.sync.stores.dropbox.dropbox_file_converter import DropboxFileConverter
from src.sync.stores.models import CloudId
from tests.file_metadata import create_cloud_file, create_cloud_folder

_ROOT_FOLDER = CloudId('/', '/')

@pytest.fixture
def sut():
    logger = Mock(logging.Logger)
    return DropboxFileConverter(logger)


@pytest.mark.parametrize('display1,name1,lower1,folder1,display2,name2,lower2,folder2', [
    ('/f1.pdf', 'f1.pdf', '/f1.pdf', _ROOT_FOLDER,
     '/F2.pdf', 'F2.pdf', '/f2.pdf', _ROOT_FOLDER),
    ('/f1.pdf', 'f1.pdf', '/f1.pdf', _ROOT_FOLDER,
     '/Root/F2.pdf', 'F2.pdf', '/root/f2.pdf', CloudId('/Root', '/Root')),
])
def test_2_files_when_converterd_gfiles_with_2_files(sut: DropboxFileConverter,
                                                     display1, name1, lower1, folder1,
                                                     display2, name2, lower2, folder2):
    dbx_file1 = __create_DropboxFile(display1, name1, lower1)
    dbx_file2 = __create_DropboxFile(display2, name2, lower2)
    expected1 = create_cloud_file(display1, name1, lower1, folder1)
    expected2 = create_cloud_file(display2, name2, lower2, folder2)
    # act
    actual = sut.convert_dropbox_entries_to_cloud([dbx_file1, dbx_file2])
    assert actual.folders == []
    assert actual.files == [expected1, expected2]


@pytest.mark.parametrize('display,name,lower,folder', [
    ('/f.pdf', 'f.pdf', '/f.pdf', _ROOT_FOLDER),
    ('/Root/f.pdf', 'f.pdf', '/root/f.pdf', CloudId('/Root', '/Root')),
    ('/Root/Sub/f.pdf', 'f.pdf', '/root/sub/f.pdf', CloudId('/Root/Sub', '/Root/Sub')),
])
def test_converted_dropbox_file(sut: DropboxFileConverter,
                                display, name, lower, folder):
    dbx_md = __create_DropboxFile(display, name, lower)
    expected = create_cloud_file(display, name, lower, folder)
    # act
    actual = sut.convert_DropboxFile_to_CloudFile(dbx_md)
    assert actual == expected


@pytest.mark.parametrize('display,name,lower', [
    ('/Root/SubPath', '/root/subpath', 'SubPath'),
    ('/Root', '/root', 'Root'),
    ('/', '/', ''),
])
def test_converted_dropbox_folder(sut: DropboxFileConverter,
                                  display, lower, name):
    dbx_dir = __create_DropboxFolder(display, lower, name)
    expected = create_cloud_folder(display, lower, name, lower)
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
