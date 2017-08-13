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

import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from avideo.extractor import (
    gen_extractors,
)


class TestNetRc(unittest.TestCase):
    def test_netrc_present(self):
        for ie in gen_extractors():
            if not hasattr(ie, '_login'):
                continue
            self.assertTrue(
                hasattr(ie, '_NETRC_MACHINE'),
                'Extractor %s supports login, but is missing a _NETRC_MACHINE property' % ie.IE_NAME)


if __name__ == '__main__':
    unittest.main()
