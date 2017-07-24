# -*- coding: utf-8 -*-
import unittest
import h5py
from kpfm.util import h5filename, silent_remove


class TestH5Filename(unittest.TestCase):

    def setUp(self):
        self.fname = '.test.h5'
        with h5py.File(self.fname) as fh:
            fh['x'] = 2

    def test_h5_filename(self):
        @h5filename
        def h5print(fh):
            print(fh.values())

        h5print(self.fname)

    def tearDown(self):
        silent_remove(self.fname)
