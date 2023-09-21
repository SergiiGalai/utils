import unittest
from src.sync.stores.common.path_helper import PathHelper


class PathHelperTests(unittest.TestCase):

    def test_starts_with_slash_when_passed_without_slashes(self):
        actual = PathHelper.start_with_slash('abc')
        self.assertEqual(actual, '/abc')

    def test_starts_with_slash_when_passed_with_slash_inside(self):
        actual = PathHelper.start_with_slash('a/b/c')
        self.assertEqual(actual, '/a/b/c')

    def test_starts_with_slash_when_passed_with_starting_slash_and_multiple_slashes(self):
        actual = PathHelper.start_with_slash('/a/b/c')
        self.assertEqual(actual, '/a/b/c')

    def test_starts_with_slash_when_passed_with_starting_slash(self):
        actual = PathHelper.start_with_slash('/abc')
        self.assertEqual(actual, '/abc')

    def test_starts_with_slash_when_passed_empty(self):
        actual = PathHelper.start_with_slash('')
        self.assertEqual(actual, '/')

    def test_no_starting_slash_when_passed_without_slashes(self):
        actual = PathHelper.strip_starting_slash('abc')
        self.assertEqual(actual, 'abc')

    def test_no_starting_slash_when_passed_with_starting_slash(self):
        actual = PathHelper.strip_starting_slash('/a/b/c')
        self.assertEqual(actual, 'a/b/c')

    def test_no_starting_slash_when_passed_empty(self):
        actual = PathHelper.strip_starting_slash('')
        self.assertEqual(actual, '')

    def test_extension_when_absolute_file_windows_path(self):
        actual = PathHelper.get_file_extension('C:\\Docs\\File.txt')
        self.assertEqual(actual, '.txt')

    def test_extension_when_absolute_file_unix_path(self):
        actual = PathHelper.get_file_extension('/usr/local/file.txt')
        self.assertEqual(actual, '.txt')

    def test_extension_when_relative_unix_path(self):
        actual = PathHelper.get_file_extension('./rel/file.abcdeg')
        self.assertEqual(actual, '.abcdeg')

    def test_empty_extension_when_no_extension(self):
        actual = PathHelper.get_file_extension('./rel/file')
        self.assertEqual(actual, '')

    def test_name_when_absolute_unix_path(self):
        actual = PathHelper.get_file_name('/usr/local/file.txt')
        self.assertEqual(actual, 'file.txt')

    def test_name_when_absolute_windows_path(self):
        actual = PathHelper.get_file_name('C:\\Docs\\File.txt')
        self.assertEqual(actual, 'File.txt')

    def test_name_when_file_name(self):
        actual = PathHelper.get_file_name('File.txt')
        self.assertEqual(actual, 'File.txt')

    def test_empty_name_when_empty(self):
        actual = PathHelper.get_file_name('')
        self.assertEqual(actual, '')
