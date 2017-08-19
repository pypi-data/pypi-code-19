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

from .Step import Step

logger = logging.getLogger(__name__)
class RootStep(Step):
    def __init__(self, document):
        self.children = []
        self._document = document

    def evaluate(self, context_node, context_position, context_size, variables):
        if len(self.children) == 0:
            logger.debug('Root step with no children: using ' + str(self._document) + ' as the result set')
            return [self._document]
        else:
            return super(RootStep, self).evaluate(self._document, 1, 1, variables)

    def __str__(self):
        return 'RootStep ' + hex(id(self)) + ': [' + ','.join([str(x) for x in self.children]) + ']'
