import os
import unittest

from os.path import realpath, basename, dirname
from aloe import files

class TestFileFunctions(unittest.TestCase):
    def test_stats(self):
        d = files.fsref('.')
        wd = realpath('.')
        ws = wd.split(os.sep)

        self.assertEqual(d.abspath, wd)
        self.assertEqual(d.dirname, dirname(wd))
        self.assertTrue(d.exists)


if __name__ == '__main__':
    unittest.main()
