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
from public import public


@public
def record_action(msg, msgdata, action, sender, reason):
    """

    :param msg:
    :param msgdata:
    :param action:
    :param sender:
    :param reason:
    :return:
    """
    msgdata['pgp_action'] = action.name
    msgdata['moderation_sender'] = sender
    msgdata.setdefault('moderation_reasons', []).append(reason)
