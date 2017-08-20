#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit test for pattern"""

import sys
import unittest
from os.path import dirname, realpath

from pm.pattern import (parse, mutant_to_str, PlainPattern, TranslatedPattern)


class RoutineTestForFuncs(unittest.TestCase):
    """Routine test."""

    def test_parse(self):
        """parse shoult return PlainPattern obj containing the right mutant tuple"""

        seq = "ACGCCAAGGGT-"
        stdseq = "ATG-CAAGGGTT"
        ex_pattern_dict = {2: ('T', 'C'), 4: ('-', 'C'), 12: ('T', '-')}

        r = parse(seq, stdseq)
        self.assertIsInstance(r, PlainPattern)
        self.assertEqual(r.mutants, ex_pattern_dict)

        ex_pattern_list = [(2, 'T', 'C'), (4, '-', 'C'), (12, 'T', '-')]

    def test_parse_with_translate_is_True(self):
        """parse should return TranslatedPattern obj containing the right mutant tuple when translate=Ture"""

        _aa_pos= " 1   2   3   4   5   6   7   8"
        _std_aa= " M   T   R   V   L   *   Y   R"
        _aa =    " T   P   R   V   L   Y   -   R"
        _nt_pos= "123 456 789 012 345 678 901 234"
        _pm_line=" ?  ?             ?   ? ? ? ? ?"
        stdseq = "ATG ACA AGG GTT UUG TAG TAC CGT".replace(' ', '')
        seq =    "ACG CCA AGG GTT UUA TAC -A- AGA".replace(' ', '')
        obj = parse(seq, stdseq, translate=True)
        self.assertIsInstance(obj, TranslatedPattern)

        ex_nt_dict = {2: ('T', 'C'), 4: ('A', 'C'), 15: ('G', 'A'), 
                      18: ('G', 'C'), 19: ('T', '-'), 21: ('C', '-'), 
                      22: ('C', 'A'), 24: ('T', 'A')}
        ex_aa_dict = {1: ('M', 'T'), 2: ('T', 'P'), 5: ('L', 'L'), 
                      6: ('*', 'Y'), 7: ('Y', '-'), 8: ('R', 'R')}
        ex_assoc_dict = {2: 1, 4: 2, 15: 5, 18: 6, 19: 7, 21: 7, 22: 8, 24: 8}

        self.assertEqual(obj.mutants, ex_nt_dict)
        self.assertEqual(obj.aa_mutants, ex_aa_dict)
        self.assertEqual(obj.assoc_dict, ex_assoc_dict)

        ex_pattern_list = [((2, 'T', 'C'), (1, 'M', 'T')),
                           ((4, 'A', 'C'), (2, 'T', 'P')),
                           ((15, 'G', 'A'), (5, 'L', 'L')),
                           ((18, 'G', 'C'), (6, '*', 'Y')),
                           ((19, 'T', '-'), (7, 'Y', '-')),
                           ((21, 'C', '-'), (7, 'Y', '-')),
                           ((22, 'C', 'A'), (8, 'R', 'R')),
                           ((24, 'T', 'A'), (8, 'R', 'R'))
                          ]
        self.assertEqual(obj.list(), ex_pattern_list)

    def test_mutant_to_str(self):
        """mutant_to_str should return the right result"""

        self.assertEqual('2T>C', mutant_to_str(2, 'T', 'C'))
        self.assertEqual('4insC', mutant_to_str(4, '-', 'C'))
        self.assertEqual('12delT', mutant_to_str(12, 'T', '-'))
        self.assertEqual('20A=A', mutant_to_str(20, 'A', 'A'))


class ErrorTestFor_parse(unittest.TestCase):

    def test_parse_with_bar_in_seq(self):
        """parse with translate=True should raise TranslationError when seq or stdseq 
        contains untranslatable codon(except the gaps identifer '-')"""

        from pm.pattern import TranslationError

        stdseq = "ATGACAAGGGTTUUGTAGTAC"
        seq = "ACGCCAAGGGTTUUATACTAP"
        with self.assertRaises(TranslationError):
            parse(seq, stdseq, True)


if __name__ == '__main__':
    unittest.main()
