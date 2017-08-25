#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Pynspect project (https://pypi.python.org/pypi/pynspect).
# Originally part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2016 CESNET, z.s.p.o (http://www.ces.net/).
# Copyright (C) since 2016 Jan Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains implementation of object representations of filtering
and query language grammar.

There is a separate class defined for each grammar rule. There are following
classes representing all possible constant and variable values (tree leaves,
without child nodes):

* :py:class:`VariableRule`
* :py:class:`ConstantRule`
* :py:class:`IPv4Rule`
* :py:class:`IPv6Rule`
* :py:class:`IntegerRule`
* :py:class:`FloatRule`
* :py:class:`ListRule`

There are following classes representing various binary and unary operations:

* :py:class:`LogicalBinOpRule`
* :py:class:`ComparisonBinOpRule`
* :py:class:`MathBinOpRule`
* :py:class:`UnaryOperationRule`

Desired hierarchical rule tree can be created either programatically, or by
parsing string rules using :py:mod:`pynspect.gparser`.

Working with rule tree is then done via objects implementing rule tree
traverser interface:

* :py:class:`RuleTreeTraverser`

The provided :py:class:`RuleTreeTraverser` class contains also implementation of
all necessary evaluation methods.

There is a simple example implementation of rule tree traverser capable of
printing rule tree into a formated string:

* :py:class:`PrintingTreeTraverser`

Rule evaluation
^^^^^^^^^^^^^^^

* Logical operations ``and or xor not exists``

  There is no special handling for operands of logical operations. Operand(s) are
  evaluated in logical expression exactly as they are received, there is no
  mangling involved.

* Comparison operations

    All comparison operations are designed to work with lists as both operands.
    This is because :py:func:`pynspect.jpath.jpath_values` function is
    used to retrieve variable values and this function always returns list.

    * Operation: ``is``

      Like in the case of logical operations, there is no mangling involved when
      evaluating this operation. Both operands are compared using Python`s native
      ``is`` operation and result is returned.

    * Operation: ``in``

      In this case left operand is iterated and each value is compared using Python`s
      native ``in`` operation with right operand. First ``True`` result wins and
      operation immediatelly returns ``True``, ``False`` is returned otherwise.

    * Any other operation: ``like eq ne gt ge lt le``

      In case of this operation both of the operands are iterated and each one is
      compared with each other. First ``True`` result wins and operation immediatelly
      returns ``True``, ``False`` is returned otherwise.

    * Math operations: ``+ - * / %``

      Current math operation implementation supports following options:

        * Both operands are lists of the same length. In this case corresponding
          elements at certain position within the list are evaluated with given
          operation. Result is a list.

        * One of the operands is a list, second is scalar value or list of the
          size 1. In this case given operation is evaluated with each element of
          the longer list. Result is a list.

        * Operands are lists of the different size. This option is **forbidden**
          and the result is ``None``.

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import re
import datetime
import calendar

import ipranges

# For python2 compatibility: conversion of datetime.
def py2_timestamp(val):
    """
    Get unix timestamp value out of given datetime object.
    """
    return calendar.timegm(val.timetuple()) + val.microsecond / 1000000.0


class FilteringRuleException(Exception):
    """
    Custom filtering rule specific exception.

    This exception will be thrown on module specific errors.
    """
    def __init__(self, description):
        super().__init__()
        self._description = description
    def __str__(self):
        return repr(self._description)


class Rule():
    """
    Base class for all filter tree rules.
    """
    pass


class ValueRule(Rule):
    """
    Base class for all filter tree value rules.
    """
    pass


class VariableRule(ValueRule):
    """
    Class for expression variables.
    """
    def __init__(self, value):
        """
        Initialize the variable with given path value.
        """
        self.value = value

    def __str__(self):
        return "{}".format(self.value)

    def __repr__(self):
        return "VARIABLE({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        return traverser.variable(self, **kwargs)


class ConstantRule(ValueRule):
    """
    Class for all expression constant values.
    """
    def __init__(self, value):
        """
        Initialize the constant with given value.
        """
        self.value = value

    def __str__(self):
        return '"{}"'.format(self.value)

    def __repr__(self):
        return "CONSTANT({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        return traverser.constant(self, **kwargs)


class IPV4Rule(ConstantRule):
    """
    Class for IPv4 address constants.
    """
    def __str__(self):
        return '{}'.format(self.value)

    def __repr__(self):
        return "IPV4({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        return traverser.ipv4(self, **kwargs)


class IPV6Rule(ConstantRule):
    """
    Class for IPv6 address constants.
    """
    def __str__(self):
        return '{}'.format(self.value)

    def __repr__(self):
        return "IPV6({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        return traverser.ipv6(self, **kwargs)


class NumberRule(ConstantRule):
    """
    Base class for all numerical constants.
    """
    pass


class IntegerRule(NumberRule):
    """
    Class for integer constants.
    """
    def __str__(self):
        return '{}'.format(self.value)

    def __repr__(self):
        return "INTEGER({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        return traverser.integer(self, **kwargs)


class FloatRule(NumberRule):
    """
    Class for float constants.
    """
    def __str__(self):
        return '{}'.format(self.value)

    def __repr__(self):
        return "FLOAT({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        return traverser.float(self, **kwargs)


class ListRule(ValueRule):
    """
    Base class for all filter tree rules.
    """
    def __init__(self, rule, next_rule = None):
        """
        Initialize the constant with given value.
        """
        if not isinstance(rule, list):
            rule = [rule]
        self.value = rule
        if next_rule:
            self.value += next_rule.value

    def __str__(self):
        return '[{}]'.format(', '.join([str(v) for v in self.value]))

    def __repr__(self):
        return "LIST({})".format(', '.join([repr(v) for v in self.value]))

    def traverse(self, traverser, **kwargs):
        return traverser.list(self, **kwargs)


class OperationRule(Rule):
    """
    Base class for all expression operations (both unary and binary).
    """
    pass


class BinaryOperationRule(OperationRule):
    """
    Base class for all binary operations.
    """
    def __init__(self, operation, left, right):
        """
        Initialize the object with operation type and both operands.
        """
        self.operation = operation
        self.left = left
        self.right = right

    def __str__(self):
        return "({} {} {})".format(str(self.left), str(self.operation), str(self.right))


class LogicalBinOpRule(BinaryOperationRule):
    """
    Base class for all logical binary operations.
    """
    def __repr__(self):
        return "LOGBINOP({} {} {})".format(repr(self.left), str(self.operation), repr(self.right))

    def traverse(self, traverser, **kwargs):
        lrt = self.left.traverse(traverser, **kwargs)
        rrt = self.right.traverse(traverser, **kwargs)
        return traverser.binary_operation_logical(self, lrt, rrt, **kwargs)


class ComparisonBinOpRule(BinaryOperationRule):
    """
    Base class for all comparison binary operations.
    """
    def __repr__(self):
        return "COMPBINOP({} {} {})".format(repr(self.left), str(self.operation), repr(self.right))

    def traverse(self, traverser, **kwargs):
        lrt = self.left.traverse(traverser, **kwargs)
        rrt = self.right.traverse(traverser, **kwargs)
        return traverser.binary_operation_comparison(self, lrt, rrt, **kwargs)


class MathBinOpRule(BinaryOperationRule):
    """
    Base class for all mathematical binary operations.
    """
    def __repr__(self):
        return "MATHBINOP({} {} {})".format(repr(self.left), str(self.operation), repr(self.right))

    def traverse(self, traverser, **kwargs):
        lrt = self.left.traverse(traverser, **kwargs)
        rrt = self.right.traverse(traverser, **kwargs)
        return traverser.binary_operation_math(self, lrt, rrt, **kwargs)


class UnaryOperationRule(OperationRule):
    """
    Base class for all unary operations.
    """
    def __init__(self, operation, right):
        """
        Initialize the object with operation type operand.
        """
        self.operation = operation
        self.right = right

    def __str__(self):
        return "({} {})".format(str(self.operation), str(self.right))

    def __repr__(self):
        return "UNOP({} {})".format(str(self.operation), repr(self.right))

    def traverse(self, traverser, **kwargs):
        rrt = self.right.traverse(traverser, **kwargs)
        return traverser.unary_operation(self, rrt, **kwargs)

def _to_numeric(val):
    """
    Helper function for conversion of various data types into numeric representation.
    """
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, datetime.datetime):
        try:
            return val.timestamp()
        except:
            # python 2 compatibility
            return py2_timestamp(val)

    return float(val)


class RuleTreeTraverser():
    """
    Base class for all rule tree traversers.
    """

    binops_logical = {
        'OP_OR':    lambda x, y : x or y,
        'OP_XOR':   lambda x, y : (x and not y) or (not x and y),
        'OP_AND':   lambda x, y : x and y,
        'OP_OR_P':  lambda x, y : x or y,
        'OP_XOR_P': lambda x, y : (x and not y) or (not x and y),
        'OP_AND_P': lambda x, y : x and y,
    }
    """
    Definitions of all logical binary operations.
    """

    def __is_ip_list(self, right):
        for itemr in right:
            typer = type(itemr)
            if typer is ipranges.IP4Net or typer is ipranges.IP6Net or typer is ipranges.IP4Range or typer is ipranges.IP6Range:
                return True
        return False

    def __op_in_iplist(self, left, right):
        for itemr in right:
            if left in itemr:
                return True
        return False

    binops_comparison = {
        'OP_LIKE': lambda x, y : re.search(y, x),
        'OP_IN':   lambda x, y : x in y,
        'OP_IS':   lambda x, y : x == y,
        'OP_EQ':   lambda x, y : x == y,
        'OP_NE':   lambda x, y : x != y,
        'OP_GT':   lambda x, y : x > y,
        'OP_GE':   lambda x, y : x >= y,
        'OP_LT':   lambda x, y : x < y,
        'OP_LE':   lambda x, y : x <= y,
    }
    """
    Definitions of all comparison binary operations.
    """

    binops_math = {
        'OP_PLUS':   lambda x, y : x + y,
        'OP_MINUS':  lambda x, y : x - y,
        'OP_TIMES':  lambda x, y : x * y,
        'OP_DIVIDE': lambda x, y : x / y,
        'OP_MODULO': lambda x, y : x % y,
    }
    """
    Definitions of all mathematical binary operations.
    """

    unops = {
        'OP_NOT':    lambda x : not x,
        'OP_EXISTS': lambda x : x,
    }
    """
    Definitions of all unary operations.
    """

    def evaluate_binop_logical(self, operation, left, right, **kwargs):
        """
        Evaluate given logical binary operation with given operands.
        """
        if not operation in self.binops_logical:
            raise Exception("Invalid logical binary operation '{}'".format(operation))
        result = self.binops_logical[operation](left, right)
        return bool(result)

    def evaluate_binop_comparison(self, operation, left, right, **kwargs):
        """
        Evaluate given comparison binary operation with given operands.
        """
        if not operation in self.binops_comparison:
            raise Exception("Invalid comparison binary operation '{}'".format(operation))
        if left is None or right is None:
            return None
        if not isinstance(left, list):
            left = [left]
        if not isinstance(right, list):
            right = [right]
        if not left or not right:
            return None
        if operation in ['OP_IS']:
            res = self.binops_comparison[operation](left, right)
            if res:
                return True
        elif operation in ['OP_IN']:
            if not self.__is_ip_list(right):
                for iteml in left:
                    res = self.binops_comparison[operation](iteml, right)
                    if res:
                        return True
            else:
                for iteml in left:
                    res = self.__op_in_iplist(iteml, right)
                    if res:
                        return True
        else:
            for iteml in left:
                if iteml is None:
                    continue
                for itemr in right:
                    if itemr is None:
                        continue
                    res = self.binops_comparison[operation](iteml, itemr)
                    if res:
                        return True
        return False

    def _calculate_vector(self, operation, left, right):
        """
        Calculate vector result from two list operands with given mathematical operation.
        """
        result = []
        if len(right) == 1:
            right = _to_numeric(right[0])
            for iteml in left:
                iteml = _to_numeric(iteml)
                result.append(self.binops_math[operation](iteml, right))
        elif len(left) == 1:
            left = _to_numeric(left[0])
            for itemr in right:
                itemr = _to_numeric(itemr)
                result.append(self.binops_math[operation](left, itemr))
        elif len(left) == len(right):
            for iteml, itemr in zip(left, right):
                iteml = _to_numeric(iteml)
                itemr = _to_numeric(itemr)
                result.append(self.binops_math[operation](iteml, itemr))
        else:
            raise FilteringRuleException("Uneven length of math operation '{}' operands".format(operation))
        return result

    def evaluate_binop_math(self, operation, left, right, **kwargs):
        """
        Evaluate given mathematical binary operation with given operands.
        """
        if not operation in self.binops_math:
            raise Exception("Invalid math binary operation '{}'".format(operation))
        if left is None or right is None:
            return None
        if not isinstance(left, list):
            left = [left]
        if not isinstance(right, list):
            right = [right]
        if not left or not right:
            return None
        try:
            vect = self._calculate_vector(operation, left, right)
            if len(vect) > 1:
                return vect
            return vect[0]
        except:
            return None

    def evaluate_unop(self, operation, right, **kwargs):
        """
        Evaluate given unary operation with given operand.
        """
        if not operation in self.unops:
            raise Exception("Invalid unary operation '{}'".format(operation))
        if right is None:
            return None
        return self.unops[operation](right)

    #def evaluate(self, operation, *args):
    #    """
    #    Master method for evaluating any operation (both unary and binary).
    #    """
    #    if operation in self.binops_comparison:
    #        return self.evaluate_binop_comparison(operation, *args)
    #    if operation in self.binops_logical:
    #        return self.evaluate_binop_logical(operation, *args)
    #    if operation in self.binops_math:
    #        return self.evaluate_binop_math(operation, *args)
    #    if operation in self.unops:
    #        return self.evaluate_unop(operation, *args)
    #    raise Exception("Invalid operation '{}'".format(operation))


class PrintingTreeTraverser(RuleTreeTraverser):
    """
    Demonstation of simple rule tree traverser - printing traverser.
    """
    def ipv4(self, rule, **kwargs):
        return "IPV4({})".format(rule.value)
    def ipv6(self, rule, **kwargs):
        return "IPV6({})".format(rule.value)
    def integer(self, rule, **kwargs):
        return "INTEGER({})".format(rule.value)
    def float(self, rule, **kwargs):
        return "FLOAT({})".format(rule.value)
    def constant(self, rule, **kwargs):
        return "CONSTANT({})".format(rule.value)
    def variable(self, rule, **kwargs):
        return "VARIABLE({})".format(rule.value)
    def list(self, rule, **kwargs):
        return "LIST({})".format(', '.join([str(v) for v in rule.value]))
    def binary_operation_logical(self, rule, left, right, **kwargs):
        return "LOGBINOP({};{};{})".format(rule.operation, left, right)
    def binary_operation_comparison(self, rule, left, right, **kwargs):
        return "COMPBINOP({};{};{})".format(rule.operation, left, right)
    def binary_operation_math(self, rule, left, right, **kwargs):
        return "MATHBINOP({};{};{})".format(rule.operation, left, right)
    def unary_operation(self, rule, right, **kwargs):
        return "UNOP({};{})".format(rule.operation, right)


#
# Perform the demonstration.
#
if __name__ == "__main__":

    print("* Rule usage:")
    RULE_VAR = VariableRule("Test")
    print("STR:  {}".format(str(RULE_VAR)))
    print("REPR: {}".format(repr(RULE_VAR)))
    RULE_CONST = ConstantRule("constant")
    print("STR:  {}".format(str(RULE_CONST)))
    print("REPR: {}".format(repr(RULE_CONST)))
    RULE_IPV4 = IPV4Rule("127.0.0.1")
    print("STR:  {}".format(str(RULE_IPV4)))
    print("REPR: {}".format(repr(RULE_IPV4)))
    RULE_IPV6 = IPV6Rule("::1")
    print("STR:  {}".format(str(RULE_IPV6)))
    print("REPR: {}".format(repr(RULE_IPV6)))
    RULE_INTEGER = IntegerRule(15)
    print("STR:  {}".format(str(RULE_INTEGER)))
    print("REPR: {}".format(repr(RULE_INTEGER)))
    RULE_FLOAT = FloatRule(15.5)
    print("STR:  {}".format(str(RULE_FLOAT)))
    print("REPR: {}".format(repr(RULE_FLOAT)))
    RULE_BINOP_L = LogicalBinOpRule('OP_OR', RULE_VAR, RULE_INTEGER)
    print("STR:  {}".format(str(RULE_BINOP_L)))
    print("REPR: {}".format(repr(RULE_BINOP_L)))
    RULE_BINOP_C = ComparisonBinOpRule('OP_GT', RULE_VAR, RULE_INTEGER)
    print("STR:  {}".format(str(RULE_BINOP_C)))
    print("REPR: {}".format(repr(RULE_BINOP_C)))
    RULE_BINOP_M = MathBinOpRule('OP_PLUS', RULE_VAR, RULE_INTEGER)
    print("STR:  {}".format(str(RULE_BINOP_M)))
    print("REPR: {}".format(repr(RULE_BINOP_M)))
    RULE_BINOP = LogicalBinOpRule('OP_OR', ComparisonBinOpRule('OP_GT', MathBinOpRule('OP_PLUS', VariableRule("Test"), IntegerRule(10)), IntegerRule(20)), ComparisonBinOpRule('OP_LT', VariableRule("Test"), IntegerRule(5)))
    print("STR:  {}".format(str(RULE_BINOP)))
    print("REPR: {}".format(repr(RULE_BINOP)))
    RULE_UNOP = UnaryOperationRule('OP_NOT', RULE_VAR)
    print("STR:  {}".format(str(RULE_UNOP)))
    print("REPR: {}".format(repr(RULE_UNOP)))

    print("\n* Traverser usage:")
    RULE_TRAVERSER = PrintingTreeTraverser()
    print("{}".format(RULE_BINOP_L.traverse(RULE_TRAVERSER)))
    print("{}".format(RULE_BINOP_C.traverse(RULE_TRAVERSER)))
    print("{}".format(RULE_BINOP_M.traverse(RULE_TRAVERSER)))
    print("{}".format(RULE_BINOP.traverse(RULE_TRAVERSER)))
    print("{}".format(RULE_UNOP.traverse(RULE_TRAVERSER)))
