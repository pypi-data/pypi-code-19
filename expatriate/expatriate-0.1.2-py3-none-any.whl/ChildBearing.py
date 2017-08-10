# Copyright 2016 Casey Jaymes

# This file is part of Expatriate.
#
# Expatriate is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Expatriate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Expatriate.  If not, see <http://www.gnu.org/licenses/>.

import logging

from .Node import Node

logger = logging.getLogger(__name__)
class ChildBearing(Node):
    def __init__(self, document, document_order, parent):
        super(ChildBearing, self).__init__(document, document_order, parent)
        self.children = []

    def __len__(self):
        return len(self.children)

    def __getitem__(self, key):
        if not isinstance(key, int) and not isinstance(key, slice):
            raise TypeError('Key values must be of int type or slice; got: ' + key.__class__.__name__)

        return self.children[key]

    def __setitem__(self, key, value):
        if not isinstance(key, int):
            raise TypeError('Key values must be of int type; got: ' + key.__class__.__name__)
        if not isinstance(value, Node):
            raise TypeError('Values must be of Node type; got: ' + value.__class__.__name__)

        self.children[key] = value

    def __delitem__(self, key):
        if not isinstance(key, int):
            raise TypeError('Key values must be of int type; got: ' + key.__class__.__name__)

        del self.children[key]

    def __iter__(self):
        return iter(self.children)

    def append(self, x):
        from .CharacterData import CharacterData

        if isinstance(x, str):
            # wrap in CharaterData
            cd = CharacterData(self._document, -1, self, x)
            self.children.append(cd)
        elif isinstance(x, int) or isinstance(x, float):
            # convert to str & wrap in CharaterData
            cd = CharacterData(self._document, -1, self, str(x))
            self.children.append(cd)
        elif isinstance(x, Node):
            self.children.append(x)
        else:
            raise ValueError('Children of ' + self.__class__.__name__ + ' must be subclass of Node; got: ' + x.__class__.__name__)

    def spawn_character_data(self, data):
        from .CharacterData import CharacterData
        n = CharacterData(self._document, -1, self, data)
        return n

    def spawn_comment(self, data):
        from .Comment import Comment
        n = Comment(self._document, -1, self, data)
        return n

    def spawn_element(self, name, attributes):
        from .Element import Element
        n = Element(self._document, -1, self, name, attributes)
        return n

    def spawn_processing_instruction(self, target, data):
        from .ProcessingInstruction import ProcessingInstruction
        n = ProcessingInstruction(self._document, -1, self, target, data)
        return n

    def count(self, *args, **kwargs):
        return self.children.count(*args, **kwargs)

    def index(self, *args, **kwargs):
        return self.children.index(*args, **kwargs)

    def extend(self, *args, **kwargs):
        return self.children.extend(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.children.insert(*args, **kwargs)

    def pop(self, *args, **kwargs):
        return self.children.pop(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self.children.remove(*args, **kwargs)

    def reverse(self, *args, **kwargs):
        return self.children.reverse(*args, **kwargs)

    def sort(self, *args, **kwargs):
        return self.children.sort(*args, **kwargs)
