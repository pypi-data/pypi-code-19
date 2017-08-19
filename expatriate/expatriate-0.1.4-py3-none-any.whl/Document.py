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
from .ChildBearing import ChildBearing
from .Comment import Comment
from .Element import Element
from .Node import Node
from .ProcessingInstruction import ProcessingInstruction

from .exceptions import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Document(ChildBearing):
    @staticmethod
    def ordered_first(nodeset):
        if len(nodeset) == 0:
            raise ValueError('Cannot determine the first node of an empty nodeset')
        first = nodeset[0]
        for n in nodeset[1:]:
            if n.get_document_order() < first.get_document_order():
                first = n
        return first

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
        for n in nodeset:
            logger.info(str(n) + ' document order: ' + str(n.get_document_order()))
        return sorted(nodeset, key=lambda n: n.get_document_order(), reverse=reverse)

    def __init__(self, encoding=None, skip_whitespace=True):
        super(Document, self).__init__()
        self.version = None
        self.encoding = encoding
        self.standalone = None

        self.root_element = None

        self._parser = xml.parsers.expat.ParserCreate(encoding=encoding)
        self._skip_whitespace = skip_whitespace
        self._in_space_preserve = False
        self._in_cdata = False
        self._stack = []

        self._parser.XmlDeclHandler = self._xml_decl_handler
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

        if ':' in name:
            prefix, colon, local_name = name.partition(':')
        else:
            prefix = None
            local_name = name

        if len(self._stack) == 0:
            el = Element(local_name, attributes, parent=self, prefix=prefix)
            self.root_element = el
            self.children.append(el)
        else:
            el = Element(local_name, attributes, parent=self._stack[-1], prefix=prefix)
            self._stack[-1].children.append(el)

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
            pi = ProcessingInstruction(target, data, parent=self)
            self.children.append(pi)
        else:
            pi = ProcessingInstruction(target, data, parent=self._stack[-1])
            self._stack[-1].children.append(pi)

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
            char_data = CharacterData(data, cdata_block=self._in_cdata, parent=self)
            self.children.append(char_data)
        else:
            char_data = CharacterData(data, cdata_block=self._in_cdata, parent=self._stack[-1])
            self._stack[-1].children.append(char_data)

    def _comment_handler(self, data):
        logger.debug('_comment_handler data: ' + str(data))

        if len(self._stack) == 0:
            c = Comment(data, parent=self)
            self.children.append(c)
        else:
            c = Comment(data, parent=self._stack[-1])
            self._stack[-1].children.append(c)

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

    def get_type(self):
        return 'root'

    def get_string_value(self):
        return self.root_element.get_string_value()

    def get_document_order(self):
        return 0

    def prefix_to_namespace(self, prefix):
        if prefix == 'xmlns':
            return 'http://www.w3.org/2000/xmlns/'
        elif prefix == 'xml':
            return 'http://www.w3.org/XML/1998/namespace'
        else:
            raise UnknownPrefixException('Unknown prefix: ' + str(prefix))

    def namespace_to_prefix(self, namespace_uri):
        if namespace_uri == 'http://www.w3.org/2000/xmlns/':
            return 'xmlns'
        elif namespace_uri == 'http://www.w3.org/XML/1998/namespace':
            return 'xml'
        else:
            raise UnknownNamespaceException('Unknown namespace uri: ' + str(namespace_uri))
