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
from email.utils import parseaddr

from mailman.interfaces.command import ContinueProcessing, IEmailCommand
from mailman.interfaces.pending import IPendings
from mailman.interfaces.subscriptions import ISubscriptionManager
from mailman.interfaces.usermanager import IUserManager
from public import public
from zope.component import getUtility
from zope.interface import implementer

from mailman_pgp.database import transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.workflows.base import CONFIRM_REQUEST
from mailman_pgp.workflows.key_change import (CHANGE_CONFIRM_REQUEST,
                                              KeyChangeWorkflow)


def _get_email(msg):
    display_name, email = parseaddr(msg['from'])
    # Address could be None or the empty string.
    if not email:
        email = msg.sender
    return email


def _cmd_set(pgp_list, mlist, msg, msgdata, arguments, results):
    if len(arguments) != 2:
        print('Missing token.', file=results)
        return ContinueProcessing.no

    wrapped = PGPWrapper(msg)
    if wrapped.is_encrypted():
        decrypted = wrapped.decrypt(pgp_list.key)
        wrapped = PGPWrapper(decrypted)

    if not wrapped.has_keys():
        print('No keys attached? Send a key.', file=results)
        return ContinueProcessing.no

    keys = list(wrapped.keys())
    if len(keys) != 1:
        print('More than one key! Send only one key.', file=results)
        return ContinueProcessing.no

    email = _get_email(msg)
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
        pgp_address.key = keys.pop()
    ISubscriptionManager(mlist).confirm(token)

    print('Key succesfully set.', file=results)
    print('Key fingerprint: {}'.format(pgp_address.key.fingerprint),
          file=results)

    return ContinueProcessing.no


def _cmd_confirm(pgp_list, mlist, msg, msgdata, arguments, results):
    if len(arguments) != 2:
        print('Missing token.', file=results)
        return ContinueProcessing.no

    email = _get_email(msg)
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

    wrapped = PGPWrapper(msg)
    if wrapped.is_encrypted():
        decrypted = wrapped.decrypt(pgp_list.key)
        wrapped = PGPWrapper(decrypted)

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

    if pendable.get('type') == KeyChangeWorkflow.pendable_class().PEND_TYPE:
        expecting = CHANGE_CONFIRM_REQUEST.format(pendable.get('fingerprint'),
                                                  token)
    else:
        expecting = CONFIRM_REQUEST.format(pgp_address.key_fingerprint, token)

    for sig_subject in wrapped.get_signed():
        if expecting in sig_subject:
            ISubscriptionManager(mlist).confirm(token)
            break
    else:
        print("Message doesn't contain the expected statement.", file=results)
    return ContinueProcessing.no


def _cmd_change(pgp_list, mlist, msg, msgdata, arguments, results):
    # New public key in attachment, requires to be signed with current
    # key
    if len(arguments) != 1:
        print('Extraneous argument/s: ' + ','.join(arguments[1:]),
              file=results)
        return ContinueProcessing.no

    wrapped = PGPWrapper(msg)
    if not wrapped.has_keys():
        print('No keys attached? Send a key.', file=results)
        return ContinueProcessing.no

    keys = list(wrapped.keys())
    if len(keys) != 1:
        print('More than one key! Send only one key.', file=results)
        return ContinueProcessing.no

    email = _get_email(msg)
    if not email:
        print('No email to change key of.', file=results)
        return ContinueProcessing.no

    pgp_address = PGPAddress.for_email(email)
    if pgp_address is None:
        print('A pgp enabled address not found.', file=results)
        return ContinueProcessing.no

    workflow = KeyChangeWorkflow(mlist, pgp_address, keys.pop())
    list(workflow)
    print('Key change request received.', file=results)
    return ContinueProcessing.no


def _cmd_revoke(pgp_list, mlist, msg, msgdata, arguments, results):
    # Current key revocation certificate in attachment, restarts the
    # subscription process, or rather only it's key setup part.
    pass


def _cmd_sign(pgp_list, mlist, msg, msgdata, arguments, results):
    # List public key attached, signed by the users current key.
    pass


SUBCOMMANDS = {
    'set': _cmd_set,
    'confirm': _cmd_confirm,
    'change': _cmd_change,
    'revoke': _cmd_revoke,
    'sign': _cmd_sign
}

ARGUMENTS = '<' + '|'.join(SUBCOMMANDS.keys()) + '>'


@public
@implementer(IEmailCommand)
class KeyCommand:
    """The `key` command."""

    name = 'key'
    argument_description = ARGUMENTS
    short_description = ''
    description = """\
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
        return command(pgp_list, mlist, msg, msgdata, arguments, results)
