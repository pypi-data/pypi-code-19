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

"""
Archives messages to a mbox, locally, encrypted (TBD how),
similar to Mailman's prototype archiver.
"""
import os
from mailbox import mbox

from flufl.lock import Lock
from mailman.interfaces.archiver import IArchiver
from public import public
from zope.interface import implementer

from mailman_pgp.config import config, mm_config
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.mime import MIMEWrapper


@public
@implementer(IArchiver)
class LocalMailboxArchiver:
    """Local PGP enabled archiver."""

    name = 'pgp-mbox-local'
    is_enabled = False

    @staticmethod
    def list_url(mlist):
        """See `IArchiver`."""
        return None

    @staticmethod
    def permalink(mlist, msg):
        """See `IArchiver`."""
        return None

    @staticmethod
    def archive_message(mlist, msg):
        """See `IArchiver`."""
        pgp_list = PGPMailingList.for_list(mlist)
        if not pgp_list:
            return None
        mailbox_dir = config.get_value('archiving', 'mailbox_dir')
        mailbox_dir.mkdir(parents=True, exist_ok=True)

        list_dir = mailbox_dir.joinpath(mlist.fqdn_listname)
        mailbox = mbox(str(list_dir))
        lock_file = os.path.join(mm_config.LOCK_DIR,
                                 '{}-{}.lock'.format(mlist.fqdn_listname,
                                                     LocalMailboxArchiver.name)
                                 )
        MIMEWrapper(msg).encrypt(pgp_list.pubkey)
        with Lock(lock_file):
            mailbox.add(msg)
        return None
