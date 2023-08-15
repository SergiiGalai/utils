import unittest
from unittest.mock import Mock, MagicMock
import logging
from config import ConfigProvider, Config

class ConfigProviderTests(unittest.TestCase):

    def test_gets_dropbox_configuration_by_default(self):
        logger = Mock(logging.Logger)
        sut = ConfigProvider(logger)
        args = sut.parse_arguments()

        actual = sut.get_config(args)

        self.assertEqual(actual.action, 'sync')
        self.assertIsNotNone(actual.token)
        self.assertEqual(actual.token, '123')
        self.assertIsNotNone(actual.local_dir)
        self.assertEqual(actual.local_dir, 'c:\\dropbox\\db\\')
        self.assertEqual(actual.cloud_dir, '/settings')
        self.assertTrue(actual.recursive)
        self.assertTrue(actual.dry_run)

    def test_gets_gdrive_configuration_when_passing_gdrive_storage(self):
        logger = Mock(logging.Logger)
        sut = ConfigProvider(logger)
        args = Mock(config = None, storage='GDRIVE', yes=None, no=None, default=None, action=None, token=None, local_dir=None, cloud_dir=None, dry_run=None, recursive=None)

        actual = sut.get_config(args)

        self.assertEqual(actual.action, 'sync')
        self.assertIsNotNone(actual.local_dir)
        self.assertEqual(actual.local_dir, 'c:\\gdrive\\db\\')
        self.assertEqual(actual.cloud_dir, '/settings')
        self.assertTrue(actual.recursive)
        self.assertTrue(actual.dry_run)
        self.assertIsNone(actual.token)

    
    def test_gets_overridden_configuration_values(self):
        logger = Mock(logging.Logger)
        sut = ConfigProvider(logger)
        args = Mock(config = None, storage='DROPBOX', yes=None, no=None, default=None, action='upload', token='12345', local_dir='d:\\another.ini', cloud_dir='/system', dry_run=True, recursive=False)

        actual = sut.get_config(args)

        self.assertEqual(actual.action, 'upload')
        self.assertEqual(actual.local_dir, 'd:\\another.ini')
        self.assertEqual(actual.cloud_dir, '/system')
        self.assertFalse(actual.recursive)
        self.assertTrue(actual.dry_run)
        self.assertEqual(actual.token, '12345')

    def test_gets_absolute_local_directory_path_when_passed_relative(self):
        logger = Mock(logging.Logger)
        sut = ConfigProvider(logger)
        args = Mock(config = None, storage='GDRIVE', yes=None, no=None, default=None, action=None, token=None, local_dir='.\\another.ini', cloud_dir=None, dry_run=None, recursive=None)

        actual = sut.get_config(args)

        self.assertFalse(actual.local_dir.startswith('.'))

if __name__ == '__main__':
    unittest.main()
