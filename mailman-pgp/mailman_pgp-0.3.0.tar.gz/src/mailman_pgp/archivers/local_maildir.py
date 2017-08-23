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
Archives messages to a maildir, locally, encrypted (TBD how),
similar to Mailman's prototype archiver.
"""
import os
from mailbox import Maildir

from flufl.lock import Lock
from mailman.interfaces.archiver import IArchiver
from public import public
from zope.interface import implementer

from mailman_pgp.config import config, mm_config
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.mime import MIMEWrapper


@public
@implementer(IArchiver)
class LocalMaildirArchiver:
    """Local PGP enabled archiver."""

    name = 'pgp-maildir-local'
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
        maildir_dir = config.get_value('archiving', 'maildir_dir')
        maildir_dir.mkdir(parents=True, exist_ok=True)

        list_dir = maildir_dir.joinpath(mlist.fqdn_listname)
        maildir = Maildir(str(list_dir))
        lock_file = os.path.join(mm_config.LOCK_DIR,
                                 '{}-{}.lock'.format(mlist.fqdn_listname,
                                                     LocalMaildirArchiver.name)
                                 )
        MIMEWrapper(msg).encrypt(pgp_list.pubkey)
        with Lock(lock_file):
            maildir.add(msg)
        return None
