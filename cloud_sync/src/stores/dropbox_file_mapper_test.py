import datetime
import unittest
from unittest.mock import Mock
import logging
import dropbox

from src.stores.dropbox_file_mapper import DropboxFileMapper
from src.stores.models import CloudFileMetadata, CloudFolderMetadata

class DropboxFileMapperTests(unittest.TestCase):

   def setUp(self):
      logger = Mock(logging.Logger)
      self.sut = DropboxFileMapper(logger)

   def test_result_contains_converted_dropbox_file(self):
      dbx_md = Mock(dropbox.files.FileMetadata)
      dbx_md.id = 'id:AABBCC'
      dbx_md.name = 'File1.pdf'
      dbx_md.path_display = '/Path/File1.pdf'
      dbx_md.path_lower = '/path/file1.pdf'
      dbx_md.client_modified = datetime.datetime(2017, 6, 13, 20, 16, 8)
      dbx_md.content_hash = '1234567890'
      dbx_md.size = 12345

      actual : CloudFileMetadata = self.sut.convert_DropboxFileMetadata_to_CloudFileMetadata(dbx_md)

      self.assertEqual(actual.id, '/path/file1.pdf')
      self.assertEqual(actual.name, 'File1.pdf')
      self.assertEqual(actual.cloud_path, '/Path/File1.pdf')
      self.assertEqual(actual.client_modified, datetime.datetime(2017, 6, 13, 20, 16, 8))
      self.assertEqual(actual.size, 12345)
      self.assertEqual(actual.content_hash, '1234567890')

   def test_result_contains_converted_dropbox_folder(self):
      dbx_dir = Mock(dropbox.files.FolderMetadata)
      dbx_dir.id = 'id:AABBCC'
      dbx_dir.path_display = '/Path/SubPath'
      dbx_dir.path_lower = '/path/subpath'
      dbx_dir.name = 'SubPath'

      actual : CloudFolderMetadata = self.sut.convert_DropboxFolderMetadata_to_CloudFolderMetadata(dbx_dir)

      self.assertEqual(actual.id, '/path/subpath')
      self.assertEqual(actual.name, 'SubPath')
      self.assertEqual(actual.path_lower, '/path/subpath')
      self.assertEqual(actual.cloud_path, '/Path/SubPath')
