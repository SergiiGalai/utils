import datetime
from unittest import TestCase
from unittest.mock import Mock
import logging
from src.clients.command_ui import CommandHandlerUi
from src.clients.console_ui import ConsoleUi

from src.command_handler import CommandHandler
from src.sync.file_sync_service import FileSyncronizationService
from src.sync.models import MapFolderResult
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class UiMock(ConsoleUi):
    def output(self, message):
        print(message)

    def message(self, message):
        print('===' + message)

    def confirm(self, message, default):
        print(message)


class TestCommandHandler(TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        sync_service = Mock(FileSyncronizationService)
        sync_service.download_files = Mock()
        sync_service.upload_files = Mock()
        sync_service.local_root.return_value = 'C:\\Path\\CloudRoot'
        ui = CommandHandlerUi(UiMock(logger), logger)
        self._sync_service = sync_service
        self._sut = CommandHandler(self._sync_service, ui, logger)

    def test_ui_output_using_debugger_and_debug_console(self):
        local1 = TestCommandHandler.__createLocalFile('f1.pdf', '/f1.pdf', 'c:\\root\\f1.pdf')
        local2 = TestCommandHandler.__createLocalFile('f2.pdf', '/sub/f2.pdf', 'c:\\root\\f2.pdf')
        cloud1 = TestCommandHandler.__createCloudFile('f3.pdf', '/f3.pdf')
        cloud2 = TestCommandHandler.__createCloudFile('f4.pdf', '/sub/f4.pdf')
        self.__set_map_files([cloud1, cloud2], [local1, local2])
        self._sut.handle('sync', '/path')
        pass

    def test_run_throws_when_unknown_command_passed(self):
        self.assertRaises(NotImplementedError, self._sut.handle, 'unknownCommand', '')
        self.assertRaises(NotImplementedError, self._sut.handle, 'DOWNLOAD', '')
        self.assertRaises(NotImplementedError, self._sut.handle, 'Upload', '')
        self.assertRaises(NotImplementedError, self._sut.handle, 'sYnc', '')

    def __set_map_files(self, download=[], upload=[]):
        map_folder_result = MapFolderResult(download, upload)
        self._sync_service.map_folder.return_value = map_folder_result

    @staticmethod
    def __createLocalFile(file_name, cloud_file_path, local_file_path,
                          modified_day=1, size=2000):
        return LocalFileMetadata(
            file_name, cloud_file_path,
            datetime.datetime(2023, 8, modified_day, 20, 14, 14),
            size, local_file_path,
            'mime')

    @staticmethod
    def __createCloudFile(file_name, cloud_file_path,
                          modified_day=1, size=2000):
        return CloudFileMetadata(
            file_name, cloud_file_path,
            datetime.datetime(2023, 8, modified_day, 20, 14, 14),
            size, cloud_file_path, '123321')
