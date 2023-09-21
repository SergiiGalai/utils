import unittest
from unittest.mock import Mock
import logging
from src.sync.stores.local.mime_type_provider import MimeTypeProvider


class MimeTypeProviderTest(unittest.TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self._sut = MimeTypeProvider(logger)

    def test_mime_for_known_type(self):
        actual = self._sut.get_by_extension('.xls')
        self.assertEqual(actual, 'application/vnd.ms-excel')

    def test_mime_for_camel_case_extension(self):
        actual = self._sut.get_by_extension('.Config')
        self.assertEqual(actual, 'application/xml')

    def test_plain_text_for_unknown_extension(self):
        actual = self._sut.get_by_extension('.unknown')
        self.assertEqual(actual, 'text/plain')
