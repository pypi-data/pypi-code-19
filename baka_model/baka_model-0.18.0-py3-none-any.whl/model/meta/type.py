"""
 # Copyright (c) 06 2016 | suryakencana
 # 6/13/16 nanang.ask@kubuskotak.com
 # This program is free software; you can redistribute it and/or
 # modify it under the terms of the GNU General Public License
 # as published by the Free Software Foundation; either version 2
 # of the License, or (at your option) any later version.
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program; if not, write to the Free Software
 # Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 #  type.py
"""
from collections import Iterable
import json

import bcrypt
from sqlalchemy import Numeric, TypeDecorator, String, CHAR, VARCHAR, Unicode, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy_utils.types import uuid

Amount = Numeric(8, 2)


class Password(str):
    """Coerce a string to a bcrypt password.

    Rationale: for an easy string comparison,
    so we can say ``some_password == 'hello123'``

    .. seealso::

        https://pypi.python.org/pypi/bcrypt/

    """

    def __new__(cls, value, salt=None, crypt=True):
        if isinstance(value, Unicode):
            value = value.encode('utf-8')
        if crypt:
            value = bcrypt.hashpw(value, salt or bcrypt.gensalt(4))
        return str.__new__(cls, value)

    def __eq__(self, other):
        if not isinstance(other, Password):
            other = Password(other, self)
        return str.__eq__(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)


class BcryptType(TypeDecorator):
    """Coerce strings to bcrypted Password objects for the database.
    """

    impl = String(128)

    def process_bind_param(self, value, dialect):
        return Password(value)

    def process_result_value(self, value, dialect):
        # already crypted, so don't crypt again
        return Password(value, value, False)

    def __repr__(self):
        return "BcryptType()"


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    .. seealso::

        http://docs.sqlalchemy.org/en/latest/core/types.html#backend-agnostic-guid-type

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
        e.g data = Column(MutableDict.as_mutable(JSONEncodedDict))
    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain dictionaries to MutableDict."""

        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        """Detect dictionary set events and emit change events."""

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        """Detect dictionary del events and emit change events."""

        dict.__delitem__(self, key)
        self.changed()


class EnumInt(object):
    def __init__(self, value, values):
        self.value = value
        self._values = values

    @property
    def title(self):
        return self.value if self.value is None else self._values[self.value][1]

    @property
    def key(self):
        return self.value is not None and self._values[self.value][0]

    def __eq__(self, other):
        values = list(map(lambda x: x[0], self._values))
        return (other in values) and self.value == values.index(other)

    def __str__(self):
        return self.value if self.value is None else u"%s, %s" % (
            self.value, self._values[self.value][1]
        )

    def __repr__(self):
        return u"EnumInt(%s)" % self

    def serialize(self):
        return {'key': self.key, 'value': self.value, 'title': self.title}


class EnumIntType(TypeDecorator):

    impl = SmallInteger
    values = None

    def __init__(self, values=None):
        super(EnumIntType, self).__init__()
        assert values is None or isinstance(values, Iterable), \
            u'Values must be None or iterable'
        self.values = values

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        values = list(map(lambda x: x[0], self.values))
        return values.index(value)

    def process_result_value(self, value, dialect):
        return EnumInt(value, self.values)
