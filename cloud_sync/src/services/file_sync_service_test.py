import datetime
import unittest
from unittest.mock import Mock
import logging
from src.configs.config import StorageConfig
from src.services.file_sync_service import FileSyncronizationService
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, CloudFolderMetadata, LocalFileMetadata

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
      self._config = self._createConfig()
      self.sut = FileSyncronizationService(self._localStore, self._cloudStore, self._config, logger)

   def test_empty_lists_when_local_and_cloud_files_match_by_metadata(self):
      self._mock_local_list([self._createLocalFile()])
      self._mock_cloud_list([self._createCloudFile()])

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [])

   def test_empty_lists_when_local_and_cloud_files_match_by_metadata_even_if_different_by_content(self):
      local_file = self._createLocalFile()
      self._mock_local_list([local_file])
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile()
      self._mock_cloud_list([cloud_file])
      self._mock_cloud_read(cloud_file, '222')

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

   def test_empty_lists_when_local_storage_file_is_older_but_same_by_content(self):
      local_file = self._createLocalFile()
      self._mock_local_list([local_file])
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile(3)
      self._mock_cloud_list([cloud_file])
      self._mock_cloud_read(cloud_file)

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [])

   def test_file_to_download_when_local_file_is_older_and_different_by_content_file(self):
      local_file = self._createLocalFile()
      self._mock_local_list([local_file])
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile(3)
      self._mock_cloud_list([cloud_file])
      self._mock_cloud_read(cloud_file, '1234')

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [cloud_file])
      self.assertListEqual(actual_upload, [])

   def test_file_to_download_when_local_file_is_different_by_content_and_size(self):
      local_file = self._createLocalFile()
      self._mock_local_list([local_file])
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile(3, 1000)
      self._mock_cloud_list([cloud_file])
      self._mock_cloud_read(cloud_file, '1234')

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [cloud_file])
      self.assertListEqual(actual_upload, [])

   def test_files_to_download_when_local_files_with_the_same_name_in_different_folders_do_not_exist(self):
      self._mock_local_list([])
      cloud_file_root = self._createCloudFile()
      cloud_file_subfolder = self._createCloudFile(cloud_file_path='/Sub/2/f.txt')
      self._mock_cloud_list([cloud_file_root, cloud_file_subfolder])

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [cloud_file_root, cloud_file_subfolder])
      self.assertListEqual(actual_upload, [])

   def test_files_to_upload_when_cloud_files_with_the_same_name_in_different_folders_do_not_exist(self):
      local_file_root = self._createLocalFile()
      local_file_subfolder = self._createLocalFile(cloud_file_path='/Sub/2/f.txt', local_file_path='c:\\path\\sub\\2\\f.txt')
      self._mock_local_list([local_file_root, local_file_subfolder])
      self._mock_cloud_list([])

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [local_file_root, local_file_subfolder])

   def test_file_to_upload_when_local_file_is_newer_and_different_by_content(self):
      local_file = self._createLocalFile(4)
      self._mock_local_list([local_file])
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile()
      self._mock_cloud_list([cloud_file])
      self._mock_cloud_read(cloud_file, '1234')

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [local_file])

   def test_file_to_upload_when_no_file_in_the_cloud(self):
      local_file = self._createLocalFile()
      self._mock_local_list([local_file])
      self._mock_cloud_list([])

      actual_download, actual_upload = self.sut.map_files(self._CLOUD_FOLDER_PATH)

      self.assertListEqual(actual_download, [])
      self.assertListEqual(actual_upload, [local_file])


   @staticmethod
   def _createConfig(name='stub', local_dir = 'c:\\path', cloud_dir = _CLOUD_FOLDER_PATH, recursive = False):
      return StorageConfig(name, 'sync', '123456', local_dir, cloud_dir, True, recursive)

   def _createLocalFile(self, modified_day = 1, size=2000, cloud_file_path = _CLOUD_FILE_PATH, local_file_path = _LOCAL_FILE_PATH):
      return LocalFileMetadata(self._FILE_NAME, cloud_file_path, local_file_path, datetime.datetime(2023, 8, modified_day, 20, 14, 14), size )

   def _createCloudFile(self, modified_day = 1, size=2000, cloud_file_path = _CLOUD_FILE_PATH):
      return CloudFileMetadata(cloud_file_path, self._FILE_NAME, cloud_file_path, datetime.datetime(2023, 8, modified_day, 20, 14, 14), size, '123321' )

   def _mock_cloud_list(self, files: list[CloudFileMetadata]):
      self._cloudStore.list_folder = Mock(return_value=([], files))

   def _mock_local_list(self, files: list[LocalFileMetadata]):
      self._localStore.list_folder = Mock(return_value=([], files))

   def _mock_cloud_read(self, file: CloudFileMetadata, content = _FILE_CONTENT):
      self._cloudStore.read = Mock(return_value=(content, file))

   def _mock_local_read(self, file: LocalFileMetadata, content = _FILE_CONTENT):
      self._localStore.read = Mock(return_value=(content, file))
