import logging
import pytest
from unittest.mock import Mock
from argparse import Namespace

from src.configs.storage_config import StorageConfigProvider

@pytest.fixture
def sut():
    logger = Mock(logging.Logger)
    return StorageConfigProvider(logger)

# def test_dropbox_configuration_by_default(sut: StorageConfigProvider):
#     args = __createArgs()
#     actual = sut.get_config(args)
#     assert actual.storage_name == 'DROPBOX'

def test_dropbox_configuration_when_passing_dropbox_storage(sut: StorageConfigProvider):
    args = __createArgs(config='config.ini', storage='DROPBOX')
    # act
    actual = sut.get_config(args)
    # assert
    assert actual.storage_name == 'DROPBOX'
    assert actual.action == 'sync'
    assert actual.local_dir is not None
    assert actual.local_dir != 'c:\\cloud_sync\\dropbox\\'
    assert ('dropbox' in actual.local_dir) == True, f'{actual.local_dir} does not contain "dropbox" substring'
    assert actual.cloud_dir == '/Temporary'
    assert actual.token is not None
    assert actual.token != '123'
    assert actual.recursive == True
    assert actual.dry_run == False

def test_gdrive_configuration_when_passing_gdrive_storage(sut: StorageConfigProvider):
    args = __createArgs(config='config.ini', storage='GDRIVE')
    # act
    actual = sut.get_config(args)
    # assert
    assert actual.storage_name == 'GDRIVE'
    assert actual.action == 'sync'
    assert actual.local_dir is not None
    assert actual.local_dir != 'c:\\cloud_sync\\gdrive\\'
    assert actual.cloud_dir == '/Temporary'
    assert actual.recursive == True
    assert actual.dry_run == False
    assert actual.token is None

def test_overridden_configuration_values(sut: StorageConfigProvider):
    args = Mock(config='anotherconfig.ini', storage='DROPBOX', yes=None, no=None, default=None, action='upload',
                token='12345', local_dir='d:\\another.ini', cloud_dir='/system', dry_run=True, recursive=False)
    # act
    actual = sut.get_config(args)
    # assert
    assert actual.action == 'upload'
    assert actual.local_dir == 'd:\\another.ini'
    assert actual.cloud_dir == '/system'
    assert actual.recursive == False
    assert actual.dry_run == True
    assert actual.token == '12345'

def test_absolute_local_directory_path_when_passed_relative(sut: StorageConfigProvider):
    args = __createArgs(config='config.ini', storage='GDRIVE', local_dir='.\\another.ini')
    # act
    actual = sut.get_config(args)
    assert actual.local_dir.startswith('.') == False

def __createArgs(config=None, storage=None, local_dir=None):
    args = Namespace()
    args.config = config
    args.storage = storage
    args.action = None
    args.token = None
    args.local_dir = local_dir
    args.cloud_dir = None
    args.dry_run = None
    args.recursive = None
    return args
