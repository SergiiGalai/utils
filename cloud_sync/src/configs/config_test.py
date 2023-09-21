from unittest import TestCase
from unittest.mock import Mock
import logging
from argparse import Namespace
from src.configs.config import StorageConfigProvider


class TestStorageConfigProvider(TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self._sut = StorageConfigProvider(logger)

    # def test_gets_dropbox_configuration_by_default(self):
    #     args = self._createArgs()
    #     actual = self._sut.get_config(args)
    #     assert actual.storage_name == 'DROPBOX'

    def test_gets_dropbox_configuration_when_passing_dropbox_storage(self):
        args = self.__createArgs(config='config.ini', storage='DROPBOX')
        # act
        actual = self._sut.get_config(args)
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

    def test_gets_gdrive_configuration_when_passing_gdrive_storage(self):
        args = self.__createArgs(config='config.ini', storage='GDRIVE')
        # act
        actual = self._sut.get_config(args)
        # assert
        assert actual.storage_name == 'GDRIVE'
        assert actual.action == 'sync'
        assert actual.local_dir is not None
        assert actual.local_dir != 'c:\\cloud_sync\\gdrive\\'
        assert actual.cloud_dir == '/Temporary'
        assert actual.recursive == True
        assert actual.dry_run == False
        assert actual.token is None

    def test_gets_overridden_configuration_values(self):
        args = Mock(config='anotherconfig.ini', storage='DROPBOX', yes=None, no=None, default=None, action='upload',
                    token='12345', local_dir='d:\\another.ini', cloud_dir='/system', dry_run=True, recursive=False)
        # act
        actual = self._sut.get_config(args)
        # assert
        assert actual.action == 'upload'
        assert actual.local_dir == 'd:\\another.ini'
        assert actual.cloud_dir == '/system'
        assert actual.recursive == False
        assert actual.dry_run == True
        assert actual.token == '12345'

    def test_gets_absolute_local_directory_path_when_passed_relative(self):
        args = self.__createArgs(config='config.ini', storage='GDRIVE', local_dir='.\\another.ini')
        # act
        actual = self._sut.get_config(args)
        assert actual.local_dir.startswith('.') == False

    @staticmethod
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
