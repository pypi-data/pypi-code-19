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
from sqlalchemy import Column, LargeBinary, String

from mailman_pgp.model.base import Base


@public
class PGPSigHash(Base):
    """"""

    __tablename__ = 'pgp_sighashes'

    hash = Column(LargeBinary, primary_key=True)
    fingerprint = Column(String(50), index=True)

    @staticmethod
    def hashes(hashes):
        if hashes is None or len(hashes) == 0:
            return None
        return PGPSigHash.query().filter(PGPSigHash.hash.in_(hashes)).all()
