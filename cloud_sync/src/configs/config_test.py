import unittest
from unittest.mock import Mock
import logging
from argparse import Namespace
from src.configs.config import StorageConfigProvider


class StorageConfigProviderTests(unittest.TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self._sut = StorageConfigProvider(logger)

    # def test_gets_dropbox_configuration_by_default(self):
    #     args = self._createArgs()
    #     #act
    #     actual = self._sut.get_config(args)
    #     #assert
    #     self.assertEqual(actual.storage_name, 'DROPBOX')

    def test_gets_dropbox_configuration_when_passing_dropbox_storage(self):
        args = self.__createArgs(config='config.ini', storage='DROPBOX')
        # act
        actual = self._sut.get_config(args)
        # assert
        self.assertEqual(actual.storage_name, 'DROPBOX')
        self.assertEqual(actual.action, 'sync')
        self.assertIsNotNone(actual.local_dir)
        self.assertNotEqual(actual.local_dir, 'c:\\cloud_sync\\dropbox\\')
        self.assertTrue('dropbox' in actual.local_dir,
                        '{} does not contain substring'.format(actual.local_dir))
        self.assertEqual(actual.cloud_dir, '/Temporary')
        self.assertIsNotNone(actual.token)
        self.assertNotEqual(actual.token, '123')
        self.assertTrue(actual.recursive)
        self.assertFalse(actual.dry_run)

    def test_gets_gdrive_configuration_when_passing_gdrive_storage(self):
        args = self.__createArgs(config='config.ini', storage='GDRIVE')
        # act
        actual = self._sut.get_config(args)
        # assert
        self.assertEqual(actual.storage_name, 'GDRIVE')
        self.assertEqual(actual.action, 'sync')
        self.assertIsNotNone(actual.local_dir)
        self.assertNotEqual(actual.local_dir, 'c:\\cloud_sync\\gdrive\\')
        self.assertEqual(actual.cloud_dir, '/Temporary')
        self.assertTrue(actual.recursive)
        self.assertFalse(actual.dry_run)
        self.assertIsNone(actual.token)

    def test_gets_overridden_configuration_values(self):
        args = Mock(config='anotherconfig.ini', storage='DROPBOX', yes=None, no=None, default=None, action='upload',
                    token='12345', local_dir='d:\\another.ini', cloud_dir='/system', dry_run=True, recursive=False)
        # act
        actual = self._sut.get_config(args)
        # assert
        self.assertEqual(actual.action, 'upload')
        self.assertEqual(actual.local_dir, 'd:\\another.ini')
        self.assertEqual(actual.cloud_dir, '/system')
        self.assertFalse(actual.recursive)
        self.assertTrue(actual.dry_run)
        self.assertEqual(actual.token, '12345')

    def test_gets_absolute_local_directory_path_when_passed_relative(self):
        args = self.__createArgs(config='config.ini', storage='GDRIVE', local_dir='.\\another.ini')
        # act
        actual = self._sut.get_config(args)
        # assert
        self.assertFalse(actual.local_dir.startswith('.'))

    @staticmethod
    def __createArgs(config=None, storage=None, local_dir=None):
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
