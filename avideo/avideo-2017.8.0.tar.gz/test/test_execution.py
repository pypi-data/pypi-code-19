#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2017 avideo authors (see AUTHORS)

#
#    This file is part of avideo.
#
#    avideo is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    avideo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with avideo.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import unicode_literals

import unittest

import sys
import os
import subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from avideo.utils import encodeArgument

rootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


try:
    _DEV_NULL = subprocess.DEVNULL
except AttributeError:
    _DEV_NULL = open(os.devnull, 'wb')


class TestExecution(unittest.TestCase):
    def test_import(self):
        subprocess.check_call([sys.executable, '-c', 'import avideo'], cwd=rootDir)

    def test_module_exec(self):
        if sys.version_info >= (2, 7):  # Python 2.6 doesn't support package execution
            subprocess.check_call([sys.executable, '-m', 'avideo', '--version'], cwd=rootDir, stdout=_DEV_NULL)

    def test_main_exec(self):
        subprocess.check_call([sys.executable, 'avideo/__main__.py', '--version'], cwd=rootDir, stdout=_DEV_NULL)

    def test_cmdline_umlauts(self):
        p = subprocess.Popen(
            [sys.executable, 'avideo/__main__.py', encodeArgument('ä'), '--version'],
            cwd=rootDir, stdout=_DEV_NULL, stderr=subprocess.PIPE)
        _, stderr = p.communicate()
        self.assertFalse(stderr)


if __name__ == '__main__':
    unittest.main()
