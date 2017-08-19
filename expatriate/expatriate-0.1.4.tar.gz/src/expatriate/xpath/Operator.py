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
import math

from .Function import Function
from ..exceptions import XPathSyntaxException

logger = logging.getLogger(__name__)
class Operator(object):
    def op_div(left, right):
        if right == 0:
            if left > 0:
                return math.inf
            else:
                return -math.inf
        else:
            return left // right

    OPERATORS = {
        '*': lambda x,y: x * y,
        # /
        # //
        # |
        '+': lambda x,y: x + y,
        '-': lambda x,y: x - y,
        '=': lambda x,y: x == y,
        '!=': lambda x,y: x != y,
        '<': lambda x,y: x < y,
        '<=': lambda x,y: x <= y,
        '>': lambda x,y: x > y,
        '>=': lambda x,y: x >= y,
        'and': lambda x,y: x and y,
        'or': lambda x,y: x or y,
        'mod': lambda x,y: math.fmod(x, y),
        'div': op_div,
        'negate': lambda x: - x,
    }
    def __init__(self, op):
        self.op = op
        self.children = []

    def evaluate(self, context_node, context_position, context_size, variables):
        from .Axis import Axis

        if self.op == 'negate':
            left = self.children[0].evaluate(context_node, context_position, context_size, variables)
            if isinstance(left, list):
                raise XPathSyntaxException('Got negate operator with a nodeset')
            elif isinstance(left, str):
                left = Functions.f_number(left)
            elif isinstance(left, bool):
                return not left
            elif isinstance(left, int) or isinstance(left, float):
                pass
            else:
                raise XPathSyntaxException('Unknown operand: ' + str(left))

            logger.debug('Negating ' + str(left))
            return Operator.OPERATORS['negate'](left)
        else:
            left = self.children[0].evaluate(context_node, context_position, context_size, variables)
            right = self.children[1].evaluate(context_node, context_position, context_size, variables)

            if self.op in ['or', 'and']:
                left = Function.f_boolean((left,), context_node, context_position, context_size, variables)
                right = Function.f_boolean((right,), context_node, context_position, context_size, variables)
            elif self.op in ['+', '-', 'div', 'mod']:
                left = Function.f_number((left,), context_node, context_position, context_size, variables)
                right = Function.f_number((right,), context_node, context_position, context_size, variables)

            if isinstance(left, list) and isinstance(right, list):
                for l in left:
                    l = Function.f_string((l,), context_node, context_position, context_size, variables)
                    for r in right:
                        r = Function.f_string((r,), context_node, context_position, context_size, variables)
                        logger.debug('Operator ' + str(l) + self.op + str(r))
                        if Operator.OPERATORS[self.op](l, r):
                            return True
                return False
            elif isinstance(left, list):
                if isinstance(right, int) or isinstance(right, float):
                    for x in left:
                        x = Function.f_number(Function.f_string((x,), context_node, context_position, context_size, variables))
                        logger.debug('Operator ' + str(x) + self.op + str(right))
                        if Operator.OPERATORS[self.op](x, right):
                            return True
                    return False
                elif isinstance(right, str):
                    for x in left:
                        x = Function.f_string((x,), context_node, context_position, context_size, variables)
                        logger.debug('Operator ' + str(x) + self.op + str(right))
                        if Operator.OPERATORS[self.op](x, right):
                            return True
                    return False
                elif isinstance(right, bool):
                    left = Function.f_boolean((left,), context_node, context_position, context_size, variables)
                    logger.debug('Operator ' + str(left) + self.op + str(right))
                    return Operator.OPERATORS[self.op](left, right)
                else:
                    raise XPathSyntaxException('Unknown right hand operand: ' + str(right))
            elif isinstance(right, list):
                if isinstance(left, int) or isinstance(left, float):
                    for x in right:
                        x = Function.f_number(Function.f_string((x,), context_node, context_position, context_size, variables))
                        logger.debug('Operator ' + str(left) + self.op + str(x))
                        if Operator.OPERATORS[self.op](left, x):
                            return True
                    return False
                elif isinstance(left, str):
                    for x in right:
                        x = Function.f_string((x,), context_node, context_position, context_size, variables)
                        logger.debug('Operator ' + str(left) + self.op + str(x))
                        if Operator.OPERATORS[self.op](left, x):
                            return True
                    return False
                elif isinstance(left, bool):
                    right = Function.f_boolean((right,), context_node, context_position, context_size, variables)
                    logger.debug('Operator ' + str(left) + self.op + str(right))
                    return Operator.OPERATORS[self.op](left, right)
                else:
                    raise XPathSyntaxException('Unknown left hand operand: ' + str(left))
            else:
                if isinstance(left, bool) or isinstance(right, bool):
                    left = Function.f_boolean((left,), context_node, context_position, context_size, variables)
                    right = Function.f_boolean((right,), context_node, context_position, context_size, variables)
                    logger.debug('Operator ' + str(left) + self.op + str(right))
                    return Operator.OPERATORS[self.op](left, right)
                elif isinstance(left, int) or isinstance(left, float) \
                or isinstance(right, int) or isinstance(right, float):
                    left = Function.f_number((left,), context_node, context_position, context_size, variables)
                    right = Function.f_number((right,), context_node, context_position, context_size, variables)
                    logger.debug('Operator ' + str(left) + self.op + str(right))
                    return Operator.OPERATORS[self.op](left, right)
                elif isinstance(left, str) or isinstance(right, str):
                    left = Function.f_string((left,), context_node, context_position, context_size, variables)
                    right = Function.f_string((right,), context_node, context_position, context_size, variables)
                    logger.debug('Operator ' + str(left) + self.op + str(right))
                    return Operator.OPERATORS[self.op](left, right)
                else:
                    return Operator.OPERATORS[self.op](left, right)

    def __str__(self):
        return 'Operator ' + self.op + ' ' + hex(id(self)) + ': [' + ','.join([str(x) for x in self.children]) + ']'
