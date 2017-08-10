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
from public import public
from sqlalchemy import Integer, TypeDecorator


@public
class EnumFlag(TypeDecorator):
    """Simple bitwise flag from an `enum.Enum`, assumes it is unique."""
    impl = Integer

    def __init__(self, enum, *args, **kw):
        super().__init__(*args, **kw)
        self.enum = enum

    def process_bind_param(self, value, dialect):
        # value is a set/frozenset of Enums.
        if value is None:
            return None
        if not isinstance(value, (set, frozenset)):
            raise ValueError

        int_value = 0
        for enum in reversed(self.enum):
            int_value = int_value << 1
            if enum in value:
                int_value += 1

        return int_value

    def process_result_value(self, value, dialect):
        # value is an integer.
        if value is None:
            return None
        if value == 0:
            return frozenset()
        result = set()
        for enum in self.enum:
            if value % 2 == 1:
                result.add(enum)
            value = value >> 1

        return frozenset(result)
