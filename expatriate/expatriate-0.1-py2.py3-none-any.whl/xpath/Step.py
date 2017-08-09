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

from .Axis import Axis

logger = logging.getLogger(__name__)
class Step(object):
    def __init__(self):
        self.children = []

    def evaluate(self, context_node, context_position, context_size, variables):
        from ..Document import Document
        if len(self.children) == 1:
            logger.debug('Collecting nodes with ' + str(self.children[0]) + ' for context node ' + str(context_node))
            ns = self.children[0].evaluate(context_node, context_position, context_size, variables)
            logger.debug('Nodes from ' + str(self.children[0]) + ': [' + ','.join([str(x) for x in ns]) + ']')

            logger.debug(str(self) + ' nodeset: [' + ','.join([str(x) for x in ns]) + ']')
            return ns
        elif len(self.children) == 2:
            logger.debug('Collecting context nodes with ' + str(self.children[0]) + ' for context node ' + str(context_node))
            context_nodes = self.children[0].evaluate(context_node, context_position, context_size, variables)
            logger.debug('Context nodes from ' + str(self.children[0]) + ': [' + ','.join([str(x) for x in context_nodes]) + ']')

            ns = []
            for i in range(len(context_nodes)):
                logger.debug('Evaluating ' + str(self.children[1]) + ' with context ' + str(context_nodes[i]))
                ns.extend(self.children[1].evaluate(context_nodes[i], i+1, len(context_nodes), variables))

            ns = Document.order_sort(ns)
            logger.debug(str(self) + ' nodeset: [' + ','.join([str(x) for x in ns]) + ']')
            return ns
        else:
            raise SyntaxException('Steps require between 1 and 2 children')

    def __str__(self):
        return 'Step ' + hex(id(self)) + ': [' + ','.join([str(x) for x in self.children]) + ']'
