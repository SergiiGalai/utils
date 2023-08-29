import unittest
from unittest.mock import Mock
import logging
from src.clients.ui import UI

from src.command import CommandRunner
from src.services.file_sync_service import FileSyncronizationService
from src.stores.local_file_store import LocalFileStore

class UiMock(UI):
   def output(self, message):
      print(message)

   def message(self, message):
      print('==='+message)

   def confirm(self, message, default):
      print(message)

class CommandRunnerTests(unittest.TestCase):

   def setUp(self):
      logger = Mock(logging.Logger)
      localStore = Mock(LocalFileStore)
      localStore.get_absolute_path = Mock(return_value='C:\\Path\\CloudRoot')

      self._syncService = Mock(FileSyncronizationService)
      self._syncService.download_files = Mock()
      self._syncService.upload_files = Mock()

      ui = UiMock(logger)
      self.sut = CommandRunner(localStore, self._syncService, ui, logger)

   def test_ui_output_using_debugger_and_debug_console(self):
      self._set_map_files(['file1.pdf', '/sub/file2.pdf'], ['file3.xls', '/sub/file4.pdf'])
      self.sut.run('sync', '/path')
      pass

   def test_run_throws_when_unknown_command_passed(self):
      self.assertRaises(NotImplementedError, self.sut.run, 'unknownCommand', '')
      self.assertRaises(NotImplementedError, self.sut.run, 'DOWNLOAD', '')
      self.assertRaises(NotImplementedError, self.sut.run, 'Upload', '')
      self.assertRaises(NotImplementedError, self.sut.run, 'sYnc', '')

   def _set_map_files(self, download = [], upload = []):
      self._syncService.map_files = Mock(return_value=(download, upload))
