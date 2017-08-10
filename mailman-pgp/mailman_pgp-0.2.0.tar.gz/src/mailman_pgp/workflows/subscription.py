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

from mailman.core.i18n import _
from mailman.interfaces.workflows import ISubscriptionWorkflow
from mailman.workflows.common import (ConfirmationMixin, VerificationMixin)
from public import public
from zope.interface import implementer

from mailman_pgp.workflows.base import PGPMixin, PGPSubscriptionBase
from mailman_pgp.workflows.key_confirm import ConfirmPubkeyMixin
from mailman_pgp.workflows.key_set import SetPubkeyMixin
from mailman_pgp.workflows.mod_approval import ModeratorSubApprovalMixin


@public
@implementer(ISubscriptionWorkflow)
class OpenSubscriptionPolicy(PGPSubscriptionBase, VerificationMixin,
                             SetPubkeyMixin, ConfirmPubkeyMixin,
                             PGPMixin):
    """"""

    name = 'pgp-policy-open'
    description = _('An open subscription policy, '
                    'for a PGP-enabled mailing list.')
    initial_state = 'prepare'
    save_attributes = (
        'verified',
        'pubkey_key',
        'pubkey_confirmed',
        'address_key',
        'subscriber_key',
        'user_key',
        'token_owner_key',
    )

    def __init__(self, mlist, subscriber=None, *,
                 pre_verified=False, pubkey=None,
                 pubkey_pre_confirmed=False):
        PGPSubscriptionBase.__init__(self, mlist, subscriber)
        VerificationMixin.__init__(self, pre_verified=pre_verified)
        SetPubkeyMixin.__init__(self, pubkey=pubkey)
        ConfirmPubkeyMixin.__init__(self, pre_confirmed=pubkey_pre_confirmed)
        PGPMixin.__init__(self, mlist)

    def _step_prepare(self):
        self.push('do_subscription')
        self.push('restore_subscriber')
        self.push('pubkey_confirmation')
        self.push('restore_address')
        self.push('pubkey_checks')
        self.push('create_address')
        self.push('verification_checks')
        self.push('sanity_checks')


@public
@implementer(ISubscriptionWorkflow)
class ConfirmSubscriptionPolicy(PGPSubscriptionBase, VerificationMixin,
                                ConfirmationMixin, SetPubkeyMixin,
                                ConfirmPubkeyMixin):
    """"""

    name = 'pgp-policy-confirm'
    description = _('A subscription policy, for a PGP-enabled mailing list '
                    'that requires confirmation.')
    initial_state = 'prepare'
    save_attributes = (
        'verified',
        'confirmed',
        'pubkey_key',
        'pubkey_confirmed',
        'address_key',
        'subscriber_key',
        'user_key',
        'token_owner_key',
    )

    def __init__(self, mlist, subscriber=None, *,
                 pre_verified=False, pre_confirmed=False, pubkey=None,
                 pubkey_pre_confirmed=False):
        PGPSubscriptionBase.__init__(self, mlist, subscriber)
        VerificationMixin.__init__(self, pre_verified=pre_verified)
        ConfirmationMixin.__init__(self, pre_confirmed=pre_confirmed)
        SetPubkeyMixin.__init__(self, pubkey=pubkey)
        ConfirmPubkeyMixin.__init__(self, pre_confirmed=pubkey_pre_confirmed)

    def _step_prepare(self):
        self.push('do_subscription')
        self.push('restore_subscriber')
        self.push('pubkey_confirmation')
        self.push('restore_address')
        self.push('pubkey_checks')
        self.push('create_address')
        self.push('confirmation_checks')
        self.push('verification_checks')
        self.push('sanity_checks')


@public
@implementer(ISubscriptionWorkflow)
class ModerationSubscriptionPolicy(PGPSubscriptionBase, VerificationMixin,
                                   ModeratorSubApprovalMixin, SetPubkeyMixin,
                                   ConfirmPubkeyMixin):
    """"""

    name = 'pgp-policy-moderate'
    description = _('A subscription policy, for a PGP-enabled mailing list '
                    'that requires moderation.')
    initial_state = 'prepare'
    save_attributes = (
        'verified',
        'approved',
        'pubkey_key',
        'pubkey_confirmed',
        'address_key',
        'subscriber_key',
        'user_key',
        'token_owner_key',
    )

    def __init__(self, mlist, subscriber=None, *,
                 pre_verified=False, pre_approved=False, pubkey=None,
                 pubkey_pre_confirmed=False):
        PGPSubscriptionBase.__init__(self, mlist, subscriber)
        VerificationMixin.__init__(self, pre_verified=pre_verified)
        ModeratorSubApprovalMixin.__init__(self, pre_approved=pre_approved)
        SetPubkeyMixin.__init__(self, pubkey=pubkey)
        ConfirmPubkeyMixin.__init__(self, pre_confirmed=pubkey_pre_confirmed)

    def _step_prepare(self):
        self.push('do_subscription')
        self.push('restore_subscriber')
        self.push('mod_approval')
        self.push('pubkey_confirmation')
        self.push('restore_address')
        self.push('pubkey_checks')
        self.push('create_address')
        self.push('verification_checks')
        self.push('sanity_checks')


@public
@implementer(ISubscriptionWorkflow)
class ConfirmModerationSubscriptionPolicy(PGPSubscriptionBase,
                                          VerificationMixin,
                                          ConfirmationMixin,
                                          ModeratorSubApprovalMixin,
                                          SetPubkeyMixin, ConfirmPubkeyMixin):
    """"""

    name = 'pgp-policy-confirm-moderate'
    description = _('A subscription policy, for a PGP-enabled mailing list '
                    'that requires moderation after confirmation.')
    initial_state = 'prepare'
    save_attributes = (
        'verified',
        'confirmed',
        'approved',
        'pubkey_key',
        'pubkey_confirmed',
        'address_key',
        'subscriber_key',
        'user_key',
        'token_owner_key',
    )

    def __init__(self, mlist, subscriber=None, *,
                 pre_verified=False, pre_confirmed=False, pre_approved=False,
                 pubkey=None, pubkey_pre_confirmed=False):
        PGPSubscriptionBase.__init__(self, mlist, subscriber)
        VerificationMixin.__init__(self, pre_verified=pre_verified)
        ConfirmationMixin.__init__(self, pre_confirmed=pre_confirmed)
        ModeratorSubApprovalMixin.__init__(self, pre_approved=pre_approved)
        SetPubkeyMixin.__init__(self, pubkey=pubkey)
        ConfirmPubkeyMixin.__init__(self, pre_confirmed=pubkey_pre_confirmed)

    def _step_prepare(self):
        self.push('do_subscription')
        self.push('restore_subscriber')
        self.push('mod_approval')
        self.push('restore_address')
        self.push('pubkey_confirmation')
        self.push('restore_address')
        self.push('pubkey_checks')
        self.push('create_address')
        self.push('confirmation_checks')
        self.push('verification_checks')
        self.push('sanity_checks')
