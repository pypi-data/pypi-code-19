"""
Copyright (c) 2017 James Patrick Dill

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from struction.util import cast_type, isclass

allowed = ["default", "between", "clamp"]


def default(value):
    return "default", value


def between(min_value, max_value):
    return "between", (min_value, max_value)

def clamp(min_value, max_value):
    return "clamp", (min_value, max_value)


class Field(object):
    def __init__(self, *args):
        self.types = []

        self.default = None
        self.between = None
        self.clamp = None

        for arg in args:
            if isclass(arg):
                self.types.append(arg)
            elif isinstance(arg, tuple):
                if len(arg) != 2 or arg[0] not in allowed:
                    raise TypeError("Invalid argument specifier: {0!r}".format(arg))
                setattr(self, arg[0], arg[1])
            else:
                raise TypeError("Invalid argument specifier: {0!r}".format(arg))

        if self.default is not None and type(self.default) not in self.types:
            raise TypeError("Default field value must match one of field type(s)")
        if len(self.types) == 0:
            raise TypeError("No type specified for field")

    def __repr__(self):
        return "<{} default={!r}>".format(" ".join(t.__name__ for t in self.types), self.default)

    def match(self, value, typecasting=False):
        if value is None:
            return

        if typecasting:
            value = cast_type(value, *self.types)

        if type(value) not in self.types:
            raise TypeError("Value must match one of field type(s)")

        if self.clamp is not None:
            value = max(self.clamp[0], min(value, self.clamp[1]))
        elif self.between is not None:
            if not (self.between[0] <= value <= self.between[1]):
                raise ValueError("Value must be between ({}, {})".format(*self.between))

        return value
