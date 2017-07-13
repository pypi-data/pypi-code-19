#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals
import os, sys, unittest

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pkg_root)

from checksumming_io import ChecksummingSink
from tests import TEST_FILE, TEST_FILE_CHECKSUMS


class TestChecksummingSink(unittest.TestCase):

    def check_sums(self, checksums):
        self.assertEqual(checksums['sha1'], TEST_FILE_CHECKSUMS['sha1'])
        self.assertEqual(checksums['sha256'], TEST_FILE_CHECKSUMS['sha256'])
        self.assertEqual(checksums['crc32c'].lower(), TEST_FILE_CHECKSUMS['crc32c'].lower())
        self.assertEqual(checksums['s3_etag'], TEST_FILE_CHECKSUMS['s3_etag'])

    def test_checksums_after_single_write(self):
        sink = ChecksummingSink()
        with open(TEST_FILE, 'rb') as fh:
            data = fh.read()
            sink.write(data)
        sums = sink.get_checksums()
        self.check_sums(sums)

    def test_checksums_after_multiple_write(self):
        sink = ChecksummingSink()
        statinfo = os.stat(TEST_FILE)
        chunk_size = statinfo.st_size // 4
        with open(TEST_FILE, 'rb') as fh:
            while True:
                data = fh.read(chunk_size)
                if not data:
                    break
                sink.write(data)
        sums = sink.get_checksums()
        self.check_sums(sums)

if __name__ == '__main__':
    unittest.main()
