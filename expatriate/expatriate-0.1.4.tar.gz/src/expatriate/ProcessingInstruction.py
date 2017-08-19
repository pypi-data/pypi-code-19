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

logger = logging.getLogger(__name__)

class ProcessingInstruction(Node):
    def __init__(self, target, data, parent=None):
        super(ProcessingInstruction, self).__init__(parent=parent)

        self.target = target
        self.data = data

    def produce(self):
        return '<?' + self.target + ' ' + self.data + '?>'

    def get_type(self):
        return 'processing instruction'

    def get_string_value(self):
        return self.data

    def get_expanded_name(self):
        return (None, self.target)
