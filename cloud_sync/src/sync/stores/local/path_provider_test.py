from unittest.mock import Mock
import logging
from src.configs.storage_config import StorageConfig
from src.sync.stores.local.path_provider import PathProvider


def test_absolute_path_returned_when_relative_with_slash():
    config = StorageConfig('storage', 'action', 'token',
                           'c:\\path\\', '/root', True, True)
    sut = __createSut(config)
    # act
    actual = sut.get_absolute_path('/settings')
    assert actual == 'c:\\path\\settings'


def test_absolute_path_returned_when_relative_path_is_slash():
    config = StorageConfig('storage', 'action', 'token',
                           'c:\\path\\', '/root', True, True)
    sut = __createSut(config)
    # act
    actual = sut.get_absolute_path('/')
    assert actual == 'c:\\path'


def test_absolute_path_returned_when_relative_without_slash():
    config = StorageConfig('storage', 'action', 'token',
                           'c:\\path', '/root', True, True)
    sut = __createSut(config)
    # act
    actual = sut.get_absolute_path('settings')
    assert actual == 'c:\\path\\settings'


def test_absolute_path_returned_when_relative_is_empty():
    config = StorageConfig('storage', 'action', 'token',
                           'c:\\path\\', '/root', True, True)
    sut = __createSut(config)
    # act
    actual = sut.get_absolute_path('')
    assert actual == 'c:\\path'


def __createSut(config) -> PathProvider:
    logger = Mock(logging.Logger)
    return PathProvider(config, logger)
