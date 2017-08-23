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
from datetime import timedelta

from mailman.interfaces.pending import IPendings
from mailman.interfaces.subscriptions import TokenOwner
from mailman.utilities.datetime import now
from mailman.utilities.modules import abstract_component
from mailman.workflows.common import SubscriptionBase
from public import public
from zope.component import getUtility

from mailman_pgp.database import transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList


@public
class PGPMixin:
    def __init__(self, mlist, pgp_address=None):
        self.mlist = mlist
        self.pgp_list = PGPMailingList.for_list(mlist)
        self.pgp_address = pgp_address
        if self.pgp_address is not None:
            self.address = self.pgp_address.address

    @property
    def address_key(self):
        return self.pgp_address.email

    @address_key.setter
    def address_key(self, value):
        self.pgp_address = PGPAddress.for_email(value)
        self.member = self.mlist.regular_members.get_member(value)

    def _step_create_address(self):
        self.pgp_address = PGPAddress.for_address(self.address)
        if self.pgp_address is None:
            with transaction() as t:
                self.pgp_address = PGPAddress(self.address)
                t.add(self.pgp_address)

    def _step_restore_address(self):
        self.pgp_address = PGPAddress.for_address(self.address)

    def _set_token(self, token_owner):
        assert isinstance(token_owner, TokenOwner)
        pendings = getUtility(IPendings)
        if self.token is not None:
            pendings.confirm(self.token)
        self.token_owner = token_owner
        if token_owner is TokenOwner.no_one:
            self.token = None
            return

        pendable = self.pendable_class()(
                list_id=self.mlist.list_id,
                email=self.address.email,
                display_name=self.address.display_name,
                when=now().replace(microsecond=0).isoformat(),
                token_owner=token_owner.name,
        )
        self.token = pendings.add(pendable, timedelta(days=3650))


@public
@abstract_component
class PGPSubscriptionBase(SubscriptionBase, PGPMixin):
    def __init__(self, mlist, subscriber=None, *, pgp_address=None):
        SubscriptionBase.__init__(self, mlist, subscriber)
        PGPMixin.__init__(self, mlist, pgp_address=pgp_address)

    def _step_restore_subscriber(self):
        self._restore_subscriber()
