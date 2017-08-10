# Copyright (C) 2017 Jan Jancar
#
# This file is a part of the Mailman PGP plugin.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for the PGP posting chain."""
import unittest

from mailman.app.lifecycle import create_list
from mailman.email.message import Message

from mailman_pgp.chains.default import PGPChain
from mailman_pgp.testing.layers import PGPConfigLayer


class TestPGPChain(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.mlist = create_list('test@example.com', style_name='pgp-default')

    def test_cached_links(self):
        chain = PGPChain()
        links = list(chain.get_links(self.mlist, Message(), {}))
        cached_links = list(chain.get_links(self.mlist, Message(), {}))
        for link, cached in zip(links, cached_links):
            self.assertIs(link, cached)
