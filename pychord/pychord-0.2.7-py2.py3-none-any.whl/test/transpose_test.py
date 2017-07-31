#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from pychord import Chord


class TestChordCreations(unittest.TestCase):

    def test_transpose_zero(self):
        c = Chord("Am")
        c.transpose(0)
        self.assertEqual(c._root, "A")
        self.assertEqual(c._quality._quality, "m")

    def test_transpose_positive(self):
        c = Chord("Am")
        c.transpose(3)
        self.assertEqual(c._root, "C")
        self.assertEqual(c._quality._quality, "m")

    def test_transpose_negative(self):
        c = Chord("Am")
        c.transpose(-4)
        self.assertEqual(c._root, "F")
        self.assertEqual(c._quality._quality, "m")

    def test_transpose_slash(self):
        c = Chord("Am7/G")
        c.transpose(3)
        self.assertEqual(c._root, "C")
        self.assertEqual(c._quality._quality, "m7")
        self.assertEqual(c._on, "Bb")

    def test_invalid_transpose_type(self):
        c = Chord("Am")
        self.assertRaises(TypeError, c.transpose, ("A"))

if __name__ == '__main__':
    unittest.main()
