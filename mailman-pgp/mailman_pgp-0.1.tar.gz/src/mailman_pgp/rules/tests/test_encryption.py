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
from unittest import TestCase

from mailman.app.lifecycle import create_list
from mailman.testing.helpers import specialized_message_from_string as mfs

from mailman_pgp.config import mm_config
from mailman_pgp.database import mm_transaction
from mailman_pgp.rules.encryption import Encryption
from mailman_pgp.testing.layers import PGPConfigLayer


class TestEncryptionRule(TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.rule = Encryption()
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')

    def test_has_rule(self):
        self.assertIn(Encryption.name, mm_config.rules.keys())

    def test_matches(self):
        msgdata = {'pgp_moderate': True}
        msg = mfs("""\
From: anne@example.com
To: test@example.com

""")
        self.assertTrue(self.rule.check(self.mlist, msg, msgdata))
        msgdata['pgp_moderate'] = False
        self.assertFalse(self.rule.check(self.mlist, msg, msgdata))
        self.assertFalse(self.rule.check(self.mlist, msg, {}))
