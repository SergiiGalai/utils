import pytest
from unittest.mock import Mock
import logging
from src.configs.config import StorageConfig
from src.sync.stores.local.path_provider import PathProvider


class TestPathProvider:

    def test_absolute_path_returned_when_relative_with_slash(self):
        config = StorageConfig('storage', 'action', 'token',
                               'c:\\path\\', '/root', True, True)
        sut = self._createSut(config)
        # act
        actual = sut.get_absolute_path('/settings')
        assert actual == 'c:\\path\\settings'

    def test_absolute_path_returned_when_relative_path_is_slash(self):
        config = StorageConfig('storage', 'action', 'token',
                               'c:\\path\\', '/root', True, True)
        sut = self._createSut(config)
        # act
        actual = sut.get_absolute_path('/')
        assert actual == 'c:\\path'

    def test_absolute_path_returned_when_relative_without_slash(self):
        config = StorageConfig('storage', 'action', 'token',
                               'c:\\path', '/root', True, True)
        sut = self._createSut(config)
        # act
        actual = sut.get_absolute_path('settings')
        assert actual == 'c:\\path\\settings'

    def test_absolute_path_returned_when_relative_is_empty(self):
        config = StorageConfig('storage', 'action', 'token',
                               'c:\\path\\', '/root', True, True)
        sut = self._createSut(config)
        # act
        actual = sut.get_absolute_path('')
        assert actual == 'c:\\path'

    @staticmethod
    def _createSut(config) -> PathProvider:
        logger = Mock(logging.Logger)
        return PathProvider(config, logger)
