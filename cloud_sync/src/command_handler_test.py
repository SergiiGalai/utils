import datetime
import unittest
from unittest.mock import Mock
import logging
from src.clients.logger_ui import LoggerUi

from src.command_handler import CommandHandler
from src.services.file_sync_service import FileSyncronizationService
from src.services.models import MapFilesResult
from src.stores.local.file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, LocalFileMetadata


class UiMock(LoggerUi):
    def output(self, message):
        print(message)

    def message(self, message):
        print('===' + message)

    def confirm(self, message, default):
        print(message)


class CommandHandlerTests(unittest.TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        sync_service = Mock(FileSyncronizationService)
        sync_service = Mock(FileSyncronizationService)
        sync_service.download_files = Mock()
        sync_service.upload_files = Mock()
        sync_service.local_root = Mock(return_value='C:\\Path\\CloudRoot')
        ui = UiMock(logger)
        self._sync_service = sync_service
        self.sut = CommandHandler(self._sync_service, ui, logger)

    def test_ui_output_using_debugger_and_debug_console(self):
        local1 = self._createLocalFile('f1.pdf', '/f1.pdf', 'c:\\root\\f1.pdf')
        local2 = self._createLocalFile('f2.pdf', '/sub/f2.pdf', 'c:\\root\\f2.pdf')
        cloud1 = self._createCloudFile('f3.pdf', '/f3.pdf')
        cloud2 = self._createCloudFile('f4.pdf', '/sub/f4.pdf')
        self._set_map_files([cloud1, cloud2], [local1, local2])
        self.sut.handle('sync', '/path')
        pass

    def test_run_throws_when_unknown_command_passed(self):
        self.assertRaises(NotImplementedError, self.sut.handle, 'unknownCommand', '')
        self.assertRaises(NotImplementedError, self.sut.handle, 'DOWNLOAD', '')
        self.assertRaises(NotImplementedError, self.sut.handle, 'Upload', '')
        self.assertRaises(NotImplementedError, self.sut.handle, 'sYnc', '')

    def _set_map_files(self, download=[], upload=[]):
        map_files = MapFilesResult(download, upload)
        self._sync_service.map_files = Mock(return_value=map_files)

    def _createLocalFile(self, file_name,
                         cloud_file_path, local_file_path,
                         modified_day=1, size=2000):
        return LocalFileMetadata(
            file_name, cloud_file_path,
            datetime.datetime(2023, 8, modified_day, 20, 14, 14),
            size, local_file_path)

    def _createCloudFile(self, file_name, cloud_file_path, 
                         modified_day=1, size=2000):
        return CloudFileMetadata(
            file_name, cloud_file_path,
            datetime.datetime(2023, 8, modified_day, 20, 14, 14),
            size, cloud_file_path, '123321')
