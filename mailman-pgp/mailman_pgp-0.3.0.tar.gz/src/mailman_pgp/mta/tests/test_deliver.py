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

""""""
import unittest

from mailman.app.lifecycle import create_list
from mailman.interfaces.mailinglist import Personalization
from mailman.interfaces.mta import SomeRecipientsFailed
from mailman.testing.helpers import (specialized_message_from_string as mfs,
                                     subscribe)

from mailman_pgp.database import transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.mta.deliver import deliver
from mailman_pgp.testing.layers import PGPSMTPLayer
from mailman_pgp.testing.pgp import load_key


class TestDeliver(unittest.TestCase):
    layer = PGPSMTPLayer

    def setUp(self):
        with transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
            self.mlist.personalize = Personalization.individual

        self.list_key = load_key('ecc_p256.priv.asc')
        self.pgp_list = PGPMailingList.for_list(self.mlist)
        self.pgp_list.key = self.list_key

        # Make Anne a member of this mailing list.
        self.anne = subscribe(self.mlist, 'Anne', email='anne@example.org')
        self.anne_key = load_key('rsa_1024.priv.asc')

        self.bart = subscribe(self.mlist, 'Bart', email='bart@example.org')
        self.bart_key = load_key('ecc_secp256k1.priv.asc')

        with transaction() as t:
            self.pgp_anne = PGPAddress(self.anne.address)
            self.pgp_anne.key = self.anne_key.pubkey
            self.pgp_anne.key_confirmed = True
            t.add(self.pgp_anne)

        with transaction() as t:
            self.pgp_bart = PGPAddress(self.bart.address)
            self.pgp_bart.key = self.bart_key.pubkey
            self.pgp_bart.key_confirmed = True
            t.add(self.pgp_bart)
        self.msg = mfs("""\
From: anne@example.org
To: test@example.com
Subject: some subject

Some text.
""")

    def test_deliver(self):
        msgdata = dict(recipients=['anne@example.org', 'bart@example.org'],
                       pgp_is_posting=True)
        deliver(self.mlist, self.msg, msgdata)

    def test_deliver_no_key(self):
        with transaction():
            self.pgp_anne.key = None
        msgdata = dict(recipients=['anne@example.org', 'bart@example.org'],
                       pgp_is_posting=True)
        with self.assertRaises(SomeRecipientsFailed) as err:
            deliver(self.mlist, self.msg, msgdata)
        self.assertEqual(err.exception.temporary_failures,
                         ['anne@example.org'])
