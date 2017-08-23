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

from mailman.database.types import SAUnicode
from mailman.interfaces.usermanager import IUserManager
from public import public
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import reconstructor
from zope.component import getUtility

from mailman_pgp.config import config
from mailman_pgp.model.base import Base
from mailman_pgp.model.fs_key import FSKey


@public
class PGPAddress(Base):
    """A PGP enabled address."""

    __tablename__ = 'pgp_addresses'

    id = Column(Integer, primary_key=True)
    email = Column(SAUnicode, index=True, unique=True)
    key_fingerprint = Column(String(50))
    key_confirmed = Column(Boolean, default=False)

    def __init__(self, address):
        super().__init__(email=address.email)
        self._init()
        self._address = address

    @reconstructor
    def _init(self):
        self._address = None
        self._key = FSKey(config.pgp.keydirs['user_keydir'],
                          self.email + '.asc', True)

    @property
    def key(self):
        """

        :return:
        :rtype: pgpy.PGPKey
        """
        self._key.reload()
        return self._key.key

    @key.setter
    def key(self, value):
        """

        :param value:
        :type value: pgpy.PGPKey
        """
        if value is None:
            self.key_fingerprint = None
        else:
            self.key_fingerprint = value.fingerprint
        self._key.key = value
        self._key.save()

    @property
    def key_path(self):
        """

        :return:
        :rtype: str
        """
        return self._key.key_path

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
        """

        :param email:
        :return:
        :rtype: PGPAddress|None
        """
        if email is None:
            return None
        return PGPAddress.query().filter_by(email=email).first()
