import unittest
from unittest.mock import Mock
import logging
from src.configs.config import StorageConfig
from src.stores.local_file_store import LocalFileStore

class LocalFileStoreTests(unittest.TestCase):

   def test_absolute_path_returned_when_relative_with_slash(self):
      logger = Mock(logging.Logger)
      config = StorageConfig('storage', 'action', 'token', 'c:\\path\\', '/root', True, True)
      sut = LocalFileStore(config, logger)

      actual = sut.get_absolute_path('/settings')

      self.assertEqual(actual, 'c:\\path\\settings')

   def test_absolute_path_returned_when_relative_path_is_slash(self):
      logger = Mock(logging.Logger)
      config = StorageConfig('storage', 'action', 'token', 'c:\\path\\', '/root', True, True)
      sut = LocalFileStore(config, logger)

      actual = sut.get_absolute_path('/')

      self.assertEqual(actual, 'c:\\path')

   def test_absolute_path_returned_when_relative_without_slash(self):
      logger = Mock(logging.Logger)
      config = StorageConfig('storage', 'action', 'token', 'c:\\path', '/root', True, True)
      sut = LocalFileStore(config, logger)

      actual = sut.get_absolute_path('settings')

      self.assertEqual(actual, 'c:\\path\\settings')

   def test_absolute_path_returned_when_relative_is_empty(self):
      logger = Mock(logging.Logger)
      config = StorageConfig('storage', 'action', 'token', 'c:\\path\\', '/root', True, True)
      sut = LocalFileStore(config, logger)

      actual = sut.get_absolute_path('')

      self.assertEqual(actual, 'c:\\path')
