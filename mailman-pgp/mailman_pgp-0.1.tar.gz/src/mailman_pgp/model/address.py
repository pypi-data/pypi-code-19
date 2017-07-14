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

"""Model for PGP enabled addresses."""
import os
from os.path import exists, isfile, join

from mailman.database.types import SAUnicode
from mailman.interfaces.usermanager import IUserManager
from pgpy import PGPKey
from sqlalchemy import Boolean, Column, Integer
from sqlalchemy.orm import reconstructor
from zope.component import getUtility

from mailman_pgp.config import config
from mailman_pgp.model.base import Base


class PGPAddress(Base):
    """A PGP enabled address."""

    __tablename__ = 'pgp_addresses'

    id = Column(Integer, primary_key=True)
    email = Column(SAUnicode, index=True, unique=True)
    key_fingerprint = Column(SAUnicode)
    key_confirmed = Column(Boolean, default=False)

    def __init__(self, address):
        super().__init__()
        self.email = address.email
        self._init()
        self._address = address

    @reconstructor
    def _init(self):
        self._address = None
        self._key = None

    @property
    def key(self):
        """

        :return:
        :rtype: pgpy.PGPKey
        """
        if self.key_fingerprint is None:
            return None
        if self._key is None:
            if exists(self.key_path) and isfile(self.key_path):
                self._key, _ = PGPKey.from_file(self.key_path)
        return self._key

    @key.setter
    def key(self, new_key):
        """

        :param new_key:
        :type new_key: PGPKey
        """
        if self.key_fingerprint is not None:
            try:
                os.remove(self.key_path)
            except FileNotFoundError:
                pass
        if new_key is None:
            self.key_fingerprint = None
            self._key = None
        else:
            self.key_fingerprint = str(new_key.fingerprint)
            with open(self.key_path, 'w') as out:
                out.write(str(new_key))
            self._key = new_key

    @property
    def key_path(self):
        """

        :return:
        :rtype: str
        """
        if self.key_fingerprint is None:
            return None
        return join(config.pgp.keydir_config['user_keydir'],
                    self.key_fingerprint + '.asc')

    @property
    def address(self):
        """

        :return:
        :rtype: mailman.model.address.Address
        """
        if self._address is None:
            self._address = getUtility(IUserManager).get_address(self.email)
        return self._address

    @staticmethod
    def for_address(address):
        """

        :param address:
        :return:
        :rtype: PGPAddress|None
        """
        if address is None:
            return None
        return PGPAddress.for_email(address.email)

    @staticmethod
    def for_email(email):
        if email is None:
            return None
        return PGPAddress.query().filter_by(email=email).first()
