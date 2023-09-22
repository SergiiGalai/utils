import logging
import pytest
from unittest.mock import Mock

from src.sync.mapping.file_mapper import FileMapper
from src.sync.models import FileSyncAction
from src.sync.file_sync_action_provider import FileSyncActionProvider
from tests.file_metadata import create_local_file, create_cloud_file


@pytest.fixture
def action_provider():
    return Mock(FileSyncActionProvider)


@pytest.fixture
def sut(action_provider):
    logger = Mock(logging.Logger)
    return FileMapper(action_provider, logger)


def test_empty_lists_when_files_match(sut: FileMapper):
    local_file = create_local_file()
    cloud_file = create_cloud_file()
    # act
    actual = sut.map_cloud_to_local([cloud_file], [local_file])
    assert actual.download == []
    assert actual.upload == []


def test_file_to_upload_when_no_file_in_the_cloud(sut: FileMapper):
    local_file = create_local_file()
    # act
    actual = sut.map_cloud_to_local([], [local_file])
    assert actual.download == []
    assert actual.upload == [local_file]


def test_file_to_download_when_no_file_locally(sut: FileMapper):
    cloud_file = create_cloud_file()
    # act
    actual = sut.map_cloud_to_local([cloud_file], [])
    assert actual.download == [cloud_file]
    assert actual.upload == []


def test_empty_lists_when_different_files_but_skip_action(sut: FileMapper, action_provider: FileSyncActionProvider):
    local_file = create_local_file()
    cloud_file = create_cloud_file(modified_day=3)
    action_provider.get_sync_action.return_value = FileSyncAction.SKIP
    # act
    actual = sut.map_cloud_to_local([cloud_file], [local_file])
    assert actual.download == []
    assert actual.upload == []


def test_empty_lists_when_different_files_but_conflict_action(sut: FileMapper, action_provider: FileSyncActionProvider):
    local_file = create_local_file()
    cloud_file = create_cloud_file(modified_day=3)
    action_provider.get_sync_action.return_value = FileSyncAction.CONFLICT
    # act
    actual = sut.map_cloud_to_local([cloud_file], [local_file])
    assert actual.download == []
    assert actual.upload == []


def test_file_to_download_when_files_equal_but_download_action(sut: FileMapper, action_provider: FileSyncActionProvider):
    local_file = create_local_file()
    cloud_file = create_cloud_file()
    action_provider.get_sync_action.return_value = FileSyncAction.DOWNLOAD
    # act
    actual = sut.map_cloud_to_local([cloud_file], [local_file])
    assert actual.download == [cloud_file]
    assert actual.upload == []


def test_file_to_upload_when_files_equal_but_upload_action(sut: FileMapper, action_provider: FileSyncActionProvider):
    local_file = create_local_file()
    cloud_file = create_cloud_file()
    action_provider.get_sync_action.return_value = FileSyncAction.UPLOAD
    # act
    actual = sut.map_cloud_to_local([cloud_file], [local_file])
    assert actual.download == []
    assert actual.upload == [local_file]


def test_files_to_download_when_local_files_with_the_same_name_in_different_folders_do_not_exist(sut: FileMapper):
    cloud_file_root = create_cloud_file()
    cloud_file_subfolder = create_cloud_file('/Sub/2/f.txt')
    # act
    actual = sut.map_cloud_to_local([cloud_file_root, cloud_file_subfolder], [])
    assert actual.download == [cloud_file_root, cloud_file_subfolder]
    assert actual.upload == []


def test_files_to_upload_when_cloud_files_with_the_same_name_in_different_folders_do_not_exist(sut: FileMapper):
    local_file_root = create_local_file()
    local_file_subfolder = create_local_file('/Sub/2/f.txt', 'c:\\path\\sub\\2\\f.txt')
    # act
    actual = sut.map_cloud_to_local([], [local_file_root, local_file_subfolder])
    assert actual.download == []
    assert actual.upload == [local_file_root, local_file_subfolder]
