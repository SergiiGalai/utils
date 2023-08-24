import unittest
from unittest.mock import Mock
import logging

from src.stores.mappers import FileMapper
from src.stores.models import CloudFileMetadata

class FileMapperTests(unittest.TestCase):

   def test_result_contains_converted_gfile_with_file_size(self):
      logger = Mock(logging.Logger)
      sut = FileMapper(logger)
      gFile = {'id':'123', 'title':'file1.pdf', 'modifiedDate':'4312', 'mimeType':'stub', 'fileSize': '12345'}

      actual : CloudFileMetadata = sut.convert_GoogleDriveFile_to_CloudFileMetadata(gFile)

      self.assertEqual(actual.id, '123')
      self.assertEqual(actual.name, 'file1.pdf')
      self.assertEqual(actual.client_modified, '4312')
      self.assertEqual(actual.path_display, 'file1.pdf')
      self.assertEqual(actual.size, '12345')

   def test_result_contains_converted_gfile_without_file_size_when_gfile_is_a_shortcut(self):
      logger = Mock(logging.Logger)
      sut = FileMapper(logger)
      gFile = {'id':'123', 'title':'file1.pdf', 'modifiedDate':'4312', 'mimeType':'application/vnd.google-apps.shortcut', 'fileSize': '12345'}

      actual : CloudFileMetadata = sut.convert_GoogleDriveFile_to_CloudFileMetadata(gFile)

      self.assertIsNone(actual.size)
