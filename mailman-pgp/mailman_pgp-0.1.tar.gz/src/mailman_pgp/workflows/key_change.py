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
from mailman.email.message import UserNotification
from mailman.interfaces.pending import IPendable, IPendings
from mailman.interfaces.subscriptions import TokenOwner
from mailman.interfaces.workflows import IWorkflow
from mailman.workflows.base import Workflow
from pgpy import PGPKey
from public import public
from zope.component import getUtility
from zope.interface import implementer

from mailman_pgp.database import transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.utils import copy_headers
from mailman_pgp.pgp.wrapper import PGPWrapper

CHANGE_CONFIRM_REQUEST = """\
----------
TODO: this is a pgp enabled list.
You requested to change your key.
Reply to this message with this whole text
signed with your supplied key, either inline or PGP/MIME.

Fingerprint: {}
Token: {}
----------
"""


@public
@implementer(IWorkflow)
class KeyChangeWorkflow(Workflow):
    name = 'pgp-key-change-workflow'
    description = ''
    initial_state = 'change_key'
    save_attributes = (
        'address_key',
        'pubkey_key'
    )

    def __init__(self, mlist, pgp_address=None, pubkey=None):
        super().__init__()
        self.mlist = mlist
        self.pgp_list = PGPMailingList.for_list(mlist)
        self.pgp_address = pgp_address
        self.pubkey = pubkey

    @property
    def address_key(self):
        return self.pgp_address.email

    @address_key.setter
    def address_key(self, value):
        self.pgp_address = PGPAddress.for_email(value)
        self.member = self.mlist.regular_members.get_member(value)

    @property
    def pubkey_key(self):
        return str(self.pubkey)

    @pubkey_key.setter
    def pubkey_key(self, value):
        self.pubkey, _ = PGPKey.from_blob(value)

    def _step_change_key(self):
        if self.pgp_address is None or self.pubkey is None:
            raise ValueError

        self.push('send_key_confirm_request')

    def _step_send_key_confirm_request(self):
        pendings = getUtility(IPendings)
        pendable = KeyChangeWorkflow.pendable_class()(
                email=self.pgp_address.email,
                pubkey=str(self.pubkey),
                fingerprint=self.pubkey.fingerprint
        )
        self.token = pendings.add(pendable)
        self.token_owner = TokenOwner.subscriber

        self.push('receive_confirmation')
        self.save()
        request_address = self.mlist.request_address
        email_address = self.pgp_address.email
        msg = UserNotification(email_address, request_address,
                               'key confirm {}'.format(self.token),
                               CHANGE_CONFIRM_REQUEST.format(
                                       self.pubkey.fingerprint,
                                       self.token))
        wrapped = PGPWrapper(msg)
        encrypted = wrapped.sign_encrypt(self.pgp_list.key, self.pubkey)

        msg.set_payload(encrypted.get_payload())
        copy_headers(encrypted, msg, True)
        msg.send(self.mlist)
        raise StopIteration

    def _step_receive_confirmation(self):
        with transaction():
            self.pgp_address.key = self.pubkey
            self.pgp_address.key_confirmed = True

        pendings = getUtility(IPendings)
        if self.token is not None:
            pendings.confirm(self.token)
            self.token = None
            self.token_owner = TokenOwner.no_one

    @classmethod
    def pendable_class(cls):
        @implementer(IPendable)
        class Pendable(dict):
            PEND_TYPE = KeyChangeWorkflow.name

        return Pendable
