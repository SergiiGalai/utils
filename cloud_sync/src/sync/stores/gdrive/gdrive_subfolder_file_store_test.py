import pytest
import logging
from unittest.mock import MagicMock, Mock

from src.sync.stores.gdrive.gdrive_api_v2_store import GdriveApiV2Store
from src.sync.stores.gdrive.gdrive_subfolder_file_store import GdriveSubfolderFileStore
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult
from tests.file_metadata import create_cloud_file, create_cloud_folder


@pytest.fixture
def store():
    return Mock(GdriveApiV2Store)


@pytest.fixture
def sut(store):
    logger = Mock(logging.Logger)
    return GdriveSubfolderFileStore(store, logger)


def test_file_when_list_sub_folder_which_does_not_exist_in_cloud(store, sut: GdriveSubfolderFileStore):
    cloud_file = create_cloud_file()
    __mock_store_list_folder(store, [cloud_file])
    # act
    actual = sut.list_folder('/Target')
    assert actual.files == [cloud_file]
    assert actual.folders == []


def test_file_and_subfolder_when_list_root_cloud_folder(store, sut: GdriveSubfolderFileStore):
    cloud_folder = create_cloud_folder()
    cloud_file = create_cloud_file()
    __mock_store_list_folder(store, [cloud_file], [cloud_folder])
    # act
    actual = sut.list_folder('/Target')
    assert actual.files == [cloud_file]
    assert actual.folders == [cloud_folder]


def test_files_and_folders_when_list_target_non_root_folder(store, sut: GdriveSubfolderFileStore):
    # arrange
    cloud_file_root = create_cloud_file('/File1.pdf', id='idrf1')
    cloud_folder_sub = create_cloud_folder('/Sub', '/sub', 'Sub', 'SubFolderId')
    cloud_file_sub = create_cloud_file('/Sub/File1.pdf', id='idf1')
    cloud_folder_sub1 = create_cloud_folder('/Sub/Sub1', '/sub/sub1', 'Sub1', 'Sub1FolderId')
    cloud_file_sub1 = create_cloud_file('/Sub/Sub1/File1.pdf', id='idsubf1')
    cloud_folder_target = create_cloud_folder('/Sub/Target', '/sub/target', 'Target', 'TargetFolderId')
    cloud_file_target = create_cloud_file('/Sub/Target/File2.pdf', 'File2.pdf', id='idsubf2')
    cloud_folder_sub2 = create_cloud_folder('/Sub/Target/Sub2', '/sub/target/sub2' 'Sub2', 'Sub2FolderId')
    cloud_file_sub2 = create_cloud_file('/Sub/Target/File2.pdf', 'File2.pdf', id='idsubf2')

    store.list_folder = MagicMock(side_effect=lambda *x: {
        ('', ''): ListCloudFolderResult([cloud_file_root], [cloud_folder_sub]),
        ('SubFolderId', '/Sub'): ListCloudFolderResult([cloud_file_sub], [cloud_folder_sub1, cloud_folder_target]),
        ('Sub1FolderId', '/Sub/Sub1'): ListCloudFolderResult([cloud_file_sub1], []),
        ('TargetFolderId', '/Sub/Target'): ListCloudFolderResult([cloud_file_target], [cloud_folder_sub2]),
        ('Sub2FolderId', '/Sub/Target/Sub2'): ListCloudFolderResult([cloud_file_sub2], []),
    }[x])  # type: ignore
    # act
    actual = sut.list_folder('/Sub/Target')
    assert actual.files == [cloud_file_target]
    assert actual.folders == [cloud_folder_sub2]


def __mock_store_list_folder(store, files: list[CloudFileMetadata], folders: list[CloudFolderMetadata] = []):
    result = ListCloudFolderResult()
    result.files = files
    result.folders = folders
    store.list_folder.return_value = result
