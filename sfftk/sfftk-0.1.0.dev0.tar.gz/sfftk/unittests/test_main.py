#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

"""
test_py

Unit tests for convert subcommand
"""

__author__  = 'Paul K. Korir, PhD'
__email__   = 'pkorir@ebi.ac.uk'
__date__    = '2016-06-10'


import sys
import os
import glob
import unittest
import shlex

from ..core.parser import parse_args
import __init__ as tests
from .. import sff as Main

# sys.path.insert(0, "..")


# redirect sys.stderr/sys.stdout to /dev/null
# from: http://stackoverflow.com/questions/8522689/how-to-temporary-hide-stdout-or-stderr-while-running-a-unittest-in-python
_stderr = sys.stderr
_stdout = sys.stdout
null = open(os.devnull, 'wb')
sys.stdout = null
sys.stderr = null

user = 'test_user'
password = 'test'
host = 'localhost'
port = '4064'


class TestMain_handle_convert(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        # clear all 
        map(os.remove, glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff')))
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        map(os.remove, glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff')))
#     def test_seg(self):
#         """Test that we can convert .seg"""
#         args = parse_args(shlex.split('convert -o {} {}'.format(
#             os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
#             os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.seg')
#             )))
#         Main.handle_convert(args)
#         sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
#         self.assertEqual(len(sff_files), 1)
#     def test_mod(self):
#         """Test that we can convert .mod"""
#         args = parse_args(shlex.split('convert -o {} {}'.format(
#             os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
#             os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod')
#             )))
#         Main.handle_convert(args)
#         sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
#         self.assertEqual(len(sff_files), 1)
#     def test_am(self):
#         """Test that we can convert .am"""
#         args = parse_args(shlex.split('convert -o {} {}'.format(
#             os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
#             os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.am')
#             )))
#         Main.handle_convert(args)
#         sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
#         self.assertEqual(len(sff_files), 1)
#     def test_surf(self):
#         """Test that we can convert .surf"""
#         args = parse_args(shlex.split('convert -o {} {}'.format(
#             os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
#             os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.surf')
#             )))
#         Main.handle_convert(args)
#         sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
#         self.assertEqual(len(sff_files), 1)     
#     def test_read_unknown(self):
#         """Test that unknown fails"""
#         args = parse_args(shlex.split('convert -o {} {}'.format(
#             os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
#             os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.xxx')
#             )))         
#         with self.assertRaises(ValueError):
#             Main.handle_convert(args)
#         sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
#         self.assertEqual(len(sff_files), 0)     
# 
# 
class TestMain_handle_view(unittest.TestCase):
    def test_seg(self):
        """Test that we can view .seg"""
        args = parse_args(shlex.split('view {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.seg')
            )))
        self.assertEqual(0, Main.handle_view(args))
#     
#     def test_read_imod(self):
#         """Test that we can view .mod"""
#         args = parse_args(['view', 'sff/test_data/test_data.mod'])
#         
#         self.assertEqual(0, Main.handle_view(args))
#         
#     def test_read_amira_mesh(self):
#         """Test that we can view .am"""
#         args = parse_args(['view', 'sff/test_data/test_data.am'])
#          
#         self.assertEqual(0, Main.handle_view(args))
#     
#     def test_read_amira_surf(self):
#         """Test that we can view .surf"""
#         args = parse_args(['view', 'sff/test_data/test_data.surf'])
#         
#         self.assertEqual(0, Main.handle_view(args))
#         
#     def test_read_unknown(self):
#         """Test that we cannot view unknown"""
#         args = parse_args(['view', 'sff/test_data/test_data.xxx'])
#         
#         with self.assertRaises(ValueError):
#             Main.handle_view(args)

