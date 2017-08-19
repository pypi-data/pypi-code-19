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

from .exceptions import *

logger = logging.getLogger(__name__)

class Namespace(Node):
    def __init__(self, prefix, uri, parent=None):
        super(Namespace, self).__init__(parent=parent)

        self.prefix = prefix
        self.uri = uri

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

    def get_type(self):
        return 'namespace'

    def get_string_value(self):
        return self.uri

    def get_expanded_name(self):
        return (None, self.prefix)

    def get_document_order(self):
        if self._parent is None:
            raise UnattachedElementException('Element ' + str(self) + ' is not attached to a document')

        do = self._parent.get_document_order()
        ordered_ns = [self._parent.namespace_nodes[k] for k in self._parent.namespace_nodes.keys()]
        return do + ordered_ns.index(self)
