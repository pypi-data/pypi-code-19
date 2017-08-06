import generate.generate
import sys
import unittest


class TestParseCommandline(unittest.TestCase):

    def test_length(self):
        sys.argv = ['test', '--length=16']
        options = generate.generate.parse_commandline()
        self.assertTrue(options.length == 16)

    def test_add_digits(self):
        sys.argv = ['test', '--add-digits']
        options = generate.generate.parse_commandline()
        self.assertTrue(options.add_digits)

    def test_add_punctuation(self):
        sys.argv = ['test', '--add-punctuation']
        options = generate.generate.parse_commandline()
        self.assertTrue(options.add_punctuation)

    def test_add_set(self):
        sys.argv = ['test', '--add-set=#$%']
        options = generate.generate.parse_commandline()
        self.assertTrue(options.add_set == [['#$%']])
