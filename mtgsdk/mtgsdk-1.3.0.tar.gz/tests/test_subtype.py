#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of mtgsdk.
# https://github.com/MagicTheGathering/mtg-sdk-python

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2016, Andrew Backes <backes.andrew@gmail.com>

import vcr
import unittest
from mtgsdk import Subtype

class TestSubtype(unittest.TestCase):
    def test_all_returns_subtypes(self):
        with vcr.use_cassette('fixtures/subtypes.yaml'):
            subtypes = Subtype.all()
            
            self.assertTrue(len(subtypes) > 20)
            self.assertTrue('Warrior' in subtypes)