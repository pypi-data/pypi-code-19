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
from .xpath.Literal import Literal

from .exceptions import *

logger = logging.getLogger(__name__)

class Attribute(Node):
    def __init__(self, local_name, value, parent=None, prefix=None, namespace=None):
        super(Attribute, self).__init__(parent=parent)

        self._prefix = prefix
        self._local_name = local_name
        self._namespace = namespace

        self.value = value

    @property
    def name(self):
        if self._prefix is None:
            return self._local_name
        else:
            return self._prefix + ':' + self._local_name

    @name.setter
    def name(self, name):
        if ':' in name:
            self._prefix, colon, self._name = name.partition(':')
        else:
            self._prefix = None
            self._name = name

        self._namespace = self.prefix_to_namespace(self._prefix)

    @property
    def local_name(self):
        return self._local_name

    @local_name.setter
    def local_name(self, local_name):
        self._local_name = local_name

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        self._prefix = prefix
        self._namespace = self.prefix_to_namespace(self._prefix)

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        self._namespace = namespace
        self._prefix = self.namespace_to_prefix(namespace)

    def get_type(self):
        return 'attribute'

    def get_string_value(self):
        return self.value

    def get_expanded_name(self):
        return (self.namespace, self.local_name)

    def __eq__(self, other):
        if isinstance(other, Literal):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        elif isinstance(other, int) or isinstance(other, float):
            return self.value == str(other)
        return object.__eq__(self, other)

    def __str__(self):
        s = self.__class__.__name__ + ' ' + hex(id(self)) + ' '
        if self.namespace is not None:
            s += self.namespace + ':'
        s += self.local_name + '=' + self.value
        return s

    def get_document_order(self):
        if self._parent is None:
            raise UnattachedElementException('Element ' + str(self) + ' is not attached to a document')

        do = self._parent.get_document_order()
        do += len(self._parent.namespace_nodes)
        ordered_attr = [self._parent.attribute_nodes[k] for k in sorted(self._parent.attribute_nodes.keys())]
        return do + ordered_attr.index(self)
