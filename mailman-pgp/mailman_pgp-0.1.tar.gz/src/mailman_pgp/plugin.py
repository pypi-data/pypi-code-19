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

"""A PGP plugin for GNU Mailman."""

from mailman.interfaces.listmanager import ListDeletedEvent
from mailman.interfaces.plugin import IPlugin
from public import public
from zope.event import classhandler
from zope.interface import implementer

from mailman_pgp.config import config
from mailman_pgp.database import Database, transaction
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp import PGP
from mailman_pgp.rest.root import RESTRoot


@public
@implementer(IPlugin)
class PGPMailman:
    """PGP plugin for Mailman!"""

    def pre_hook(self):
        """See `IPlugin`."""
        config.load(self.name)
        config.db = Database()
        config.pgp = PGP()

    def post_hook(self):
        """See `IPlugin`."""
        pass

    def rest_object(self):
        """See `IPlugin`."""
        return RESTRoot()


@classhandler.handler(ListDeletedEvent)
def on_delete(mlist):
    pgp_list = PGPMailingList.for_list(mlist)
    if pgp_list:
        with transaction() as session:
            # TODO shred the list key
            session.delete(pgp_list)
