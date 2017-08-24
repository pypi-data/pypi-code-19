# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import nose.tools as nt

import sympy

from fastr.core.dimension import HasDimensions, Dimension
from fastr import exceptions


class Dimensional(HasDimensions):
    """
    Test implementation of a HasDimensions class for testing.
    """
    SIZE = (42, 1337, sympy.Symbol('X'))
    NAME = ('answer', 'l33t', 'vague')

    def __init__(self):
        self._dimensions = tuple(Dimension(x, y) for x, y in zip(self.NAME, self.SIZE))

    @property
    def dimensions(self):
        return self._dimensions


class TestDimension():
    """
    Test for the Dimension
    """
    def setup(self):
        self.cleese = Dimension('john', 196)
        self.palin = Dimension('michael', 178)

    def test_name(self):
        nt.eq_(self.cleese.name, 'john')
        nt.eq_(self.palin.name, 'michael')

    def test_size(self):
        nt.eq_(self.cleese.size, 196)
        nt.eq_(self.palin.size, 178)

    @nt.raises(exceptions.FastrTypeError)
    def test_wrong_size_type_str(self):
        Dimension('eric', 'idle')

    @nt.raises(exceptions.FastrTypeError)
    def test_wrong_size_type_float(self):
        Dimension('graham', 1.88)

    @nt.raises(exceptions.FastrTypeError)
    def test_wrong_name_type_unicode(self):
        Dimension(u'terry', 173)

    @nt.raises(exceptions.FastrValueError)
    def test_wrong_value_size(self):
        Dimension('negative', -1)


class TestHasDimension():
    """
    Tests for the Dimenions and HasDimensions mixin
    """
    def setup(self):
        self.test_object = Dimensional()

    def test_size(self):
        nt.eq_(self.test_object.size, self.test_object.SIZE)

    def test_dimnames(self):
        nt.eq_(self.test_object.dimnames, self.test_object.NAME)
