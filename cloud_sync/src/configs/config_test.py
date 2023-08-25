import unittest
from unittest.mock import Mock
import logging
from argparse import Namespace
from src.configs.config import StorageConfigProvider

class StorageConfigProviderTests(unittest.TestCase):

    @staticmethod
    def _createArgs(config=None, storage=None, local_dir=None):
        args = Namespace()
        args.config = config
        args.storage = storage
        args.action = None
        args.token = None
        args.local_dir = local_dir
        args.cloud_dir = None
        args.dryrun = None
        args.recursive = None
        return args

    def setUp(self):
        logger = Mock(logging.Logger)
        self.sut = StorageConfigProvider(logger)

    def test_gets_dropbox_configuration_by_default(self):
        args = self._createArgs()

        actual = self.sut.get_config(args)

        self.assertEqual(actual.storage_name, 'DROPBOX')
        self.assertEqual(actual.action, 'sync')
        self.assertIsNotNone(actual.local_dir)
        self.assertNotEqual(actual.local_dir, 'c:\\dropbox\\db\\')
        self.assertTrue('dropbox' in actual.local_dir, '{} does not contain substring'.format(actual.local_dir))
        self.assertEqual(actual.cloud_dir, '/settings')
        self.assertIsNotNone(actual.token)
        self.assertNotEqual(actual.token, '123')
        self.assertTrue(actual.recursive)
        self.assertTrue(actual.dry_run)

    def test_gets_gdrive_configuration_when_passing_gdrive_storage(self):
        args = self._createArgs(config = 'config.ini', storage='GDRIVE')
        actual = self.sut.get_config(args)

        self.assertEqual(actual.storage_name, 'GDRIVE')
        self.assertEqual(actual.action, 'sync')
        self.assertIsNotNone(actual.local_dir)
        self.assertNotEqual(actual.local_dir, 'c:\\gdrive\\db\\')
        self.assertEqual(actual.cloud_dir, '/settings')
        self.assertTrue(actual.recursive)
        self.assertTrue(actual.dry_run)
        self.assertIsNone(actual.token)

    def test_gets_overridden_configuration_values(self):
        args = Mock(config = 'anotherconfig.ini', storage='DROPBOX', yes=None, no=None, default=None, action='upload', token='12345', local_dir='d:\\another.ini', cloud_dir='/system', dry_run=True, recursive=False)

        actual = self.sut.get_config(args)

        self.assertEqual(actual.action, 'upload')
        self.assertEqual(actual.local_dir, 'd:\\another.ini')
        self.assertEqual(actual.cloud_dir, '/system')
        self.assertFalse(actual.recursive)
        self.assertTrue(actual.dry_run)
        self.assertEqual(actual.token, '12345')

    def test_gets_absolute_local_directory_path_when_passed_relative(self):
        args = self._createArgs(config = 'config.ini', storage='GDRIVE', local_dir='.\\another.ini')

        actual = self.sut.get_config(args)

        self.assertFalse(actual.local_dir.startswith('.'))
