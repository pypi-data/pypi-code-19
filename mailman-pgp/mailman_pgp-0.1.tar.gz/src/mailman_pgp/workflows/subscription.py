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
from mailman.workflows.common import (ConfirmationMixin, ModerationMixin,
                                      SubscriptionBase, VerificationMixin)
from public import public
from zope.interface import implementer

from mailman_pgp.workflows.base import (ConfirmPubkeyMixin, PGPMixin,
                                        SetPubkeyMixin)


@public
@implementer(ISubscriptionWorkflow)
class OpenSubscriptionPolicy(SubscriptionBase, VerificationMixin,
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
        SubscriptionBase.__init__(self, mlist, subscriber)
        VerificationMixin.__init__(self, pre_verified=pre_verified)
        SetPubkeyMixin.__init__(self, pubkey=pubkey)
        ConfirmPubkeyMixin.__init__(self, pre_confirmed=pubkey_pre_confirmed)
        PGPMixin.__init__(self)

    def _step_prepare(self):
        self.push('do_subscription')
        self.push('pubkey_confirmation')
        self.push('pubkey_checks')
        self.push('pgp_prepare')
        self.push('verification_checks')
        self.push('sanity_checks')


@public
@implementer(ISubscriptionWorkflow)
class ConfirmSubscriptionPolicy(SubscriptionBase, VerificationMixin,
                                ConfirmationMixin, SetPubkeyMixin,
                                ConfirmPubkeyMixin, PGPMixin):
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
        SubscriptionBase.__init__(self, mlist, subscriber)
        VerificationMixin.__init__(self, pre_verified=pre_verified)
        ConfirmationMixin.__init__(self, pre_confirmed=pre_confirmed)
        SetPubkeyMixin.__init__(self, pubkey=pubkey)
        ConfirmPubkeyMixin.__init__(self, pre_confirmed=pubkey_pre_confirmed)
        PGPMixin.__init__(self)

    def _step_prepare(self):
        self.push('do_subscription')
        self.push('pubkey_confirmation')
        self.push('pubkey_checks')
        self.push('pgp_prepare')
        self.push('confirmation_checks')
        self.push('verification_checks')
        self.push('sanity_checks')


@public
@implementer(ISubscriptionWorkflow)
class ModerationSubscriptionPolicy(SubscriptionBase, VerificationMixin,
                                   ModerationMixin, SetPubkeyMixin,
                                   ConfirmPubkeyMixin, PGPMixin):
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
        SubscriptionBase.__init__(self, mlist, subscriber)
        VerificationMixin.__init__(self, pre_verified=pre_verified)
        ModerationMixin.__init__(self, pre_approved=pre_approved)
        SetPubkeyMixin.__init__(self, pubkey=pubkey)
        ConfirmPubkeyMixin.__init__(self, pre_confirmed=pubkey_pre_confirmed)
        PGPMixin.__init__(self)

    def _step_prepare(self):
        self.push('do_subscription')
        self.push('moderation_checks')
        self.push('pubkey_confirmation')
        self.push('pubkey_checks')
        self.push('pgp_prepare')
        self.push('verification_checks')
        self.push('sanity_checks')


@public
@implementer(ISubscriptionWorkflow)
class ConfirmModerationSubscriptionPolicy(SubscriptionBase, VerificationMixin,
                                          ConfirmationMixin, ModerationMixin,
                                          SetPubkeyMixin, ConfirmPubkeyMixin,
                                          PGPMixin):
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
        SubscriptionBase.__init__(self, mlist, subscriber)
        VerificationMixin.__init__(self, pre_verified=pre_verified)
        ConfirmationMixin.__init__(self, pre_confirmed=pre_confirmed)
        ModerationMixin.__init__(self, pre_approved=pre_approved)
        SetPubkeyMixin.__init__(self, pubkey=pubkey)
        ConfirmPubkeyMixin.__init__(self, pre_confirmed=pubkey_pre_confirmed)
        PGPMixin.__init__(self)

    def _step_prepare(self):
        self.push('do_subscription')
        self.push('moderation_checks')
        self.push('pubkey_confirmation')
        self.push('pubkey_checks')
        self.push('pgp_prepare')
        self.push('confirmation_checks')
        self.push('verification_checks')
        self.push('sanity_checks')
