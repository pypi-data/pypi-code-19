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

from .ChildBearing import ChildBearing
from .Node import Node
from .Attribute import Attribute
from .Namespace import Namespace

from .exceptions import *

from publishsubscribe import PublishingDict
from publishsubscribe import Subscriber

logger = logging.getLogger(__name__)

class Element(ChildBearing, Subscriber):
    def __init__(self, local_name, attributes=None, prefix=None, namespace=None, parent=None):
        super(Element, self).__init__(parent=parent)

        if attributes is None:
            self._attributes = PublishingDict({})
        else:
            self._attributes = PublishingDict(attributes)

        self._prefix = prefix
        self._namespace = namespace
        self._local_name = local_name

        self._init_namespaces()
        self._init_attributes()

    # redefine parent property
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent
        self._init_namespaces()

    @property
    def attributes(self):
        return self._attributes

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

        if self._parent is not None:
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
        if self._parent is not None:
            self._namespace = self.prefix_to_namespace(self._prefix)

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        self._namespace = namespace
        if self._parent is not None:
            self._prefix = self.namespace_to_prefix(namespace)

    def data_added(self, publisher, addition):
        logger.debug('Added attributes: ' + str(addition))
        self._init_attributes()
        for k in addition:
            if k.startswith('xmlns'):
                self._init_namespaces()

    def data_updated(self, publisher, updates):
        logger.debug('Updated attributes: ' + str(updates))
        self._init_attributes()
        for k in updates:
            if k.startswith('xmlns'):
                self._init_namespaces()

    def data_deleted(self, publisher, deletion):
        logger.debug('Deleted attributes: ' + str(deletion))
        self._init_attributes()
        for k in deletion:
            if k.startswith('xmlns'):
                self._init_namespaces()

    def _init_attributes(self):
        # create nodes for each of the attributes
        self.attribute_nodes = {}
        for k, v in self._attributes.items():
            if ':' in k:
                prefix, colon, local_name = k.partition(':')
                # check prefix
                namespace = self.prefix_to_namespace(prefix)
            else:
                local_name = k
                prefix = None
                namespace = None
            n = Attribute(local_name, v, parent=self, prefix=prefix, namespace=namespace)
            self.attribute_nodes[k] = n

    def _init_namespaces(self):
        if isinstance(self._parent, Element):
            self._prefix_to_namespace = self._parent._prefix_to_namespace.copy()
            self._namespace_to_prefixes = self._parent._namespace_to_prefixes.copy()
        else:
            # parent is-a Document or None
            self._prefix_to_namespace = {
                'xml': 'http://www.w3.org/XML/1998/namespace',
            }
            self._namespace_to_prefixes = {
                'http://www.w3.org/XML/1998/namespace': 'xml',
            }

        # check for prefix namespaces
        for k, v in self._attributes.items():
            if k.startswith('xmlns:'):
                prefix = k.partition(':')[2]
                if prefix in self._prefix_to_namespace.keys():
                    raise PrefixRedefineException('Prefix ' + prefix + ' has already been used but is being redefined')
                self._prefix_to_namespace[prefix] = v
                self._namespace_to_prefixes[v] = prefix
                logger.debug('Added prefix ' + prefix + ' for uri ' + v)
            elif k.startswith('xmlns'):
                self._prefix_to_namespace[None] = v
                self._namespace_to_prefixes[v] = None
                logger.debug('Added prefix None for uri ' + v)

        # now that we've parsed the namespace attributes, we can figure out missing info
        if self._prefix is None and None in self._prefix_to_namespace:
            self._namespace = self._prefix_to_namespace[None]

        if self._prefix is None and self._namespace is not None:
            self._prefix = self.namespace_to_prefix(self._namespace)
        elif self._namespace is None and self._prefix is not None:
            self._namespace = self.prefix_to_namespace(self._prefix)

        # create nodes for each of the namespaces
        self.namespace_nodes = {}
        for prefix in self._prefix_to_namespace.keys():
            uri = self._prefix_to_namespace[prefix]
            n = Namespace(prefix, uri, parent=self)
            self.namespace_nodes[prefix] = n

    def prefix_to_namespace(self, prefix):
        logger.debug('Resolving prefix: ' + str(prefix))
        if prefix == 'xmlns':
            return 'http://www.w3.org/2000/xmlns/'
        elif prefix in self._prefix_to_namespace:
            return self._prefix_to_namespace[prefix]
        elif prefix is None:
            return None
        else:
            raise UnknownPrefixException('Unknown prefix: ' + str(prefix))

    def namespace_to_prefix(self, namespace):
        logger.debug('Resolving namespace: ' + str(namespace))
        if namespace == 'http://www.w3.org/2000/xmlns/':
            return 'xmlns'
        elif namespace in self._namespace_to_prefixes:
            return self._namespace_to_prefixes[namespace]
        else:
            raise UnknownNamespaceException('Unknown namespace uri: ' + str(namespace))

    def escape_attribute(self, text):
        return self.escape(text).replace('"', '&quot;')

    def produce(self):
        s = '<' + self.name
        for k, v in self.attributes.items():
            s += ' ' + self.escape(k) + '="' + self.escape_attribute(v) + '"'
        if len(self.children) == 0:
            s += '/>'
        else:
            s += '>'
            for c in self.children:
                s += c.produce()
            s += '</' + self.name + '>'

        return s

    def get_type(self):
        return 'element'

    def get_string_value(self):
        from .CharacterData import CharacterData
        s = ''
        for c in self.children:
            if isinstance(c, CharacterData):
                s += c.data
            elif isinstance(c, Element):
                s += c.get_string_value()
        return s

    def get_expanded_name(self):
        return (self.namespace, self.local_name)

    def __str__(self):
        s = self.__class__.__name__ + ' ' + hex(id(self)) + ' ' + self.name
        if 'id' in self.attributes:
            s += ' id=' + self.attributes['id']
        if 'name' in self.attributes:
            s += ' name=' + self.attributes['name']
        return s

    def find_by_id(self, id_):
        logger.debug(str(self) + ' checking attributes for id: ' + str(id_))
        for k, v in self.attributes.items():
            k = k.lower()
            if k.endswith(':id') or k == 'id':
                logger.debug(str(self) + ' found id: ' + str(v))
                if v == id_:
                    logger.debug(str(self) + ' matches id: ' + str(id_))
                    return self
                else:
                    logger.debug(str(self) + ' id ' + str(v) + ' does not match id: ' + str(id_))

        return super(Element, self).find_by_id(id_)

    def get_node_count(self):
        do = 1 + len(self.namespace_nodes) + len(self.attribute_nodes)
        for c in self.children:
            do += c.get_node_count()
        return do
