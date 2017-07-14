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

"""Various pgp and email utilities."""


def copy_headers(from_msg, to_msg, overwrite=False):
    """
    Copy the headers and unixfrom from a message to another one.

    :param from_msg: The source `Message`.
    :type from_msg: email.message.Message
    :param to_msg: The destination `Message`.
    :type to_msg: email.message.Message
    """
    for key, value in from_msg.items():
        if overwrite:
            del to_msg[key]
        if key not in to_msg:
            to_msg[key] = value
    if to_msg.get_unixfrom() is None:
        to_msg.set_unixfrom(from_msg.get_unixfrom())
