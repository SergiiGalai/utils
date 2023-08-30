import datetime
import unittest
from unittest.mock import Mock
import logging
from pydrive.drive import GoogleDriveFile

from src.stores.gdrive_file_mapper import GoogleDriveFileMapper
from src.stores.models import CloudFileMetadata, CloudFolderMetadata

class GoogleDriveFileMapperTests(unittest.TestCase):

   def setUp(self):
      logger = Mock(logging.Logger)
      self.sut = GoogleDriveFileMapper(logger)

   def test_CloudFileMetadata_when_converted_gfile_with_file_size(self):
      gFile = self._createGoogleDriveFile('application/pdf')

      actual : CloudFileMetadata = self.sut.convert_GoogleDriveFile_to_CloudFileMetadata(gFile)

      self.assertEqual(actual.id, '1C7Vb')
      self.assertEqual(actual.name, 'File1.pdf')
      self.assertEqual(actual.client_modified, datetime.datetime(2023, 8, 15, 14, 27, 44))
      self.assertEqual(actual.cloud_path, 'File1.pdf')
      self.assertEqual(actual.size, 12345)
      self.assertEqual(actual.content_hash, '0')

   def test_CloudFileMetadata_with_null_file_size_when_gfile_is_a_shortcut(self):
      gFile = self._createGoogleDriveFile('application/vnd.google-apps.shortcut')

      actual : CloudFileMetadata = self.sut.convert_GoogleDriveFile_to_CloudFileMetadata(gFile)

      self.assertEqual(actual.size, 0)

   def test_CloudFolderMetadata_when_gFolder_passed(self):
      gFile = GoogleDriveFile(metadata={'id':'1C7Vb', 'title':'Settings', 'mimeType':'application/vnd.google-apps.folder'})

      actual : CloudFolderMetadata = self.sut.convert_GoogleDriveFile_to_CloudFolderMetadata(gFile)

      self.assertEqual(actual.id, '1C7Vb')
      self.assertEqual(actual.name, 'Settings')
      self.assertEqual(actual.path_lower, '1C7Vb')
      self.assertEqual(actual.cloud_path, 'Settings')

   @staticmethod
   def _createGoogleDriveFile(mimeType):
      return GoogleDriveFile(metadata={'id':'1C7Vb', 'title':'File1.pdf', 'modifiedDate':'2023-08-15T14:27:44.000Z', 'mimeType':mimeType, 'fileSize': '12345'})
