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
from mailman.interfaces.pending import IPendable
from mailman.interfaces.workflows import IWorkflow
from mailman.workflows.base import Workflow
from public import public
from zope.interface import implementer

from mailman_pgp.workflows.base import PGPMixin
from mailman_pgp.workflows.key_confirm import ConfirmPubkeyMixin
from mailman_pgp.workflows.key_set import SetPubkeyMixin
from mailman_pgp.workflows.mod_approval import ModeratorKeyRevokeApprovalMixin


class KeyRevokeBase(Workflow, PGPMixin):
    def __init__(self, mlist, pgp_address=None):
        Workflow.__init__(self)
        PGPMixin.__init__(self, mlist, pgp_address)

    @classmethod
    def pendable_class(cls):
        @implementer(IPendable)
        class Pendable(dict):
            PEND_TYPE = cls.name

        return Pendable


@public
@implementer(IWorkflow)
class KeyRevokeWorkflow(KeyRevokeBase, SetPubkeyMixin, ConfirmPubkeyMixin,
                        ModeratorKeyRevokeApprovalMixin):
    name = 'pgp-key-revoke-workflow'
    description = ''
    initial_state = 'prepare'
    save_attributes = (
        'approved',
        'address_key',
        'pubkey_key',
        'pubkey_confirmed'
    )

    def __init__(self, mlist, pgp_address=None, pubkey=None,
                 pubkey_pre_confirmed=False, pre_approved=False):
        KeyRevokeBase.__init__(self, mlist, pgp_address=pgp_address)
        SetPubkeyMixin.__init__(self, pubkey=pubkey)
        ConfirmPubkeyMixin.__init__(self, pre_confirmed=pubkey_pre_confirmed)
        ModeratorKeyRevokeApprovalMixin.__init__(self,
                                                 pre_approved=pre_approved)

    def _step_prepare(self):
        self.push('mod_approval')
        self.push('pubkey_confirmation')
        self.push('pubkey_checks')
