import datetime
import unittest
from unittest.mock import Mock
import logging
from src.services.content_file_comparer import ContentFileComparer
from src.services.file_comparer import FileComparison
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, LocalFileMetadata

class ContentFileComparerTests(unittest.TestCase):
   _LOCAL_FILE_PATH = 'C:\\Path\\CloudRoot\\sub\\f.txt'
   _CLOUD_FOLDER_PATH = '/Sub'
   _CLOUD_FILE_PATH = '/Sub/f.txt'
   _FILE_NAME = 'f.txt'
   _FILE_CONTENT = '111'

   def setUp(self):
      logger = Mock(logging.Logger)
      self._localStore = Mock(LocalFileStore)
      self._cloudStore = Mock(CloudStore)
      self.sut = ContentFileComparer(self._localStore, self._cloudStore, logger)

   def test_equal_when_files_match_by_metadata(self):
      local_file = self._createLocalFile()
      cloud_file = self._createCloudFile()
      #act
      actual = self.sut.are_equal(local_file, cloud_file)
      self.assertEqual(actual, FileComparison.EQUAL_BY_METADATA)

   def test_equal_when_files_match_by_metadata_and_different_by_content(self):
      local_file = self._createLocalFile()
      self._mock_local_read(local_file)
      cloud_file = self._createCloudFile()
      self._mock_cloud_read(cloud_file, '222')
      #act
      actual = self.sut.are_equal(local_file, cloud_file)
      self.assertEqual(actual, FileComparison.EQUAL_BY_METADATA)

   def test_different_when_files_different_by_name(self):
      local_file = self._createLocalFile()
      cloud_file = self._createCloudFile(name='dif_name')
      #act
      actual = self.sut.are_equal(local_file, cloud_file)
      self.assertEqual(actual, FileComparison.DIF_BY_NAME)

   def test_different_when_files_different_by_size(self):
      local_file = self._createLocalFile()
      cloud_file = self._createCloudFile(size=1000)
      #act
      actual = self.sut.are_equal(local_file, cloud_file)
      self.assertEqual(actual, FileComparison.DIF_BY_SIZE)

   def test_equal_when_files_different_by_modified_date_but_equal_by_content(self):
      local_file = self._createLocalFile()
      cloud_file = self._createCloudFile(3)
      self._mock_local_read(local_file)
      self._mock_cloud_read(cloud_file)
      #act
      actual = self.sut.are_equal(local_file, cloud_file)
      self.assertEqual(actual, FileComparison.EQUAL_BY_CONTENT)

   def test_equal_when_files_different_by_modified_date_and_different_by_content(self):
      local_file = self._createLocalFile()
      cloud_file = self._createCloudFile(3)
      self._mock_local_read(local_file)
      self._mock_cloud_read(cloud_file, 'another_content')
      #act
      actual = self.sut.are_equal(local_file, cloud_file)
      self.assertEqual(actual, FileComparison.DIF_BY_DATE)

   def _createLocalFile(self, modified_day = 1, size=2000, name = _FILE_NAME):
      return LocalFileMetadata(name, self._CLOUD_FILE_PATH, self._LOCAL_FILE_PATH, datetime.datetime(2023, 8, modified_day, 20, 14, 14), size )

   def _createCloudFile(self, modified_day = 1, size=2000, name = _FILE_NAME):
      return CloudFileMetadata(self._CLOUD_FILE_PATH, name, self._CLOUD_FILE_PATH, datetime.datetime(2023, 8, modified_day, 20, 14, 14), size, '123321' )

   def _mock_cloud_read(self, file: CloudFileMetadata, content = _FILE_CONTENT):
      self._cloudStore.read = Mock(return_value=(content, file))

   def _mock_local_read(self, file: LocalFileMetadata, content = _FILE_CONTENT):
      self._localStore.read = Mock(return_value=(content, file))
