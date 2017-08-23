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

"""The key email command."""
import copy
import logging
from email.mime.text import MIMEText

from mailman.email.message import UserNotification
from mailman.interfaces.command import ContinueProcessing, IEmailCommand
from mailman.interfaces.member import MemberRole
from mailman.interfaces.pending import IPendings
from mailman.interfaces.subscriptions import ISubscriptionManager
from mailman.interfaces.usermanager import IUserManager
from pgpy.constants import KeyFlags
from pgpy.errors import PGPError
from public import public
from zope.component import getUtility
from zope.interface import implementer

from mailman_pgp.config import mm_config
from mailman_pgp.database import transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.mime import MIMEWrapper
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.utils.email import get_email
from mailman_pgp.utils.pgp import key_merge, key_usable
from mailman_pgp.workflows.key_change import (CHANGE_CONFIRM_REQUEST,
                                              KeyChangeModWorkflow,
                                              KeyChangeWorkflow)
from mailman_pgp.workflows.key_confirm import CONFIRM_REQUEST
from mailman_pgp.workflows.key_revoke import KeyRevokeWorkflow

log = logging.getLogger('mailman.plugin.pgp.commands')


def _cmd_set(pgp_list, mlist, msg, msgdata, arguments, results):
    """
    `key set "token"` command.

    Used during the subscription to a PGP enabled mailing list, if the user
    didn't already setup a `PGPaddress`.

     * This command message CAN be encrypted to the list key, in which case it
     will be decrypted.
     * This command message MUST have exactly one transferrable PGP public key
     attached (either PGP/MIME or inline PGP).
    """
    if len(arguments) != 2:
        print('Missing token.', file=results)
        return ContinueProcessing.no

    wrapped = PGPWrapper(msg, True)
    if wrapped.is_encrypted():
        wrapped.try_decrypt(pgp_list.key)

    if not wrapped.has_keys():
        print('No keys attached? Send a key.', file=results)
        return ContinueProcessing.no

    keys = list(wrapped.keys())
    if len(keys) != 1:
        print('More than one key! Send only one key.', file=results)
        return ContinueProcessing.no
    key = keys.pop()

    if not key.is_public:
        print('You probably wanted to send your public key only.',
              file=results)
        return ContinueProcessing.no

    if not key_usable(key, {KeyFlags.EncryptCommunications, KeyFlags.Sign}):
        print('Need a key which can be used to encrypt communications.',
              file=results)
        return ContinueProcessing.no

    email = get_email(msg)
    if not email:
        print('No email to subscribe with.', file=results)
        return ContinueProcessing.no

    address = getUtility(IUserManager).get_address(email)
    if not address:
        print('No adddress to subscribe with.', file=results)
        return ContinueProcessing.no

    pgp_address = PGPAddress.for_address(address)
    if pgp_address is None:
        print('A pgp enabled address not found.', file=results)
        return ContinueProcessing.no

    token = arguments[1]
    pendable = getUtility(IPendings).confirm(token, expunge=False)
    if pendable is None:
        print('Wrong token.', file=results)
        return ContinueProcessing.no

    with transaction():
        pgp_address.key = key
    ISubscriptionManager(mlist).confirm(token)

    print('Key succesfully set.', file=results)
    print('Key fingerprint: {}'.format(pgp_address.key.fingerprint),
          file=results)

    return ContinueProcessing.no


def _cmd_confirm(pgp_list, mlist, msg, msgdata, arguments, results):
    """
    `key confirm "token"` command.

    Used during subscription to confirm the setting of a users key, also for
    confirming the change of a key of a subscriber after the `key change`
    command.

     * This command message CAN be encrypted to the list key, in which case it
     will be decrypted.
     * This command message MUST contain the appropriate statement of key
     ownership, sent to the user after the `key set` or `key change` commands.
     This statement MUST be singed by the users current key.
    """
    if len(arguments) != 2:
        print('Missing token.', file=results)
        return ContinueProcessing.no

    email = get_email(msg)
    if not email:
        print('No email to subscribe with.', file=results)
        return ContinueProcessing.no

    pgp_address = PGPAddress.for_email(email)
    if pgp_address is None:
        print('A pgp enabled address not found.', file=results)
        return ContinueProcessing.no

    if pgp_address.key is None:
        print('No key set.', file=results)
        return ContinueProcessing.no

    wrapped = PGPWrapper(msg, True)
    if wrapped.is_encrypted():
        wrapped.try_decrypt(pgp_list.key)

    if not wrapped.is_signed():
        print('Message not signed, ignoring.', file=results)
        return ContinueProcessing.no

    if not wrapped.verifies(pgp_address.key):
        print('Message failed to verify.', file=results)
        return ContinueProcessing.no

    token = arguments[1]

    pendable = getUtility(IPendings).confirm(token, expunge=False)
    if pendable is None:
        print('Wrong token.', file=results)
        return ContinueProcessing.no

    if pendable.get('type') in (KeyChangeWorkflow.name,
                                KeyChangeModWorkflow.name):
        expecting = CHANGE_CONFIRM_REQUEST.format(pendable.get('fingerprint'),
                                                  token)
    else:
        expecting = CONFIRM_REQUEST.format(pgp_address.key_fingerprint, token)

    for sig_subject in wrapped.get_signed():
        if expecting in sig_subject:
            with transaction():
                pgp_address.key_confirmed = True
            ISubscriptionManager(mlist).confirm(token)
            break
    else:
        print("Message doesn't contain the expected statement.", file=results)
    return ContinueProcessing.no


def _cmd_change(pgp_list, mlist, msg, msgdata, arguments, results):
    """
    `key change` command.

    Used when a user wants to change a key of a `PGPAddress`.

     * This command message CAN be encrypted to the list key, in which case it
     will be decrypted.
     * This command message MUST have exactly one transferrable PGP public key
     attached (either PGP/MIME or inline PGP).
    """
    if len(arguments) != 1:
        print('Extraneous argument/s: ' + ','.join(arguments[1:]),
              file=results)
        return ContinueProcessing.no

    email = get_email(msg)
    if not email:
        print('No email to change key of.', file=results)
        return ContinueProcessing.no

    pgp_address = PGPAddress.for_email(email)
    if pgp_address is None:
        print('A pgp enabled address not found.', file=results)
        return ContinueProcessing.no

    if pgp_address.key is None:
        print("You currently don't have a key set.", file=results)
        return ContinueProcessing.no

    if not pgp_address.key_confirmed:
        print('Your key is currently not confirmed.', file=results)
        return ContinueProcessing.no

    wrapped = PGPWrapper(msg, True)
    if wrapped.is_encrypted():
        wrapped.try_decrypt(pgp_list.key)

    if not wrapped.has_keys():
        print('No keys attached? Send a key.', file=results)
        return ContinueProcessing.no

    keys = list(wrapped.keys())
    if len(keys) != 1:
        print('More than one key! Send only one key.', file=results)
        return ContinueProcessing.no
    key = keys.pop()

    if not key.is_public:
        print('You probably wanted to send your public key only.',
              file=results)
        return ContinueProcessing.no

    if not key_usable(key, {KeyFlags.EncryptCommunications, KeyFlags.Sign}):
        print('Need a key which can be used to encrypt communications.',
              file=results)
        return ContinueProcessing.no

    workflow_class = mm_config.workflows[pgp_list.key_change_workflow]

    workflow = workflow_class(mlist, pgp_address, key)
    list(workflow)
    print('Key change request received.', file=results)
    return ContinueProcessing.no


def _cmd_revoke(pgp_list, mlist, msg, msgdata, arguments, results):
    """
    `key revoke` command.

    Used when a user has to revoke a part of a key used for a `PGPAddress`.

     * This command message CAN be encrypted to the list key, in which case it
     will be decrypted.
     * This command message MUST have at least one revocation certificate
     attached.
    """
    if len(arguments) != 1:
        print('Extraneous argument/s: ' + ','.join(arguments[1:]),
              file=results)
        return ContinueProcessing.no

    email = get_email(msg)
    if not email:
        print('No email to revoke key of.', file=results)
        return ContinueProcessing.no

    pgp_address = PGPAddress.for_email(email)
    if pgp_address is None:
        print('A pgp enabled address not found.', file=results)
        return ContinueProcessing.no

    key = pgp_address.key
    if key is None:
        print("You currently don't have a key set.", file=results)
        return ContinueProcessing.no

    if not pgp_address.key_confirmed:
        print('Your key is currently not confirmed.', file=results)
        return ContinueProcessing.no

    wrapped = PGPWrapper(msg, True)
    if wrapped.is_encrypted():
        wrapped.try_decrypt(pgp_list.key)

    if not wrapped.has_revocs():
        print('No key revocations attached? Send a key revocation.',
              file=results)
        return ContinueProcessing.no

    key_copy = copy.copy(key)

    revocs = list(wrapped.revocs())
    matches = 0
    for revoc in revocs:
        old_matches = matches
        try:
            verified = key_copy.verify(key_copy, revoc)
            if verified:
                key_copy |= revoc
                matches += 1
                continue
        except PGPError:
            pass

        for subkey in key_copy.subkeys.values():
            try:
                verified = key_copy.verify(subkey, revoc)
                if verified:
                    subkey |= revoc
                    matches += 1
                    break
            except PGPError:
                pass
        # No match?
        if matches == old_matches:
            print('Revocation found for not-found key.', file=results)

    if not key_usable(key_copy,
                      {KeyFlags.EncryptCommunications, KeyFlags.Sign}):
        # Start reset process.
        with transaction():
            pgp_address.key = None
            pgp_address.key_confirmed = False
        workflow = KeyRevokeWorkflow(mlist, pgp_address)
        list(workflow)
        print('Key needs to be reset.', file=results)
    else:
        # Just update key.
        if matches > 0:
            with transaction():
                pgp_address.key = key_copy
            print('Key succesfully updated.', file=results)
        else:
            print('Nothing to do.', file=results)
    return ContinueProcessing.yes


def _cmd_sign(pgp_list, mlist, msg, msgdata, arguments, results):
    # List public key attached, signed by the users current key.
    if len(arguments) != 1:
        print('Extraneous argument/s: ' + ','.join(arguments[1:]),
              file=results)
        return ContinueProcessing.no

    email = get_email(msg)
    if not email:
        print('No email.', file=results)
        return ContinueProcessing.no

    pgp_address = PGPAddress.for_email(email)
    if pgp_address is None:
        print('A pgp enabled address not found.', file=results)
        return ContinueProcessing.no

    key = pgp_address.key
    if key is None:
        print("You currently don't have a key set.", file=results)
        return ContinueProcessing.no

    if not pgp_address.key_confirmed:
        print('Your key is currently not confirmed.', file=results)
        return ContinueProcessing.no

    wrapped = PGPWrapper(msg, True)
    if wrapped.is_encrypted():
        wrapped.try_decrypt(pgp_list.key)

    if not wrapped.has_keys():
        print('No keys attached? Send a key.', file=results)
        return ContinueProcessing.no

    keys = list(wrapped.keys())
    if len(keys) != 1:
        print('More than one key! Send only one key.', file=results)
        return ContinueProcessing.no
    key = keys.pop()

    allowed_signers = pgp_list.key_signing_allowed
    roster_map = {
        MemberRole.member: mlist.members,
        MemberRole.owner: mlist.owners,
        MemberRole.moderator: mlist.moderators,
        MemberRole.nonmember: mlist.nonmembers
    }
    allowed = False
    for allowed_role in allowed_signers:
        allowed_roster = roster_map[allowed_role]
        if allowed_roster.get_member(email) is not None:
            allowed = True
            break

    if not allowed:
        print('You are not allowed to sign the list key.', file=results)
        return ContinueProcessing.no

    try:
        key_merge(pgp_list.key, key, pgp_address.key)
    except ValueError as e:
        print(str(e), file=results)
        return ContinueProcessing.no

    pgp_list.fs_key.save()

    print('List key updated with new signatures.', file=results)
    return ContinueProcessing.yes


def _cmd_receive(pgp_list, mlist, msg, msgdata, arguments, results):
    if len(arguments) != 1:
        print('Extraneous argument/s: ' + ','.join(arguments[1:]),
              file=results)
        return ContinueProcessing.no

    email = get_email(msg)
    if not email:
        print('No email to send list public key.', file=results)
        return ContinueProcessing.no

    out = UserNotification(email, mlist.request_address,
                           '{} public key'.format(mlist.fqdn_listname))
    out.set_type('multipart/mixed')
    out['MIME-Version'] = '1.0'
    out.attach(MIMEText('Here is the public key you requested.'))
    MIMEWrapper(out).attach_keys(pgp_list.pubkey)

    out.send(mlist)
    print('Key sent.', file=results)
    return ContinueProcessing.yes


SUBCOMMANDS = {
    'set': _cmd_set,
    'confirm': _cmd_confirm,
    'change': _cmd_change,
    'revoke': _cmd_revoke,
    'sign': _cmd_sign,
    'receive': _cmd_receive
}

ARGUMENTS = '<' + '|'.join(SUBCOMMANDS) + '>'


@public
@implementer(IEmailCommand)
class KeyCommand:
    """The `key` command."""

    name = 'key'
    argument_description = ARGUMENTS
    short_description = 'PGP key management.'
    description = """\
    A general command for PGP key management for PGP enabled mailing lists.

    `key set <token>`
      A command used to set the address public key during subscription to a
      mailing list. Is only required on the first subscription of a given
      address to a PGP enabled mailing list. This command requires the command
      message to have exactly one PGP public key attached (either PGP/MIME or
      inline). This command should be encrypted to the mailing list public key.

    `key confirm <token>`
      A command used to confirm the setting of a new public key, either during
      subscription or later after a `key change` command. Is only required on
      the first subscription of a given address to a PGP enabled mailing list.
      This command requires the command message to contain the statement sent
      from the mailing list in response to the `key set <token>` command, and
      requires this statement signed by the key that was attached to the `key
      set` command message.

    `key change`
      A command used to change the address public key.

    `key revoke`
      A command used to revoke a part of/the whole address public key, when the
      user has access to a revocation certificate (but not the signing
      capability of the key to use `key change`). A revocation certificate
      must be attached to the message like a PGP key would. The revocation
      signature is verified, and the proper revocation is performed, if the
      key is left unusable after that, you will be prompted to set and confirm
      a new one.

    `key sign`
      A command used to add your signature to the list key, if you trust it. It
      requires exactly one PGP public key attached, which should be the list
      public key, signed with your address key. It is scanned for all new
      certifications by your address key and the valid ones are imported. A
      list might be configured to allow even a non-subscriber to sign its key.

    `key receive`
      A command used to request the list public key. The list public key will
      be sent in a response.
    """

    def process(self, mlist, msg, msgdata, arguments, results):
        """See `IEmailCommand`."""
        if len(arguments) == 0:
            print('No sub-command specified,'
                  ' must be one of {}.'.format(ARGUMENTS), file=results)
            return ContinueProcessing.no

        if arguments[0] not in SUBCOMMANDS:
            print('Wrong sub-command specified,'
                  ' must be one of {}.'.format(ARGUMENTS), file=results)
            return ContinueProcessing.no

        pgp_list = PGPMailingList.for_list(mlist)
        if pgp_list is None:
            print("This mailing list doesn't have pgp enabled.", file=results)
            return ContinueProcessing.no

        command = SUBCOMMANDS[arguments[0]]
        log.debug('key {}'.format(arguments[0]))
        return command(pgp_list, mlist, msg, msgdata, arguments, results)
