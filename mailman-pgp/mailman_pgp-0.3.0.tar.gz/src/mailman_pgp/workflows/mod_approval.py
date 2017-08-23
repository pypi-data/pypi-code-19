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
from mailman.interfaces.pending import IPendings
from mailman.interfaces.subscriptions import TokenOwner
from public import public
from zope.component import getUtility

from mailman_pgp.pgp.mime import MIMEWrapper

SUBSCRIPTION_MOD_REQUEST = """\
----------
TODO: this is a pgp enabled list.
A user with address {address} requested subscription.
The key is attached to this message.

Fingerprint: {fingerprint}
----------
"""

KEY_CHANGE_MOD_REQUEST = """\
----------
TODO: this is a pgp enabled list.
A subscriber with address {address} requested a change of his key.
The new key is attached to this message.

Old key fingerprint: {old_fpr}
New key fingerprint: {new_fpr}
----------
"""

KEY_REVOKE_MOD_REQUEST = """\
----------
TODO: this is a pgp enabled list.
A subscriber with address {address} revoked a part of his key,
which made it unusable and needs to be reset. The subscriber
supplied a new key. The new key is attached to this message.

Old key fingerprint: {old_fpr}
New key fingerprint: {new_fpr}
----------
"""


class ModeratorApprovalMixin:
    def __init__(self, pre_approved=False):
        self.approved = pre_approved

    def _step_mod_approval(self):
        if not self.approved:
            self.push('get_approval')

    def _step_get_approval(self):
        self._pend(TokenOwner.moderator)
        self.push('receive_mod_confirmation')
        self.save()

        name = self._request_name
        body = self._request_body

        if self.mlist.admin_immed_notify:
            subject = 'New {} request from {}'.format(name,
                                                      self.pgp_address.email)
            msg = UserNotification(
                    self.mlist.owner_address, self.mlist.owner_address,
                    subject, body, self.mlist.preferred_language)
            MIMEWrapper(msg).attach_keys(self.pubkey)
            msg.send(self.mlist)
        raise StopIteration

    def _step_receive_mod_confirmation(self):
        pendings = getUtility(IPendings)
        if self.token is not None:
            pendings.confirm(self.token)
            self.token = None
            self.token_owner = TokenOwner.no_one


@public
class ModeratorSubApprovalMixin(ModeratorApprovalMixin):
    def __init__(self, pre_approved=False):
        super().__init__(pre_approved)

    @property
    def _request_name(self):
        return 'subscription'

    @property
    def _request_body(self):
        params = {'mlist': self.mlist.fqdn_listname,
                  'address': self.pgp_address.email,
                  'fingerprint': self.pubkey.fingerprint}
        return SUBSCRIPTION_MOD_REQUEST.format(**params)


@public
class ModeratorKeyChangeApprovalMixin(ModeratorApprovalMixin):
    def __init__(self, pre_approved=False):
        super().__init__(pre_approved)

    @property
    def _request_name(self):
        return 'key change'

    @property
    def _request_body(self):
        params = {'mlist': self.mlist.fqdn_listname,
                  'address': self.pgp_address.email,
                  'fingerprint': self.pubkey.fingerprint,
                  'old_fpr': self.pgp_address.key_fingerprint,
                  'new_fpr': self.pubkey.fingerprint}
        return KEY_CHANGE_MOD_REQUEST.format(**params)


@public
class ModeratorKeyRevokeApprovalMixin(ModeratorApprovalMixin):
    def __init__(self, pre_approved=False):
        super().__init__(pre_approved)

    @property
    def _request_name(self):
        return 'key reset'

    @property
    def _request_body(self):
        params = {'mlist': self.mlist.fqdn_listname,
                  'address': self.pgp_address.email,
                  'fingerprint': self.pubkey.fingerprint,
                  'old_fpr': self.pgp_address.key_fingerprint,
                  'new_fpr': self.pubkey.fingerprint}
        return KEY_REVOKE_MOD_REQUEST.format(**params)
