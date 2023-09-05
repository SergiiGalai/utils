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

   def test_2_files_when_converterd_gfiles_with_2_files_in_the_root(self):
      dbx_file1 = self._creatDropboxFile('f1.pdf', 'f1.pdf', 'f1.pdf')
      dbx_file2 = self._creatDropboxFile('F2.pdf', 'F2.pdf', 'f2.pdf')
      expected1 = self._createCloudFileMetadata('f1.pdf', 'f1.pdf', 'f1.pdf')
      expected2 = self._createCloudFileMetadata('F2.pdf', 'F2.pdf', 'f2.pdf')
      #act
      actual_dirs, actual_files = self.sut.convert_dropbox_entries_to_FileMetadatas([dbx_file1, dbx_file2])
      #assert
      self.assertEqual(actual_dirs, [])
      self.assertEqual(actual_files, [expected1, expected2])

   def test_2_files_when_converterd_gfiles_with_2_files_in_the_subfolder(self):
      dbx_file1 = self._creatDropboxFile('f1.pdf', '/Path/f1.pdf', '/path/f1.pdf')
      dbx_file2 = self._creatDropboxFile('F2.pdf', '/Path/F2.pdf', '/path/f2.pdf')
      expected1 = self._createCloudFileMetadata('f1.pdf', '/Path/f1.pdf', '/path/f1.pdf')
      expected2 = self._createCloudFileMetadata('F2.pdf', '/Path/F2.pdf', '/path/f2.pdf')
      #act
      actual_dirs, actual_files = self.sut.convert_dropbox_entries_to_FileMetadatas([dbx_file1, dbx_file2])
      #assert
      self.assertEqual(actual_dirs, [])
      self.assertEqual(actual_files, [expected1, expected2])

   def test_result_contains_converted_dropbox_file(self):
      dbx_md = self._creatDropboxFile()
      expected = self._createCloudFileMetadata()
      #act
      actual = self.sut.convert_DropboxFileMetadata_to_CloudFileMetadata(dbx_md)
      #assert
      self.assertEqual(actual, expected)

   def test_result_contains_converted_dropbox_folder(self):
      dbx_dir = self._creatDropboxFolder()
      expected = self._createCloudFolderMetadata()
      #act
      actual = self.sut.convert_DropboxFolderMetadata_to_CloudFolderMetadata(dbx_dir)
      #assert
      self.assertEqual(actual, expected)

   DEFAULT_NAME = 'File1.pdf'
   DEFAULT_PATH_DISPLAY = '/Path/File1.pdf'
   DEFAULT_PATH_LOWER = '/path/file1.pdf'

   @staticmethod
   def _creatDropboxFile(name=DEFAULT_NAME, path_display=DEFAULT_PATH_DISPLAY, path_lower=DEFAULT_PATH_LOWER):
      result = Mock(dropbox.files.FileMetadata)
      result.id = 'id:AABBCC'
      result.name = name
      result.path_display = path_display
      result.path_lower = path_lower
      result.client_modified = datetime.datetime(2017, 6, 13, 20, 16, 8)
      result.content_hash = '1234567890'
      result.size = 12345
      return result

   @staticmethod
   def _createCloudFileMetadata(name=DEFAULT_NAME, cloud_path=DEFAULT_PATH_DISPLAY, path_lower=DEFAULT_PATH_LOWER):
      return CloudFileMetadata(name, cloud_path, datetime.datetime(2017, 6, 13, 20, 16, 8), 12345, path_lower, '1234567890')

   @staticmethod
   def _creatDropboxFolder(name='SubPath', path_display='/Path/SubPath', path_lower='/path/subpath'):
      result = Mock(dropbox.files.FolderMetadata)
      result.id = 'id:AABBCC'
      result.path_display = path_display
      result.path_lower = path_lower
      result.name = name
      return result

   @staticmethod
   def _createCloudFolderMetadata(name='SubPath', cloud_path='/Path/SubPath', path_lower='/path/subpath'):
      return CloudFolderMetadata(path_lower, name, path_lower, cloud_path)
