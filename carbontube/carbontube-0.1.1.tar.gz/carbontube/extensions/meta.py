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

from carbontube.extensions.registry import PIPELINES
from carbontube.extensions.registry import PHASES
from carbontube.extensions.registry import STORAGE_BACKENDS


class Extension(type):
    def __init__(ExtensionClass, name, bases, members):
        get_member = lambda key: members.get(key) or getattr(ExtensionClass, key, None)

        extension_name = get_member('name')
        path = get_member('__module__')

        if name not in ('ExtensionMeta', 'Extension'):
            _EXTENSION_REGISTRY[extension_name] = ExtensionClass
            _EXTENSION_CACHE[name] = ExtensionClass

        ExtensionClass.metadata = ExtensionMetadata([
            ('name', extension_name),
            ('version', get_member('version')),
            ('description', get_member('description')),
            ('required_arguments', get_member('required_arguments')),
            ('optional_arguments', get_member('optional_arguments')),
        ])
        super(Extension, ExtensionClass).__init__(name, bases, members)
