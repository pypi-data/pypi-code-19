#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from clds_pipeline import clds_pipeline
from clds_pipeline.wordnet import WordNetExpander

class TestClds_pipeline(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_something(self):
        pass

    def test_synset_names(self):
        expander = WordNetExpander()
        expanded_nouns = expander.noun('dog')
        self.assertEqual(
            ['dog', 'domestic_dog', 
             'Canis_familiaris', 'frump', 'cad'],
            list(expanded_nouns)
        )

        expanded_verbs = expander.verb('run')
        self.assertEqual(
            ['run', 'scat', 'scarper', 'turn_tail', 'lam'],
            list(expanded_verbs)
        )

        expanded_adj = expander.adj('shiny')
        self.assertEqual(
            ['glistening', 'glossy', 'lustrous', 'sheeny', 'shiny'],
            list(expanded_adj)
        )

        expanded_adv = expander.adv('fast')
        self.assertEqual(
            ['fast', 'tight'],
            list(expanded_adv)
        )
        
