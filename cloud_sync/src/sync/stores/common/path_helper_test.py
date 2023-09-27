import pytest
from src.sync.stores.common.path_helper import *


@pytest.mark.parametrize("path,expected", [
    ('', '/'),
    ('abc', '/abc'),
    ('/abc', '/abc'),
    ('a/b/c', '/a/b/c'),
    ('/a/b/c', '/a/b/c')])
def test_start_with_slash(path, expected):
    actual = start_with_slash(path)
    assert actual == expected


@pytest.mark.parametrize("path,expected", [
    ('abc', 'abc'),
    ('/a/b/c', 'a/b/c'),
    ('', '')])
def test_strip_starting_slash(path, expected):
    actual = strip_starting_slash(path)
    assert actual == expected


def test_extension_when_absolute_file_windows_path():
    actual = get_file_extension('C:\\Docs\\File.txt')
    assert actual == '.txt'


@pytest.mark.parametrize("path,expected", [
    ('./rel/file', ''),
    ('./rel/file.abcdeg', '.abcdeg'),
    ('/usr/local/file.txt', '.txt'),
    ('', '')])
def test_get_file_extension(path, expected):
    actual = get_file_extension(path)
    assert actual == expected

def test_name_when_absolute_windows_path():
    actual = get_file_name('C:\\Docs\\File.txt')
    assert actual == 'File.txt'


@pytest.mark.parametrize("path,expected", [
    ('/usr/local/file.txt', 'file.txt'),
    ('File.txt', 'File.txt'),
    ('', '')])
def test_file_name(path, expected):
    actual = get_file_name(path)
    assert actual == expected


def test_folder_when_absolute_windows_path():
    actual = get_folder_path('C:\\Docs\\Sub\\File.txt')
    assert actual == 'C:\\Docs\\Sub'


@pytest.mark.parametrize("path,expected", [
    ('/usr/local/sub/file.txt', '/usr/local/sub'),
    ('', '')])
def test_folder_path(path, expected):
    actual = get_folder_path(path)
    assert actual == expected
