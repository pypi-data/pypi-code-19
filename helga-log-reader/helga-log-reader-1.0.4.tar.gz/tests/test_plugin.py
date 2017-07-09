import sys
from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    from mock import mock
sys.modules['helga.plugins'] = mock.Mock()


from helga_log_reader.plugin import parse_date


class TestResults(TestCase):
    def test_parse_simple(self):
        # to be honest, this mostly just checks syntax of the file
        # this is the most trivial test ever, just to get coverage
        # and fail builds on syntax error etc
        self.assertEqual(1, parse_date('2017-01-01').day)
