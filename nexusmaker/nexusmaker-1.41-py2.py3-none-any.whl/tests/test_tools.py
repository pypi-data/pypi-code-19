#!/usr/bin/env python3
#coding=utf-8
"""..."""
__author__ = 'Simon J. Greenhill <simon@simon.net.nz>'
__copyright__ = 'Copyright (c) 2016 Simon J. Greenhill'
__license__ = 'New-style BSD'

import unittest

from nexusmaker.tools import slugify, parse_word, natsort

class Test_NatSort(unittest.TestCase):
    def test(self):
        self.assertEqual(natsort(['b', 'a']), ['a', 'b'])
        self.assertEqual(natsort(['c', '1']), ['1', 'c'])
        self.assertEqual(natsort(['52', '1']), ['1', '52'])
        self.assertEqual(natsort(['54', '53']), ['53', '54'])
        self.assertEqual(natsort(['53', '54']), ['53', '54'])


class Test_Slugify(unittest.TestCase):
    def test_brackets(self):
        self.assertEqual(slugify('Banggai (W.dialect)'), 'Banggai_Wdialect')

    def test_dash(self):
        self.assertEqual(slugify('Aklanon - Bisayan'), 'Aklanon_Bisayan')

    def test_accents(self):
        self.assertEqual(slugify('Gimán'), 'Giman')
        self.assertEqual(slugify('Hanunóo'), 'Hanunoo')

    def test_colon(self):
        self.assertEqual(slugify('Kakiduge:n Ilongot'), 'Kakidugen_Ilongot')

    def test_slash(self):
        self.assertEqual(slugify('Angkola / Mandailin'), 'Angkola_Mandailin')
    
    def test_apostrophe(self):
        self.assertEqual(slugify('V’ënen Taut'), 'Venen_Taut')


class TestParseWord(unittest.TestCase):
    def test_One_1(self):
        self.assertEqual(parse_word("One_1"), ("One", "1"))
    
    def test_One_13(self):
        self.assertEqual(parse_word("One_13"), ("One", "13"))

    def test_One_u_21(self):
        self.assertEqual(parse_word("One_u_21"), ("One", "u_21"))

    def test_One_u21(self):
        self.assertEqual(parse_word("One_u21"), ("One", "u21"))

    def test_One_Hundred_16(self):
        self.assertEqual(parse_word("One_Hundred_16"), ("One_Hundred", "16"))
    
    def test_One_Hundred_u_16(self):
        self.assertEqual(parse_word("One_Hundred_u_16"), ("One_Hundred", "u_16"))

    def test_One_Hundred_u16(self):
        self.assertEqual(parse_word("One_Hundred_u16"), ("One_Hundred", "u16"))

    def test_Eight_u_3569(self):
        self.assertEqual(parse_word("Eight_u_3569"), ("Eight", "u_3569"))

    def test_Eight_u3569(self):
        self.assertEqual(parse_word("Eight_u3569"), ("Eight", "u3569"))
        
    def test_correct_true_u_5631(self):
        self.assertEqual(parse_word("correct_true_u_5631"), ("correct_true", "u_5631"))

    def test_correct_true_u5631(self):
        self.assertEqual(parse_word("correct_true_u5631"), ("correct_true", "u5631"))

    def test_to_tie_up_fasten_u_5685(self):
        self.assertEqual(parse_word("to_tie_up_fasten_u_5685"), ("to_tie_up_fasten", "u_5685"))

    def test_to_tie_up_fasten_u5685(self):
        self.assertEqual(parse_word("to_tie_up_fasten_u5685"), ("to_tie_up_fasten", "u5685"))
    
    def test_error(self):
        with self.assertRaises(ValueError):
            parse_word("hand")

