from src.sync.stores.common.path_helper import *


def test_starts_with_slash_when_passed_without_slashes():
    actual = start_with_slash('abc')
    assert actual == '/abc'


def test_starts_with_slash_when_passed_with_slash_inside():
    actual = start_with_slash('a/b/c')
    assert actual == '/a/b/c'


def test_starts_with_slash_when_passed_with_starting_slash_and_multiple_slashes():
    actual = start_with_slash('/a/b/c')
    assert actual == '/a/b/c'


def test_starts_with_slash_when_passed_with_starting_slash():
    actual = start_with_slash('/abc')
    assert actual == '/abc'


def test_starts_with_slash_when_passed_empty():
    actual = start_with_slash('')
    assert actual == '/'


def test_no_starting_slash_when_passed_without_slashes():
    actual = strip_starting_slash('abc')
    assert actual == 'abc'


def test_no_starting_slash_when_passed_with_starting_slash():
    actual = strip_starting_slash('/a/b/c')
    assert actual == 'a/b/c'


def test_no_starting_slash_when_passed_empty():
    actual = strip_starting_slash('')
    assert actual == ''


def test_extension_when_absolute_file_windows_path():
    actual = get_file_extension('C:\\Docs\\File.txt')
    assert actual == '.txt'


def test_extension_when_absolute_file_unix_path():
    actual = get_file_extension('/usr/local/file.txt')
    assert actual == '.txt'


def test_extension_when_relative_unix_path():
    actual = get_file_extension('./rel/file.abcdeg')
    assert actual == '.abcdeg'


def test_empty_extension_when_no_extension():
    actual = get_file_extension('./rel/file')
    assert actual == ''


def test_name_when_absolute_unix_path():
    actual = get_file_name('/usr/local/file.txt')
    assert actual == 'file.txt'


def test_name_when_absolute_windows_path():
    actual = get_file_name('C:\\Docs\\File.txt')
    assert actual == 'File.txt'


def test_name_when_file_name():
    actual = get_file_name('File.txt')
    assert actual == 'File.txt'


def test_empty_name_when_empty():
    actual = get_file_name('')
    assert actual == ''
