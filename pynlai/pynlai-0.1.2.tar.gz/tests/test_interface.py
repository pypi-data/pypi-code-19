#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
test_interface
--------------

unit tests for pynlai interface module
'''


from collections import OrderedDict
import six
import unittest

import en_core_web_sm as en

import pynlai
from pynlai import core
from pynlai import views

from .shared import *


class TestInterface(unittest.TestCase):

    def setUp(self):
        self.nl = 'Test the nl_function with value set to 1.'
        self.trigger = pynlai.Trigger(
            core.to_obj,
            views._DEP_TOKEN['HR'],
            OrderedDict([
                ('lemma_', 'nl_function'),
                ('dep_', 'dobj'),
                ('head.lemma_', 'test'),
                ('head.pos_', 'VERB'),
            ]),
        )
        def arg_callback(sent):
            ents = core.to_ent(doc=sent, nlp=nlp).pop()
            view = core.create_view(ents, views._ENT_SPAN['HR'])
            return dict([('value', view['text'])])
        self.argument = pynlai.Argument(
            core.to_nc,
            views._DEP_SPAN['HR'],
            OrderedDict([
                ('root.lemma_', 'value'),
            ]),
            arg_callback,
        )
        @pynlai.nl_function(
            self.trigger,
            self.argument,
        )
        def nl_function(value):
            return value
        self.nl_function = nl_function

    def tearDown(self):
        pass

    def test_decorator(self):
        self.assertTrue(hasattr(self.nl_function, '__pynlai_triggers'))

    def test_run(self):
        r = pynlai.run(doc=self.nl, nlp=nlp, obj=self)
        self.assertEqual(r, u'1')
