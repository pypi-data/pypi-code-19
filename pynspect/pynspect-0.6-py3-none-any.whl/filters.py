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
This module provides tools for data filtering based on filtering and query
grammar.

The filtering grammar is thoroughly described in following module:

* :py:mod:`pynspect.lexer`

  Lexical analyzer, descriptions of valid grammar tokens.

* :py:mod:`pynspect.gparser`

  Grammar parser, language grammar description

* :py:mod:`pynspect.rules`

  Object representation of grammar rules, interface definition

* :py:mod:`pynspect.jpath`

  The addressing language JPath.

Please refer to appropriate module for more in-depth information.

There are two main tools in this package:

* :py:class:`DataObjectFilter`

  Tool capable of filtering data structures according to given filtering rules.

* :py:class:`IDEAFilterCompiler`

  Filter compiler, that ensures appropriate data types for correct variable
  comparison evaluation.

.. todo::

    There is quite a lot of code that needs to be written before actual filtering
    can take place. In the future, there should be some kind of object, that will
    be tailored for immediate processing and will take care of initializing
    uderlying parser, compiler and filter. This object will be designed later.

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>"


import re
import ipranges

from pynspect.rules import IPV4Rule, IPV6Rule, IntegerRule, FloatRule, NumberRule, VariableRule,\
    LogicalBinOpRule, UnaryOperationRule, ComparisonBinOpRule, MathBinOpRule, ListRule,\
    RuleTreeTraverser
from pynspect.jpath import jpath_values


class DataObjectFilter(RuleTreeTraverser):
    """
    Rule tree traverser implementing  default object filtering logic.

    Following example demonstrates DataObjectFilter usage in conjuction with
    MentatFilterParser::

    >>> flt = DataObjectFilter()
    >>> psr = MentatFilterParser()
    >>> psr.build()
    >>> rule = psr.parse('ID like "e214d2d9"')
    >>> result = flt.filter(rule, test_msg)

    Alternativelly rule tree can be created by hand/programatically:

    >>> rule = ComparisonBinOpRule('OP_GT', VariableRule("ConnCount"), IntegerRule(1))
    >>> result = flt.filter(rule, test_msg1)
    """
    def filter(self, rule, data):
        """
        Apply given filtering rule to given data structure.

        :param Rule rule: filtering rule to be checked
        :param any data: data structure to check against rule, ussually dict
        :return: True or False or expression result
        :rtype: bool or any
        """
        return rule.traverse(self, obj = data)

    #---------------------------------------------------------------------------

    def ipv4(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return rule.value
    def ipv6(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return rule.value
    def integer(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return rule.value
    def constant(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return rule.value
    def variable(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return jpath_values(kwargs['obj'], rule.value)
    def list(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return [i.value for i in rule.value]
    def binary_operation_logical(self, rule, left, right, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return self.evaluate_binop_logical(rule.operation, left, right, **kwargs)
    def binary_operation_comparison(self, rule, left, right, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return self.evaluate_binop_comparison(rule.operation, left, right, **kwargs)
    def binary_operation_math(self, rule, left, right, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return self.evaluate_binop_math(rule.operation, left, right, **kwargs)
    def unary_operation(self, rule, right, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return self.evaluate_unop(rule.operation, right, **kwargs)


def compile_ip_v4(rule):
    """
    Compiler helper method: attempt to compile constant into object representing
    IPv4 address to enable relations and thus simple comparisons using Python
    operators.
    """
    if isinstance(rule.value, ipranges.Range):
        return rule
    return IPV4Rule(ipranges.from_str_v4(rule.value))

def compile_ip_v6(rule):
    """
    Compiler helper method: attempt to compile constant into object representing
    IPv6 address to enable relations and thus simple comparisons using Python
    operators.
    """
    if isinstance(rule.value, ipranges.Range):
        print("IPv6 {} already compiled".format(rule.value))
        return rule
    print("Compiling IPv6 {} to Range object".format(rule.value))
    return IPV6Rule(ipranges.from_str_v6(rule.value))

CVRE = re.compile(r'\[\d+\]')
def clean_variable(var):
    """
    Remove any array indices from variable name to enable indexing into :py:data:`COMPILATIONS`
    callback dictionary.

    This dictionary contains postprocessing callback appropriate for opposing
    operand of comparison operation for variable on given JPath.
    """
    return CVRE.sub('', var)


COMPILATIONS = {
    'Source.IP4': compile_ip_v4,
    'Target.IP4': compile_ip_v4,
    'Source.IP6': compile_ip_v6,
    'Target.IP6': compile_ip_v6,
}


class IDEAFilterCompiler(RuleTreeTraverser):
    """
    Rule tree traverser implementing IDEA filter compilation algorithm.

    Following example demonstrates DataObjectFilter usage in conjuction with
    MentatFilterParser::

    >>> msg_idea = lite.Idea(test_msg)
    >>> flt = DataObjectFilter()
    >>> cpl = IDEAFilterCompiler()
    >>> psr = MentatFilterParser()
    >>> psr.build()
    >>> rule = psr.parse('ID like "e214d2d9"')
    >>> rule = cpl.compile(rule)
    >>> result = flt.filter(rule, test_msg)
    """
    def compile(self, rule):
        """
        Compile given filtering rule into format appropriate for processing IDEA
        messages.

        :param Rule rule: filtering rule to be compiled
        :return: compiled filtering rule
        :rtype: Rule
        """
        return rule.traverse(self)


    #---------------------------------------------------------------------------


    def ipv4(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        rule = compile_ip_v4(rule)
        return rule

    def ipv6(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        rule = compile_ip_v4(rule)
        return rule

    def integer(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        rule.value = int(rule.value)
        return rule

    def constant(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return rule

    def variable(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return rule

    def list(self, rule, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return rule

    def binary_operation_logical(self, rule, left, right, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return LogicalBinOpRule(rule.operation, left, right)

    def binary_operation_comparison(self, rule, left, right, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        var = val = None
        if isinstance(left, VariableRule) and not isinstance(right, VariableRule):
            var = left
            val = right
        elif isinstance(right, VariableRule) and not isinstance(left, VariableRule):
            var = right
            val = left
        if var and val:
            path = clean_variable(var.value)
            if path in COMPILATIONS.keys():
                if isinstance(val, ListRule):
                    result = []
                    for itemv in val.value:
                        result.append(COMPILATIONS[path](itemv))
                    right = ListRule(result)
                else:
                    right = COMPILATIONS[path](val)
        return ComparisonBinOpRule(rule.operation, left, right)

    def binary_operation_math(self, rule, left, right, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        if isinstance(left, IntegerRule) and isinstance(right, IntegerRule):
            result = self.evaluate_binop_math(rule.operation, left.value, right.value)
            if isinstance(result, list):
                return ListRule([IntegerRule(r) for r in result])
            return IntegerRule(result)
        elif isinstance(left, NumberRule) and isinstance(right, NumberRule):
            result = self.evaluate_binop_math(rule.operation, left.value, right.value)
            if isinstance(result, list):
                return ListRule([FloatRule(r) for r in result])
            return FloatRule(result)
        return MathBinOpRule(rule.operation, left, right)

    def unary_operation(self, rule, right, **kwargs):
        """Implementation of :py:class:`pynspect.rules.RuleTreeTraverser` interface"""
        return UnaryOperationRule(rule.operation, right)


#
# Perform the demonstration.
#
if __name__ == "__main__":

    import pprint

    DEMO_DATA   = {"Test": 15, "Attr": "ABC"}
    DEMO_RULE   = ComparisonBinOpRule('OP_GT', VariableRule("Test"), IntegerRule(10))
    DEMO_FILTER = DataObjectFilter()
    pprint.pprint(DEMO_FILTER.filter(DEMO_RULE, DEMO_DATA))
