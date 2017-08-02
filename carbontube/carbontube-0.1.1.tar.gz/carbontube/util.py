# -*- coding: utf-8 -*-
# <carbontube - distributed pipeline framework>
#
# Copyright (C) <2016>  Gabriel Falcão <gabriel@nacaolivre.org>
# (C) Author: Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import io
import re
import zlib
import pickle
from plant import Node
from agentzero.serializers import BaseSerializer

internal_node = Node(__file__).dir


class CompressedPickle(BaseSerializer):
    """Serializes to and from zlib compressed pickle"""

    def pack(self, item):
        return zlib.compress(pickle.dumps(item))

    def unpack(self, item):
        return pickle.loads(zlib.decompress(item))


def sanitize_name(name):
    """ensures that a job type or pipeline name are safe for storage and handling.

    :param name: the string

    :returns: a safe string
    """
    return re.sub(r'[^\w_-]+', '_', name).strip('_')


def parse_port(address):
    """parses the port from a zmq tcp address

    :param address: the string of address

    :returns: an ``int`` or ``None``
    """
    found = re.search(r':(\d+)', address)
    if found:
        return int(found.group(1))


def read_internal_file(path):
    """reads an internal file, mostly used for loading lua scripts"""
    target = internal_node.join(path)
    return io.open(target, 'rb').read()
