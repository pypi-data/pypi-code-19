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
REST root.


/lists/ -> List all known encrypted lists.
/lists/<list_id>/ ->
/lists/<list_id>/key -> GET list_public_key
"""

from mailman.rest.helpers import child
from public import public

from mailman_pgp.rest.addresses import AllAddresses, AnAddress
from mailman_pgp.rest.lists import AllEncryptedLists, AnEncryptedList


@public
class RESTRoot:
    @child()
    def lists(self, context, segments):
        if len(segments) == 0:
            return AllEncryptedLists(), []
        else:
            list_identifier = segments.pop(0)
            return AnEncryptedList(list_identifier), segments

    @child()
    def addresses(self, context, segments):
        if len(segments) == 0:
            return AllAddresses(), []
        else:
            email = segments.pop(0)
            return AnAddress(email), segments
