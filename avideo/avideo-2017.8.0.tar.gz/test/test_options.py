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

# Allow direct execution
import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from avideo.options import _hide_login_info


class TestOptions(unittest.TestCase):
    def test_hide_login_info(self):
        self.assertEqual(_hide_login_info(['-u', 'foo', '-p', 'bar']),
                         ['-u', 'PRIVATE', '-p', 'PRIVATE'])
        self.assertEqual(_hide_login_info(['-u']), ['-u'])
        self.assertEqual(_hide_login_info(['-u', 'foo', '-u', 'bar']),
                         ['-u', 'PRIVATE', '-u', 'PRIVATE'])
        self.assertEqual(_hide_login_info(['--username=foo']),
                         ['--username=PRIVATE'])


if __name__ == '__main__':
    unittest.main()
