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

from .Function import Function
from ..exceptions import XPathSyntaxException

logger = logging.getLogger(__name__)
class Predicate(object):
    def __init__(self):
        self.children = []

    def evaluate(self, context_node, context_position, context_size, variables):
        if len(self.children) != 1:
            raise XPathSyntaxException('Predicate can only have 1 expression')

        v = self.children[0].evaluate(context_node, context_position, context_size, variables)

        if isinstance(v, bool):
            logger.debug('Boolean predicate subexpression: ' + str(v))
            return v
        elif isinstance(v, int) or isinstance(v, float):
            logger.debug('Numeric result for predicate subexpression: ' + str(v) + '; comparing to position()')
            return Function.f_position((), context_node, context_position, context_size, variables) == v
        else:
            v_b = Function.f_boolean((v,), context_node, context_position, context_size, variables)
            logger.debug('Converting predicate subexpression result ' + str(v) + ' to boolean: '  + str(v_b))
            return v_b

    def __str__(self):
        return 'Predicate ' + hex(id(self)) + ': [' + ','.join([str(x) for x in self.children]) + ']'
