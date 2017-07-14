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
from mailman.interfaces.usermanager import IUserManager
from public import public
from zope.component import getUtility

from mailman_pgp.database import mm_transaction
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.workflows.subscription import (
    ConfirmModerationSubscriptionPolicy, ConfirmSubscriptionPolicy,
    ModerationSubscriptionPolicy, OpenSubscriptionPolicy)


@public
class TestSubscriptionWorkflows(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
        self.sender = getUtility(IUserManager).create_address(
                'rsa-1024b@example.org')

    def test_open_policy(self):
        workflow = OpenSubscriptionPolicy(self.mlist, self.sender)
        next(workflow)

    def test_confirm_policy(self):
        workflow = ConfirmSubscriptionPolicy(self.mlist, self.sender)
        next(workflow)

    def test_moderation_policy(self):
        workflow = ModerationSubscriptionPolicy(self.mlist, self.sender)
        next(workflow)

    def test_confirm_moderation_policy(self):
        workflow = ConfirmModerationSubscriptionPolicy(self.mlist, self.sender)
        next(workflow)
