import datetime
import unittest
from unittest.mock import Mock
import logging
from src.configs.config import StorageConfig
from src.services.file_sync_service import FileSyncronizationService
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileMetadata, LocalFileStore
from src.stores.models import CloudFileMetadata, CloudFolderMetadata

class FileSyncronizationServiceTests(unittest.TestCase):
   _LOCAL_FOLDER_PATH = 'c:\\path\\sub'
   _LOCAL_FILE_PATH = 'c:\\path\\sub\\f.txt'
   _CLOUD_FOLDER_PATH = '/sub'
   _CLOUD_FILE_PATH = '/sub/f.txt'
   _FILE_NAME = 'f.txt'
   _FILE_CONTENT = '111'

   def setUp(self):
      logger = Mock(logging.Logger)
      self.localStore = Mock(LocalFileStore)
      self.cloudStore = Mock(CloudStore)
      self.config = self._createConfig()
      self.sut = FileSyncronizationService(self.localStore, self.cloudStore, self.config, logger)

   def test_empty_lists_when_local_and_cloud_files_match_by_metadata(self):
      self.localStore.get_file_metadata = Mock(return_value= self._createLocalFile())
      self._mock_local_list()
      self._mock_cloud_list([self._createCloudFile()])

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [])

   def test_empty_lists_when_local_and_cloud_files_match_by_metadata_even_if_different_by_content(self):
      local_file = self._createLocalFile()
      self._mock_local_list()
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile()
      self._mock_cloud_list([cloud_file])
      self._mock_cloud_read(cloud_file, '222')

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [])

   def test_file_to_download_when_local_storage_has_no_file(self):
      self._mock_local_list([])
      self._mock_cloud_list([self._createCloudFile()])

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [self._CLOUD_FILE_PATH])
      self.assertListEqual(actual_upload, [])

   def test_empty_lists_when_local_storage_file_is_older_but_same_by_content(self):
      local_file = self._createLocalFile()
      self._mock_local_list()
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile(3)
      self._mock_cloud_list([cloud_file])
      self._mock_cloud_read(cloud_file)

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [])

   def test_file_to_download_when_local_file_is_older_and_different_by_content_file(self):
      local_file = self._createLocalFile()
      self._mock_local_list()
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile(3)
      self._mock_cloud_list([cloud_file])
      self._mock_cloud_read(cloud_file, '1234')

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [self._CLOUD_FILE_PATH])
      self.assertListEqual(actual_upload, [])

   def test_file_to_download_when_local_file_is_different_by_content_and_size(self):
      local_file = self._createLocalFile()
      self._mock_local_list()
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile(3, 1000)
      self._mock_cloud_list([cloud_file])
      self._mock_cloud_read(cloud_file, '1234')

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [self._CLOUD_FILE_PATH])
      self.assertListEqual(actual_upload, [])

   def test_file_to_upload_when_local_file_is_newer_and_different_by_content(self):
      local_file = self._createLocalFile(4)
      self._mock_local_list()
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile()
      self._mock_cloud_list([cloud_file])
      self._mock_cloud_read(cloud_file, '1234')

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [self._CLOUD_FILE_PATH])

   def test_file_to_upload_when_no_file_in_the_cloud(self):
      self.localStore.get_file_metadata = Mock(return_value= self._createLocalFile())
      self._mock_local_list()
      self._mock_cloud_list([])

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [self._CLOUD_FILE_PATH])


   @staticmethod
   def _createConfig(name='stub', local_dir = 'c:\\path', cloud_dir = _CLOUD_FOLDER_PATH, recursive = False):
      return StorageConfig(name, 'sync', '123456', local_dir, cloud_dir, True, recursive)

   def _createLocalFile(self, modified_day = 1, size=2000):
      return LocalFileMetadata(self._FILE_NAME, self._LOCAL_FILE_PATH, datetime.datetime(2023, 8, modified_day, 20, 14, 14), size )

   def _createCloudFile(self, modified_day = 1, size=2000):
      return CloudFileMetadata(self._CLOUD_FILE_PATH, self._FILE_NAME, self._CLOUD_FILE_PATH, datetime.datetime(2023, 8, modified_day, 20, 14, 14), size )

   def _mock_cloud_list(self, files: list):
      self.cloudStore.list_folder = Mock(return_value=(self._CLOUD_FOLDER_PATH, [], files))

   def _mock_local_list(self, files: list = [_FILE_NAME]):
      self.localStore.list_folder = Mock(return_value=(self._LOCAL_FOLDER_PATH, [], files))
      self.localStore.get_absolute_path = Mock(return_value= self._LOCAL_FILE_PATH)

   def _mock_cloud_read(self, file: CloudFileMetadata, content = _FILE_CONTENT):
      cloudReadResponse=Mock()
      cloudReadResponse.content = content
      self.cloudStore.read = Mock(return_value=(cloudReadResponse, file))

   def _mock_local_read(self, file: LocalFileMetadata, content = _FILE_CONTENT):
      self.localStore.get_file_metadata = Mock(return_value= file)
      self.localStore.read = Mock(return_value=(content, file))
