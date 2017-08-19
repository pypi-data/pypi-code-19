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

from .Operator import Operator
from ..exceptions import XPathSyntaxException

logger = logging.getLogger(__name__)
class Expression(object):
    def __init__(self):
        self.children = []

    def evaluate(self, context_node, context_position, context_size, variables):
        logger.debug('Evaluating ' + str(self))
        if len(self.children) > 1:
            raise XPathSyntaxException('Expression has more than 1 child')

        v = self.children[0].evaluate(context_node, context_position, context_size, variables)
        logger.debug('Child ' + str(self.children[0]) + ' evaluated to ' + str(v))

        return v

    def __str__(self):
        return 'Expression ' + hex(id(self)) + ': [' + ','.join([str(x) for x in self.children]) + ']'
