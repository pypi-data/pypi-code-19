#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
test_core
---------

unit tests for pynlai package core functionality
'''


import six
import unittest

from click.testing import CliRunner
import en_core_web_sm as en
from spacy.tokens import Doc

from pynlai import cli
from pynlai import core
from pynlai import views

from .shared import *


class TestCore(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    def test_nlp_preprocess(self):
        try:
            core.to_pos('Test.', nlp)
        except ValueError as e:
            self.assertTrue('pass args by name' in str(e))
        try:
            core.to_pos(nlp=nlp)
        except ValueError as e:
            self.assertTrue('must pass `doc`' in str(e))
        try:
            core.to_pos(doc='Test.')
        except ValueError as e:
            self.assertTrue('must pass `nlp`' in str(e))
        try:
            core.to_pos(doc=object(), nlp=nlp)
        except ValueError as e:
            self.assertTrue('arg of Doc or text type' in str(e))
        r = core.to_pos(doc=Doc(nlp.vocab), nlp=nlp)
        six.assertCountEqual(self, r, [])

    def test_create_view(self):
        class View(object):
            a = 1
            b = 2
            c = 3
        o = View()
        v = ('a', 'c')
        r = core.create_view(o, v)
        e = {'a': 1, 'c': 3}
        self.assertDictEqual(r, e)

    def test_to_ent(self):
        s = 'London is a big city in the United Kingdom.'
        v = views._ENT_SPAN['HR']
        r = [core.create_view(e, v) for e in core.to_ent(doc=s, nlp=nlp)]
        ents = [
            {'text': 'London', 'label_': 'GPE'},
            {'text': 'the United Kingdom', 'label_': 'GPE'},
        ]
        for i in range(0, 2):
            self.assertDictEqual(r[i], ents[i])

    def test_to_nc(self):
        s = 'I like green eggs and ham.'
        v = views._DEP_SPAN['HR']
        r = [core.create_view(e, v) for e in core.to_nc(doc=s, nlp=nlp)]
        ncs = [
            {
                'text': 'I',
                'root.orth_': 'I',
                'root.lemma_': '-PRON-',
                'root.dep_': 'nsubj',
                'root.head.orth_': 'like',
                'root.head.lemma_': 'like',
                'root.head.pos_': 'VERB',
            },
            {
                'text': 'green eggs',
                'root.orth_': 'eggs',
                'root.lemma_': 'egg',
                'root.dep_': 'dobj',
                'root.head.orth_': 'like',
                'root.head.lemma_': 'like',
                'root.head.pos_': 'VERB',
            },
            {
                'text': 'ham',
                'root.orth_': 'ham',
                'root.lemma_': 'ham',
                'root.dep_': 'conj',
                'root.head.orth_': 'eggs',
                'root.head.lemma_': 'egg',
                'root.head.pos_': 'NOUN',
            },
        ]
        six.assertCountEqual(self, r, ncs)

    def test_to_obj(self):
        s = 'I like green eggs and ham,'
        v = views._DEP_TOKEN['HR']
        r = [core.create_view(e, v) for e in core.to_obj(doc=s, nlp=nlp)]
        objs = [
            {
                'orth_': 'eggs',
                'lemma_': 'egg',
                'dep_': 'dobj',
                'head.orth_': 'like',
                'head.lemma_': 'like',
                'head.pos_': 'VERB',
            },
        ]
        six.assertCountEqual(self, r, objs)

    def test_to_pos(self):
        s = 'This is a test sentence.'
        v = views._POS_TOKEN['HR']
        r = [core.create_view(e, v) for e in core.to_pos(doc=s, nlp=nlp)]
        pos = [
            {'orth_': 'This', 'pos_': 'DET', 'lemma_': 'this'},
            {'orth_': 'is', 'pos_': 'VERB', 'lemma_': 'be'},
            {'orth_': 'a', 'pos_': 'DET', 'lemma_': 'a'},
            {'orth_': 'test', 'pos_': 'NOUN', 'lemma_': 'test'},
            {'orth_': 'sentence', 'pos_': 'NOUN', 'lemma_': 'sentence'},
            {'orth_': '.', 'pos_': 'PUNCT', 'lemma_': '.'},
        ]
        six.assertCountEqual(self, r, pos)

    def test_to_sub(self):
        s = 'I like green eggs and ham,'
        v = views._DEP_TOKEN['HR']
        r = [core.create_view(e, v) for e in core.to_sub(doc=s, nlp=nlp)]
        subs = [
            {
                'orth_': 'I',
                'lemma_': '-PRON-',
                'dep_': 'nsubj',
                'head.orth_': 'like',
                'head.lemma_': 'like',
                'head.pos_': 'VERB',
            },
        ]
        six.assertCountEqual(self, r, subs)
