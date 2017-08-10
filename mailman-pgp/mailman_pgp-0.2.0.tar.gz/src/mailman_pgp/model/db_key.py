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

"""Database stored PGP key."""
from public import public
from sqlalchemy import Column, Integer, LargeBinary
from sqlalchemy.orm import reconstructor

from mailman_pgp.model.base import Base
from mailman_pgp.utils.pgp import key_from_blob


@public
class DBKey(Base):
    """Database stored PGP key."""
    __tablename__ = 'keys'

    id = Column(Integer, primary_key=True)
    _key_material = Column('key_material', LargeBinary)

    def __init__(self, key=None):
        super().__init__()
        self._init()
        self.key = key

    @reconstructor
    def _init(self):
        self._key = None

    @property
    def key(self):
        if self._key is None:
            self._key = key_from_blob(self._key_material)
        return self._key

    @key.setter
    def key(self, value):
        if value is None:
            self._key = None
            self._key_material = bytes()
        else:
            self._key = value
            self._key_material = bytes(value)
