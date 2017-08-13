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

rootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestVerboseOutput(unittest.TestCase):
    def test_private_info_arg(self):
        outp = subprocess.Popen(
            [
                sys.executable, 'avideo/__main__.py', '-v',
                '--username', 'johnsmith@gmail.com',
                '--password', 'secret',
            ], cwd=rootDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sout, serr = outp.communicate()
        self.assertTrue(b'--username' in serr)
        self.assertTrue(b'johnsmith' not in serr)
        self.assertTrue(b'--password' in serr)
        self.assertTrue(b'secret' not in serr)

    def test_private_info_shortarg(self):
        outp = subprocess.Popen(
            [
                sys.executable, 'avideo/__main__.py', '-v',
                '-u', 'johnsmith@gmail.com',
                '-p', 'secret',
            ], cwd=rootDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sout, serr = outp.communicate()
        self.assertTrue(b'-u' in serr)
        self.assertTrue(b'johnsmith' not in serr)
        self.assertTrue(b'-p' in serr)
        self.assertTrue(b'secret' not in serr)

    def test_private_info_eq(self):
        outp = subprocess.Popen(
            [
                sys.executable, 'avideo/__main__.py', '-v',
                '--username=johnsmith@gmail.com',
                '--password=secret',
            ], cwd=rootDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sout, serr = outp.communicate()
        self.assertTrue(b'--username' in serr)
        self.assertTrue(b'johnsmith' not in serr)
        self.assertTrue(b'--password' in serr)
        self.assertTrue(b'secret' not in serr)

    def test_private_info_shortarg_eq(self):
        outp = subprocess.Popen(
            [
                sys.executable, 'avideo/__main__.py', '-v',
                '-u=johnsmith@gmail.com',
                '-p=secret',
            ], cwd=rootDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sout, serr = outp.communicate()
        self.assertTrue(b'-u' in serr)
        self.assertTrue(b'johnsmith' not in serr)
        self.assertTrue(b'-p' in serr)
        self.assertTrue(b'secret' not in serr)


if __name__ == '__main__':
    unittest.main()
