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

"""Filesystem stored PGP key."""
from os import remove, urandom
from os.path import getmtime, getsize, join
from pathlib import Path

from public import public

from mailman_pgp.utils.file import locked_obj
from mailman_pgp.utils.pgp import key_from_file


@public
class FSKey:
    """Filesystem stored PGP key."""

    def __init__(self, keydir, keyfile, load=False):
        self._key = None
        self._mtime = None
        if isinstance(keydir, Path):
            self.keydir = str(keydir)
        else:
            self.keydir = keydir
        self.keyfile = keyfile
        if load:
            self.load()

    @property
    def key(self):
        """

        :rtype: pgpy.PGPKey
        """
        return self._key

    @key.setter
    def key(self, value):
        """

        :param value:
        :type value: pgpy.PGPKey
        """
        self._key = value

    @property
    def key_path(self):
        return join(self.keydir, self.keyfile)

    @property
    def lock_path(self):
        return self.key_path + '.lock'

    def _load(self):
        try:
            self.key = key_from_file(self.key_path)
            self._mtime = getmtime(self.key_path)
        except FileNotFoundError:
            self.key = None
            self._mtime = None

    @locked_obj('lock_path')
    def load(self):
        self._load()

    @locked_obj('lock_path')
    def reload(self):
        if self.key is None:
            self._load()
        else:
            mtime = getmtime(self.key_path)
            if self._mtime is None or mtime > self._mtime:
                self._load()

    @locked_obj('lock_path')
    def save(self):
        if self.key is None:
            remove(self.key_path)
            self._mtime = None
        else:
            with open(self.key_path, 'w') as key_file:
                key_file.write(str(self.key))
            self._mtime = getmtime(self.key_path)

    @locked_obj('lock_path')
    def delete(self):
        try:
            remove(self.key_path)
        except FileNotFoundError:
            pass

    @locked_obj('lock_path')
    def shred(self):
        try:
            size = getsize(self.key_path)
            for _ in range(50):
                with open(self.key_path, 'wb') as f:
                    data = urandom(size)
                    f.write(data)
            remove(self.key_path)
        except FileNotFoundError:
            pass
