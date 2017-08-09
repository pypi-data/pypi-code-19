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
import re
import xml.parsers.expat

from .CharacterData import CharacterData
from .Comment import Comment
from .Element import Element
from .Node import Node
from .ProcessingInstruction import ProcessingInstruction

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class Document(Node):
    @staticmethod
    def ordered_first(nodeset):
        if len(nodeset) == 0:
            return None
        n = nodeset[0]
        for i in range(1, len(nodeset)):
            if nodeset[i]._document_order < n._document_order:
                n = nodeset[i]
        return n

    @staticmethod
    def is_nodeset(nodeset):
        if not isinstance(nodeset, list):
            return False
        for n in nodeset:
            if not isinstance(n, Node):
                return False
        return True

    @staticmethod
    def order_sort(nodeset, reverse=False):
        if not Document.is_nodeset(nodeset):
            raise TypeError('Cannot sort by document order without a nodeset')
        return sorted(nodeset, key=lambda x: x._document_order, reverse=reverse)

    def __init__(self, encoding=None, skip_whitespace=True):
        super(Document, self).__init__(self, -1, None)
        self.version = None
        self.encoding = encoding
        self.standalone = None

        self.root_element = None
        self.children = []

        self._parser = xml.parsers.expat.ParserCreate(encoding=encoding)
        self._skip_whitespace = skip_whitespace
        self._in_space_preserve = False
        self._in_cdata = False
        self._stack = []
        self._element_index = {}
        self._order_count = 0

        self._parser.XmlDeclHandler = self._xml_decl_handler

        # we ignore dtds
        # self._parser.StartDoctypeDeclHandler = self._start_doctype_decl_handler
        # self._parser.EndDoctypeDeclHandler = self._end_doctype_decl_handler
        # self._parser.ElementDeclHandler = self._element_decl_handler
        # self._parser.AttlistDeclHandler = self._attlist_decl_handler
        #
        # self._parser.EntityDeclHandler = self._entity_decl_handler
        #
        # self._parser.NotationDeclHandler = self._notation_decl_handler
        #
        # self._parser.ExternalEntityRefHandler = self._external_entity_ref_handler

        # we do our own namespace processing
        # self._parser.StartNamespaceDeclHandler = self._start_namespace_handler
        # self._parser.EndNamespaceDeclHandler = self._end_namespace_handler

        self._parser.StartElementHandler = self._start_element_handler
        self._parser.EndElementHandler = self._end_element_handler

        self._parser.ProcessingInstructionHandler = self._processing_instruction_handler

        self._parser.CharacterDataHandler = self._character_data_handler

        self._parser.CommentHandler = self._comment_handler

        self._parser.StartCdataSectionHandler = self._start_cdata_section_handler
        self._parser.EndCdataSectionHandler = self._end_cdata_section_handler

        self._parser.DefaultHandlerExpand = self._default_handler_expand

        self._parser.NotStandaloneHandler = self._not_standalone_handler

    def parse(self, data, isfinal=True):
        logger.debug('Parsing data: ' + str(data))
        self._parser.Parse(data, isfinal)

        # TODO check that we're the only thing left on the stack when isfinal

    def parse_file(self, file_):
        logger.debug('Parsing file: ' + str(file_))
        self._parser.ParseFile(file_)

        # TODO check that we're the only thing left on the stack when isfinal

    def produce(self, xml_decl=True):
        s = ''
        if xml_decl:
            s = '<?xml version="'
            if self.version is None:
                self.version = 1.0
            s += str(self.version)
            s += '"'
            if self.encoding is None:
                self.encoding = 'UTF-8'
            s += ' encoding="' + self.encoding + '"'
            if self.standalone is not None:
                if self.standalone:
                    s += ' standalone="yes"'
                else:
                    s += ' standalone="no"'
            s += '>'

            for item in self.children:
                s += item.produce()

            return s.encode(self.encoding)

    def _xml_decl_handler(self, version, encoding, standalone):
        logger.debug('_xml_decl_handler version: ' + str(version) + ' encoding: ' + str(encoding) + ' standalone: ' + str(standalone))
        self.version = float(version)
        self.encoding = encoding
        if standalone is None or standalone == -1:
            self.standalone = None
        else:
            if standalone.lower() == 'yes':
                self.standalone = True
            else:
                self.standalone = False

    def _start_element_handler(self, name, attributes):
        logger.debug('_start_element_handler elname: ' + str(name) + ' attname: ' + str(name) + ' attributes: ' + str(attributes))

        # check for whitespace preservation
        if 'xml:space' in attributes and attributes['xml:space'] == 'preserve':
            self._in_space_preserve = True

        if len(self._stack) == 0:
            el = Element(self, self._order_count, self, name, attributes)
            self.root_element = el
            self.children.append(el)
        else:
            el = Element(self, self._order_count, self._stack[-1], name, attributes)
            self._stack[-1].children.append(el)
        self._order_count += 1

        if 'id' in attributes:
            self._element_index[attributes['id']] = el

        self._stack.append(el)

    def _end_element_handler(self, name):
        logger.debug('_end_element_handler name: ' + str(name))
        el = self._stack.pop()
        if el.name != name:
            raise ValueError('Stack pop element name (' + el.name + ') does not match end tag name: ' + name)

        # check for whitespace preservation
        if 'xml:space' in el.attributes and el.attributes['xml:space'] == 'preserve':
            self._in_space_preserve = False

    def _processing_instruction_handler(self, target, data):
        logger.debug('_processing_instruction_handler target: ' + str(target) + ' data: ' + str(data))

        if len(self._stack) == 0:
            pi = ProcessingInstruction(self, self._order_count, self, target, data)
            self.children.append(pi)
        else:
            pi = ProcessingInstruction(self, self._order_count, self._stack[-1], target, data)
            self._stack[-1].children.append(pi)
        self._order_count += 1

    def _character_data_handler(self, data):
        logger.debug('_character_data_handler data: ' + str(data.encode('UTF-8')))
        if not self._in_space_preserve:
            if self._skip_whitespace:
                data = data.strip(' \t\n')
                logger.debug('Stripped to: ' + str(data.encode('UTF-8')))
            if data == '':
                logger.debug('Skipping whitespace character data')
                return

        if len(self._stack) == 0:
            char_data = CharacterData(self, self._order_count, self, data, cdata_block=self._in_cdata)
            self.children.append(char_data)
        else:
            char_data = CharacterData(self, self._order_count, self._stack[-1], data, cdata_block=self._in_cdata)
            self._stack[-1].children.append(char_data)
        self._order_count += 1

    def _comment_handler(self, data):
        logger.debug('_comment_handler data: ' + str(data))

        if len(self._stack) == 0:
            c = Comment(self, self._order_count, data)
            self.children.append(c)
        else:
            c = Comment(self, self._order_count, self._stack[-1], data)
            self._stack[-1].children.append(c)
        self._order_count += 1

    def _start_cdata_section_handler(self):
        logger.debug('_start_cdata_section_handler')
        self._in_cdata = True

    def _end_cdata_section_handler(self):
        logger.debug('_end_cdata_section_handler')
        self._in_cdata = False

    def _default_handler_expand(self, data):
        logger.debug('_default_handler_expand data: ' + str(data))

    def _not_standalone_handler(self, data):
        logger.debug('_not_standalone_handler data: ' + str(data))

    # def _start_doctype_decl_handler(self, doctypeName, systemId, publicId, has_internal_subset):
    #     logger.debug('_start_doctype_decl_handler doctypeName: ' + str(doctypeName) + ' systemId: ' + str(systemId) + ' publicId: ' + str(publicId) + ' has_internal_subset: ' + str(has_internal_subset))
    #
    # def _end_doctype_decl_handler(self):
    #     logger.debug('_end_doctype_decl_handler')
    #
    # def _element_decl_handler(self, name, model):
    #     logger.debug('_element_decl_handler doctypeName: ' + str(name) + ' model: ' + str(model))
    #
    # def _attlist_decl_handler(self, elname, attname, type_, default, required):
    #     logger.debug('_attlist_decl_handler elname: ' + str(elname) + ' attname: ' + str(attname) + ' type_: ' + str(type_) + ' default: ' + str(default) + ' required: ' + str(required))
    #
    # def _entity_decl_handler(self, entityName, is_parameter_entity, value, base, systemId, publicId, notationName):
    #     logger.debug('_entity_decl_handler entityName: ' + str(entityName) + ' is_parameter_entity: ' + str(is_parameter_entity) + ' value: ' + str(value) + ' base: ' + str(base) + ' systemId: ' + str(systemId) + ' publicId: ' + str(publicId) + ' notationName: ' + str(notationName))
    #
    # def _notation_decl_handler(self, notationName, base, systemId, publicId):
    #     logger.debug('_notation_decl_handler notationName: ' + str(notationName) + ' base: ' + str(base) + ' systemId: ' + str(systemId) + ' publicId: ' + str(publicId))
    #
    # def _external_entity_ref_handler(self, context, base, systemId, publicId):
    #     logger.debug('_external_entity_ref_handler context: ' + str(context) + ' base: ' + str(base) + ' systemId: ' + str(systemId) + ' publicId: ' + str(publicId))

    # def _start_namespace_handler(self, prefix, uri):
    #     logger.debug('_start_namespace_handler prefix: ' + str(prefix) + ' uri: ' + str(uri))
    #     self.namespaces[prefix] = url
    #
    # def _end_namespace_handler(self, prefix):
    #     logger.debug('_end_namespace_handler prefix: ' + str(prefix))
    #     self._stack[-1].namespaces[prefix] = self.namespaces[prefix]

    def get_type(self):
        return 'root'

    def get_string_value(self):
        return self.root_element.get_string_value()

    def __len__(self):
        return len(self.children)

    def __getitem__(self, key):
        if not isinstance(key, int) and not isinstance(key, slice):
            raise TypeError('Key values must be of int type or slice')

        return self.children[key]

    def __setitem__(self, key, value):
        if not isinstance(key, int):
            raise TypeError('Key values must be of int type')
        if not isinstance(value, Node):
            raise TypeError('Values must be of Node type')

        self.children[key] = value

    def __delitem__(self, key):
        if not isinstance(key, int):
            raise TypeError('Key values must be of int type')

        del self.children[key]

    def __iter__(self):
        return iter(self.children)
