import datetime
import unittest
from unittest.mock import Mock
import logging
from src.configs.config import StorageConfig
from src.services.file_comparer import FileComparer
from src.services.file_sync_service import FileSyncronizationService
from src.services.models import FileAction
from src.services.storage_strategy import StorageStrategy
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, LocalFileMetadata

class FileSyncronizationServiceTests(unittest.TestCase):
   _LOCAL_FILE_PATH = 'C:\\Path\\CloudRoot\\sub\\f.txt'
   _CLOUD_FOLDER_PATH = '/Sub'
   _CLOUD_FILE_PATH = '/Sub/f.txt'
   _FILE_NAME = 'f.txt'
   _FILE_CONTENT = '111'

   def setUp(self):
      logger = Mock(logging.Logger)
      self._localStore = Mock(LocalFileStore)
      self._cloudStore = Mock(CloudStore)
      self._fileComparer = Mock(FileComparer)
      self._config = self._createConfig()
      strategy = Mock(StorageStrategy)
      strategy.create_cloud_store = Mock(return_value=self._cloudStore)
      strategy.create_file_comparer = Mock(return_value=self._fileComparer)
      self.sut = FileSyncronizationService(strategy, self._localStore, self._config, logger)

   def test_empty_lists_when_local_and_cloud_files_match_by_metadata(self):
      self._mock_local_list([self._createLocalFile()])
      self._mock_cloud_list([self._createCloudFile()])

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [])

   def test_file_to_download_when_local_storage_has_no_file(self):
      cloud_file = self._createCloudFile()
      self._mock_local_list([])
      self._mock_cloud_list([cloud_file])

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [cloud_file])
      self.assertListEqual(actual_upload, [])

   def test_empty_lists_when_both_files_exist_and_file_comparer_returns_skip(self):
      local_file = self._createLocalFile()
      self._mock_local_list([local_file])
      cloud_file = self._createCloudFile(3)
      self._mock_cloud_list([cloud_file])
      self._fileComparer.get_file_action = Mock(return_value=FileAction.SKIP)
      #action
      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)
      #assert
      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [])

   def test_empty_lists_when_both_files_exist_and_file_comparer_returns_conflict(self):
      local_file = self._createLocalFile()
      self._mock_local_list([local_file])
      cloud_file = self._createCloudFile(3)
      self._mock_cloud_list([cloud_file])
      self._fileComparer.get_file_action = Mock(return_value=FileAction.CONFLICT)
      #action
      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)
      #assert
      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [])

   def test_file_to_download_when_both_files_exist_and_file_comparer_returns_download(self):
      local_file = self._createLocalFile()
      self._mock_local_list([local_file])
      cloud_file = self._createCloudFile()
      self._mock_cloud_list([cloud_file])
      self._fileComparer.get_file_action = Mock(return_value=FileAction.DOWNLOAD)
      #action
      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)
      #assert
      self.assertListEqual(actual_download, [cloud_file])
      self.assertListEqual(actual_upload, [])

   def test_file_to_upload_when_both_files_present_and_file_comparer_returns_upload(self):
      local_file = self._createLocalFile()
      self._mock_local_list([local_file])
      cloud_file = self._createCloudFile()
      self._mock_cloud_list([cloud_file])
      self._fileComparer.get_file_action = Mock(return_value=FileAction.UPLOAD)
      #action
      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)
      #assert
      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [local_file])

   def test_files_to_download_when_local_files_with_the_same_name_in_different_folders_do_not_exist(self):
      self._mock_local_list([])
      cloud_file_root = self._createCloudFile()
      cloud_file_subfolder = self._createCloudFile(cloud_file_path='/Sub/2/f.txt')
      self._mock_cloud_list([cloud_file_root, cloud_file_subfolder])
      #action
      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)
      #assert
      self.assertListEqual(actual_download, [cloud_file_root, cloud_file_subfolder])
      self.assertListEqual(actual_upload, [])

   def test_files_to_upload_when_cloud_files_with_the_same_name_in_different_folders_do_not_exist(self):
      local_file_root = self._createLocalFile()
      local_file_subfolder = self._createLocalFile(cloud_file_path='/Sub/2/f.txt', local_file_path='c:\\path\\sub\\2\\f.txt')
      self._mock_local_list([local_file_root, local_file_subfolder])
      self._mock_cloud_list([])
      #action
      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)
      #assert
      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [local_file_root, local_file_subfolder])

   def test_file_to_upload_when_no_file_in_the_cloud(self):
      local_file = self._createLocalFile()
      self._mock_local_list([local_file])
      self._mock_cloud_list([])
      #action
      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)
      #assert
      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [local_file])


   @staticmethod
   def _createConfig(name='GDRIVE', local_dir = 'c:\\path', cloud_dir = _CLOUD_FOLDER_PATH, recursive = False):
      return StorageConfig(name, 'sync', '123456', local_dir, cloud_dir, True, recursive)

   def _createLocalFile(self, modified_day = 1, size=2000, cloud_file_path = _CLOUD_FILE_PATH, local_file_path = _LOCAL_FILE_PATH):
      return LocalFileMetadata(self._FILE_NAME, cloud_file_path, datetime.datetime(2023, 8, modified_day, 20, 14, 14), size, local_file_path )

   def _createCloudFile(self, modified_day = 1, size=2000, cloud_file_path = _CLOUD_FILE_PATH):
      return CloudFileMetadata(self._FILE_NAME, cloud_file_path, datetime.datetime(2023, 8, modified_day, 20, 14, 14), size, cloud_file_path, '123321' )

   def _mock_cloud_list(self, files: list[CloudFileMetadata]):
      self._cloudStore.list_folder = Mock(return_value=([], files))

   def _mock_local_list(self, files: list[LocalFileMetadata]):
      self._localStore.list_folder = Mock(return_value=([], files))
