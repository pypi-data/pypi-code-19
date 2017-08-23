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
import copy
from email.utils import parseaddr

from mailman.email.message import MultipartDigestMessage
from public import public


@public
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
    if to_msg.get_unixfrom() is None or overwrite:
        to_msg.set_unixfrom(from_msg.get_unixfrom())
    if (hasattr(from_msg, 'original_size')
        and (getattr(to_msg, 'original_size', None) is None
             or overwrite)):
        to_msg.original_size = from_msg.original_size


@public
def overwrite_message(from_msg, to_msg):
    """
    Overwrite message data of `to_msg` with that of `from_msg`.

    :param from_msg: The source `Message`.
    :type from_msg: email.message.Message
    :param to_msg: The destination `Message`.
    :type to_msg: email.message.Message
    """
    for key in to_msg.keys():
        del to_msg[key]
    for key, value in from_msg.items():
        to_msg[key] = value
    to_msg.set_unixfrom(from_msg.get_unixfrom())
    to_msg.set_payload(from_msg.get_payload(), from_msg.get_charset())
    to_msg.preamble = from_msg.preamble
    to_msg.epilogue = from_msg.epilogue
    to_msg.set_default_type(from_msg.get_default_type())
    if hasattr(from_msg, 'orignal_size'):
        to_msg.original_size = from_msg.original_size


@public
def make_multipart(msg):
    """

    :param msg:
    :type msg: email.message.Message
    :return:
    :rtype: email.message.MIMEMultipart|
            mailman.email.message.MultipartDigestMessage
    """
    if msg.is_multipart():
        out = copy.deepcopy(msg)
    else:
        out = MultipartDigestMessage()
        out.attach(msg)
        copy_headers(msg, out)
    return out


@public
def get_email(msg):
    display_name, email = parseaddr(msg['from'])
    # Address could be None or the empty string.
    if not email:
        email = msg.sender
    return email
