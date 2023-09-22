import logging
import pytest
from unittest.mock import Mock

from src.clients.command_ui import CommandHandlerUi
from src.clients.console_ui import ConsoleUi
from src.command_handler import CommandHandler
from src.sync.file_sync_service import FileSyncronizationService
from src.sync.models import MapFolderResult
from tests.file_metadata import create_local_file, create_cloud_file

class UiMock(ConsoleUi):
    def output(self, message):
        print(message)

    def message(self, message):
        print('===' + message)

    def confirm(self, message, default):
        print(message)

@pytest.fixture
def sync_service():
    sync_service = Mock(FileSyncronizationService)
    sync_service.download_files = Mock()
    sync_service.upload_files = Mock()
    sync_service.local_root.return_value = 'C:\\Path\\CloudRoot'
    return sync_service

@pytest.fixture
def sut(sync_service):
    logger = Mock(logging.Logger)
    ui = CommandHandlerUi(UiMock(logger), logger)
    return CommandHandler(sync_service, ui, logger)

def test_ui_output_using_debugger_and_debug_console(sync_service, sut: CommandHandler):
    local1 = create_local_file('/f1.pdf', 'c:\\root\\f1.pdf', 'f1.pdf')
    local2 = create_local_file('/sub/f2.pdf', 'c:\\root\\f2.pdf', 'f2.pdf')
    cloud1 = create_cloud_file('/f3.pdf', 'f3.pdf')
    cloud2 = create_cloud_file('/sub/f4.pdf', 'f4.pdf')
    sync_service.map_folder.return_value = MapFolderResult([cloud1, cloud2], [local1, local2])
    sut.handle('sync', '/path')
    pass

@pytest.mark.parametrize("command", ['unknownCommand', 'DOWNLOAD', 'Upload', 'sYnc'])
def test_run_throws_when_unknown_command_passed(sut: CommandHandler, command: str):
    with pytest.raises(NotImplementedError):
        sut.handle(command, '')
