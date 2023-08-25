import datetime
import unittest
from unittest.mock import Mock
import logging
import dropbox
from pydrive.drive import GoogleDriveFile

from src.stores.file_mappers import DropboxFileMapper, GoogleDriveFileMapper
from src.stores.models import CloudFileMetadata, CloudFolderMetadata

class GoogleDriveFileMapperTests(unittest.TestCase):

   @staticmethod
   def _createGoogleDriveFile(mimeType):
      return GoogleDriveFile(metadata={'id':'1C7Vb', 'title':'File1.pdf', 'modifiedDate':'2023-08-15T14:27:44.000Z', 'mimeType':mimeType, 'fileSize': '12345'})

   def setUp(self):
      logger = Mock(logging.Logger)
      self.sut = GoogleDriveFileMapper(logger)

   def test_CloudFileMetadata_when_converted_gfile_with_file_size(self):
      gFile = self._createGoogleDriveFile('application/pdf')

      actual : CloudFileMetadata = self.sut.convert_GoogleDriveFile_to_CloudFileMetadata(gFile)

      self.assertEqual(actual.id, '1C7Vb')
      self.assertEqual(actual.name, 'File1.pdf')
      self.assertEqual(actual.client_modified, '2023-08-15T14:27:44.000Z')
      self.assertEqual(actual.path_display, 'File1.pdf')
      self.assertEqual(actual.size, '12345')

   def test_CloudFileMetadata_with_null_file_size_when_gfile_is_a_shortcut(self):
      gFile = self._createGoogleDriveFile('application/vnd.google-apps.shortcut')

      actual : CloudFileMetadata = self.sut.convert_GoogleDriveFile_to_CloudFileMetadata(gFile)

      self.assertIsNone(actual.size)

   def test_CloudFolderMetadata_when_gFolder_passed(self):
      gFile = GoogleDriveFile(metadata={'id':'1C7Vb', 'title':'Settings', 'mimeType':'application/vnd.google-apps.folder'})

      actual : CloudFolderMetadata = self.sut.convert_GoogleDriveFile_to_CloudFolderMetadata(gFile)

      self.assertEqual(actual.id, '1C7Vb')
      self.assertEqual(actual.name, 'Settings')
      self.assertEqual(actual.path_lower, '1C7Vb')
      self.assertEqual(actual.path_display, 'Settings')


class DropboxFileMapperTests(unittest.TestCase):

   def setUp(self):
      logger = Mock(logging.Logger)
      self.sut = DropboxFileMapper(logger)

   def test_result_contains_converted_dropbox_file(self):
      dbx_md = Mock(dropbox.files.FileMetadata)
      dbx_md.id = 'id:AABBCC'
      dbx_md.name = 'File1.pdf'
      dbx_md.path_display = '/Path/File1.pdf'
      dbx_md.client_modified = datetime.datetime(2017, 6, 13, 20, 16, 8)
      dbx_md.size = 12345

      actual : CloudFileMetadata = self.sut.convert_DropboxFileMetadata_to_CloudFileMetadata(dbx_md)

      self.assertEqual(actual.id, '/Path/File1.pdf')
      self.assertEqual(actual.name, 'File1.pdf')
      self.assertEqual(actual.path_display, '/Path/File1.pdf')
      self.assertEqual(actual.client_modified, datetime.datetime(2017, 6, 13, 20, 16, 8))
      self.assertEqual(actual.size, 12345)

   def test_result_contains_converted_dropbox_folder(self):
      dbx_dir = Mock(dropbox.files.FolderMetadata)
      dbx_dir.id = 'id:AABBCC'
      dbx_dir.path_display = '/Path/SubPath'
      dbx_dir.path_lower = '/path/subpath'
      dbx_dir.name = 'SubPath'

      actual : CloudFolderMetadata = self.sut.convert_DropboxFolderMetadata_to_CloudFolderMetadata(dbx_dir)

      self.assertEqual(actual.id, '/Path/SubPath')
      self.assertEqual(actual.name, 'SubPath')
      self.assertEqual(actual.path_lower, '/path/subpath')
      self.assertEqual(actual.path_display, '/Path/SubPath')
