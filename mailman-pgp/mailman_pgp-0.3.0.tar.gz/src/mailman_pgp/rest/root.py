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

"""REST root."""

from mailman.rest.helpers import child, NotFound
from public import public

from mailman_pgp.rest.addresses import AllAddresses, AnAddress
from mailman_pgp.rest.config import AConfig
from mailman_pgp.rest.lists import AllPGPLists, APGPList


@public
class RESTRoot:
    @child()
    def lists(self, context, segments):
        if len(segments) == 0:
            return AllPGPLists(), []
        else:
            list_identifier = segments.pop(0)
            return APGPList(list_identifier), segments

    @child()
    def addresses(self, context, segments):
        if len(segments) == 0:
            return AllAddresses(), []
        else:
            email = segments.pop(0)
            return AnAddress(email), segments

    @child()
    def config(self, context, segments):
        if len(segments) == 0:
            return AConfig(), []
        elif len(segments) == 1:
            section = segments.pop(0)
            return AConfig(section), []
        elif len(segments) == 2:
            section = segments.pop(0)
            attribute = segments.pop(0)
            return AConfig(section, attribute), []
        else:
            return NotFound(), []
