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

from mailman_pgp.database import mm_transaction
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.testing.layers import PGPConfigLayer


class TestDiscussionStyle(TestCase):
    layer = PGPConfigLayer

    def test_create(self):
        with mm_transaction():
            mlist = create_list('test@example.com', style_name='pgp-default')

        pgp_list = PGPMailingList.query().filter_by(
                list_id=mlist.list_id).first()

        # Test that we have our PGPMailingList
        self.assertIsNotNone(pgp_list)
        self.assertEqual(pgp_list.mlist, mlist)

        # from LegacyDiscussionStyle
        self.assertEqual(mlist.allow_list_posts, True)
        self.assertEqual(mlist.send_welcome_message, True)
        self.assertEqual(mlist.send_goodbye_message, True)
        self.assertEqual(mlist.anonymous_list, False)
