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


class enumflag_validator:
    def __init__(self, enum):
        self.enum = enum

    def __call__(self, value):
        if isinstance(value, (tuple, list)):
            result = set()
            for val in value:
                result.add(self.enum[val])
            return result

        return {self.enum[value]}


class workflow_validator:
    def __init__(self, *classes):
        self.classes = classes

    def __call__(self, value):
        if value in (workflow.name for workflow in self.classes):
            return value
        raise ValueError
