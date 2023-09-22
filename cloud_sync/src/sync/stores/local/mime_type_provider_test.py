import pytest
from src.sync.stores.local.mime_type_provider import MimeTypeProvider


@pytest.fixture
def sut():
    return MimeTypeProvider()

def test_mime_for_known_type(sut: MimeTypeProvider):
    actual = sut.get_by_extension('.xls')
    assert actual == 'application/vnd.ms-excel'

def test_mime_for_camel_case_extension(sut: MimeTypeProvider):
    actual = sut.get_by_extension('.Config')
    assert actual == 'application/xml'

def test_plain_text_for_unknown_extension(sut: MimeTypeProvider):
    actual = sut.get_by_extension('.unknown')
    assert actual == 'text/plain'
