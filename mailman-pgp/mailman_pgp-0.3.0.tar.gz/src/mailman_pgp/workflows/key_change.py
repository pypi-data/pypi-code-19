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

from mailman_pgp.config import config
from mailman_pgp.database import transaction
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.workflows.base import PGPMixin
from mailman_pgp.workflows.mod_approval import (
    ModeratorKeyChangeApprovalMixin)

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


class KeyChangeBase(Workflow, PGPMixin):
    save_attributes = (
        'address_key',
        'pubkey_key',
    )

    def __init__(self, mlist, pgp_address=None, pubkey=None):
        Workflow.__init__(self)
        PGPMixin.__init__(self, mlist, pgp_address)
        self.pubkey = pubkey

    @property
    def pubkey_key(self):
        return str(self.pubkey)

    @pubkey_key.setter
    def pubkey_key(self, value):
        self.pubkey, _ = PGPKey.from_blob(value)

    def _pend(self, token_owner, lifetime=None):
        pendings = getUtility(IPendings)
        pendable = self.pendable_class()(
                email=self.pgp_address.email,
                pubkey=str(self.pubkey),
                fingerprint=self.pubkey.fingerprint
        )

        self.token = pendings.add(pendable, lifetime=lifetime)
        self.token_owner = token_owner

    def _step_change_key(self):
        if self.pgp_address is None or self.pubkey is None:
            raise ValueError

        self.push('send_key_confirm_request')

    def _step_send_key_confirm_request(self):
        self._pend(TokenOwner.subscriber,
                   lifetime=config.get_value('misc',
                                             'change_request_lifetime'))
        self.push('receive_confirmation')
        self.save()
        request_address = self.mlist.request_address
        email_address = self.pgp_address.email
        msg = UserNotification(email_address, request_address,
                               'key confirm {}'.format(self.token),
                               CHANGE_CONFIRM_REQUEST.format(
                                       self.pubkey.fingerprint,
                                       self.token))
        PGPWrapper(msg).sign_encrypt(self.pgp_list.key, self.pubkey)

        msg.send(self.mlist)
        raise StopIteration

    def _step_receive_confirmation(self):
        self._set_token(TokenOwner.no_one)

    def _step_do_change(self):
        with transaction():
            self.pgp_address.key = self.pubkey
            self.pgp_address.key_confirmed = True

    @classmethod
    def pendable_class(cls):
        @implementer(IPendable)
        class Pendable(dict):
            PEND_TYPE = cls.name

        return Pendable


@public
@implementer(IWorkflow)
class KeyChangeWorkflow(KeyChangeBase):
    name = 'pgp-key-change-workflow'
    description = ''
    initial_state = 'prepare'

    def _step_prepare(self):
        self.push('do_change')
        self.push('change_key')


@public
@implementer(IWorkflow)
class KeyChangeModWorkflow(KeyChangeBase, ModeratorKeyChangeApprovalMixin):
    name = 'pgp-key-change-mod-workflow'
    description = ''
    initial_state = 'prepare'
    save_attributes = (
        'approved',
        'address_key',
        'pubkey_key'
    )

    def __init__(self, mlist, pgp_address=None, pubkey=None,
                 pre_approved=False):
        KeyChangeBase.__init__(self, mlist, pgp_address, pubkey)
        ModeratorKeyChangeApprovalMixin.__init__(self, pre_approved)

    def _step_prepare(self):
        self.push('do_change')
        self.push('mod_approval')
        self.push('change_key')
