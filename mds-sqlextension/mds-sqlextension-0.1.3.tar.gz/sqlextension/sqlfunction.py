# -*- coding: utf-8 -*-
 
from sql.operators import BinaryOperator
from sql import Flavor
from sql.functions import Function

__all__ = ['FuzzyEqal', 'Ascii', 'Concat2', 'RPad', 'Lower', 'ArrayAgg', 
            'Replace', 'AnyInArray']


class FuzzyEqal(BinaryOperator):
    """ read: https://www.rdegges.com/2013/easy-fuzzy-text-searching-with-postgresql/
        run 'CREATE EXTENSION pg_trgm;' to enable fuzzymatch in postgresql
    """
    __slots__ = ()

    @property
    def _operator(self):
        # '%' must be escaped with format paramstyle
        if Flavor.get().paramstyle == 'format':
            return '%%'
        else:
            return '%'


class Ascii(Function):
    __slots__ = ()
    _function = 'ASCII'


class Concat2(Function):
    __slots__ = ()
    _function = 'CONCAT'


class RPad(Function):
    __slots__ = ()
    _function = 'RPAD'


class Lower(Function):
    __slots__ = ()
    _function = 'LOWER'


class ArrayAgg(Function):
    __slots__ = ()
    _function = 'ARRAY_AGG'


class Replace(Function):
    __slots__ = ()
    _function = 'REPLACE'


class AnyInArray(Function):
    __slots__ = ()
    _function = 'ANY'
  
    def __str__(self):
        Mapping = Flavor.get().function_mapping.get(self.__class__)
        if Mapping:
            return str(Mapping(*self.args))
        return self._function + '(' + ', '.join(
            map(self._format, self.args)) + '::int[])'
  
class SplitPart(Function):
    __slots__ = ()
    _function = 'SPLIT_PART'
