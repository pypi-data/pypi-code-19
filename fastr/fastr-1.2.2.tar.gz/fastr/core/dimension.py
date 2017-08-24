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


from abc import ABCMeta, abstractproperty

import sympy

from fastr import exceptions


class Dimension(object):
    """
    A class representing a dimension. It contains the name and size of the
    dimension.
    """
    def __init__(self, name, size):
        """
        The constructor for the dimension.

        :param str name: Name of the dimension
        :param size: Size fo the dimension
        :type size: int or sympy.Symbol
        """
        if not isinstance(name, str):
            raise exceptions.FastrTypeError("Dimension.name should be a str, "
                                            "found [{}] {}".format(type(name).__name__,
                                                                   size))

        if not isinstance(size, (int, sympy.Symbol)):
            raise exceptions.FastrTypeError("Dimension.size should be an int or"
                                            " sympy.Symbol, found [{}] {}".format(type(size).__name__,
                                                                                  size))

        if isinstance(size, int) and size < 0:
            raise exceptions.FastrValueError("Dimension.size should be non-negative")

        self.name = name
        self.size = size


class HasDimensions(object):
    """
    A Mixin class for any object that has a notion of dimensions and size. It
    uses the dimension property to expose the dimension name and size.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def dimensions(self):
        """
        The dimensions has to be implemented by any subclass. It has to provide
        a tuple of Dimensions.

        :return: dimensions
        :rtype: tuple
        """

    @property
    def dimnames(self):
        """
        A tuple containing the dimension names of this object. All items of the
        tuple are of type str.
        """
        return tuple(x.name for x in self.dimensions)

    @property
    def size(self):
        """
        A tuple containing the size of this object. All items of the
        tuple are of type int or sympy.Symbol.
        """
        return tuple(x.size for x in self.dimensions)