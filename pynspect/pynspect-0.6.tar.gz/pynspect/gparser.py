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
This module contains object encapsulation of `PLY <http://www.dabeaz.com/ply/>`__
parser for filtering and query language grammar used in Mentat project.

Grammar features
^^^^^^^^^^^^^^^^

* Logical operations: ``and or xor not exists``

  All logical operations support upper case and lower case name variants.
  Additionally, there are also symbolic variants ``|| ^^ && ! ?`` with higher
  priority and which can be used in some cases instead of parentheses.

* Comparison operations: ``like in is eq ne gt ge lt le``

  All comparison operations support upper case and lower case name variants.
  Additionally, there are also symbolic variants.

* Mathematical operations: ``+ - * / %``
* JPath variables: ``Source[0].IP4[1]``
* Directly recognized constants:

    * IPv4: ``127.0.0.1 127.0.0.1/32 127.0.0.1-127.0.0.5 127.0.0.1..127.0.0.5``
    * IPv6: ``::1 ::1/64 ::1-::5 ::1..::5``
    * integer: ``0 1 42``
    * float: ``3.14159``
* Quoted literal constants: ``"double quotes"`` or ``'single quotes'``

For more details on supported grammar token syntax please see the documentation
of :py:mod:`pynspect.lexer` module.

Currently implemented grammar
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bnf

    expression : xor_expression OP_OR expression
               | xor_expression

    xor_expression : and_expression OP_XOR xor_expression
                   | and_expression

    and_expression : or_p_expression OP_AND and_expression
                   | or_p_expression

    or_p_expression : xor_p_expression OP_OR_P or_p_expression
                    | xor_p_expression

    xor_p_expression : and_p_expression OP_XOR_P xor_p_expression
                     | and_p_expression

    and_p_expression : not_expression OP_AND_P and_p_expression
                     | not_expression

    not_expression : OP_NOT ex_expression
                   | ex_expression

    ex_expression : OP_EXISTS cmp_expression
                  | cmp_expression

    cmp_expression : term OP_LIKE cmp_expression
                   | term OP_IN cmp_expression
                   | term OP_IS cmp_expression
                   | term OP_EQ cmp_expression
                   | term OP_NE cmp_expression
                   | term OP_GT cmp_expression
                   | term OP_GE cmp_expression
                   | term OP_LT cmp_expression
                   | term OP_LE cmp_expression
                   | term

    term : factor OP_PLUS term
         | factor OP_MINUS term
         | factor OP_TIMES term
         | factor OP_DIVIDE term
         | factor OP_MODULO term
         | factor

    factor : IPV4
           | IPV6
           | INTEGER
           | FLOAT
           | VARIABLE
           | CONSTANT
           | LBRACK list RBRACK
           | LPAREN expression RPAREN

    list : IPV4
         | IPV6
         | INTEGER
         | FLOAT
         | VARIABLE
         | CONSTANT
         | IPV4 COMMA list
         | IPV6 COMMA list
         | INTEGER COMMA list
         | FLOAT COMMA list
         | VARIABLE COMMA list
         | CONSTANT COMMA list

.. note::

    Implementation of this module is very *PLY* specific, please read the
    appropriate `documentation <http://www.dabeaz.com/ply/ply.html#ply_nn3>`__
    to understand it.

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>"


import logging
import ply.yacc

from pynspect.lexer import MentatFilterLexer
from pynspect.rules import IPV4Rule, IPV6Rule, IntegerRule, FloatRule, VariableRule, ConstantRule,\
    LogicalBinOpRule, UnaryOperationRule, ComparisonBinOpRule, MathBinOpRule, ListRule


class MentatFilterParser():
    """
    Object encapsulation of *PLY* parser implementation for filtering and
    query language grammar used in Mentat project.
    """

    def build(self):
        """
        Build/rebuild the parser object
        """
        self.logger = logging.getLogger('ply_parser')

        self.lexer = MentatFilterLexer()
        self.lexer.build()

        self.tokens = self.lexer.tokens

        self.parser = ply.yacc.yacc(
            module=self,
            debuglog=self.logger,
            errorlog=self.logger
            #start='statements',
            #debug=yacc_debug,
            #optimize=yacc_optimize,
            #tabmodule=yacctab
        )

    def parse(self, data, filename='', debuglevel=0):
        """
        Parse given data.

            data:
                A string containing the filter definition
            filename:
                Name of the file being parsed (for meaningful
                error messages)
            debuglevel:
                Debug level to yacc
        """
        self.lexer.filename = filename
        self.lexer.reset_lineno()
        if not data or data.isspace():
            return []
        return self.parser.parse(data, lexer=self.lexer, debug=debuglevel)


    #---------------------------------------------------------------------------


    def _create_factor_rule(self, tok):
        """
        Simple helper method for creating factor node objects based on node name.
        """
        if tok[0] == 'IPV4':
            return IPV4Rule(tok[1])
        if tok[0] == 'IPV6':
            return IPV6Rule(tok[1])
        if tok[0] == 'INTEGER':
            return IntegerRule(tok[1])
        if tok[0] == 'FLOAT':
            return FloatRule(tok[1])
        if tok[0] == 'VARIABLE':
            return VariableRule(tok[1])
        return ConstantRule(tok[1])

    def p_expression(self, tok):
        """expression : xor_expression OP_OR expression
                      | xor_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    def p_xor_expression(self, tok):
        """xor_expression : and_expression OP_XOR xor_expression
                          | and_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    def p_and_expression(self, tok):
        """and_expression : or_p_expression OP_AND and_expression
                          | or_p_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    def p_or_p_expression(self, tok):
        """or_p_expression : xor_p_expression OP_OR_P or_p_expression
                      | xor_p_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    def p_xor_p_expression(self, tok):
        """xor_p_expression : and_p_expression OP_XOR_P xor_p_expression
                          | and_p_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    def p_and_p_expression(self, tok):
        """and_p_expression : not_expression OP_AND_P and_p_expression
                          | not_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    def p_not_expression(self, tok):
        """not_expression : OP_NOT ex_expression
                          | ex_expression"""
        if len(tok) == 3:
            tok[0] = UnaryOperationRule(tok[1], tok[2])
        else:
            tok[0] = tok[1]

    def p_ex_expression(self, tok):
        """ex_expression : OP_EXISTS cmp_expression
                         | cmp_expression"""
        if len(tok) == 3:
            tok[0] = UnaryOperationRule(tok[1], tok[2])
        else:
            tok[0] = tok[1]

    def p_cmp_expression(self, tok):
        """cmp_expression : term OP_LIKE cmp_expression
                          | term OP_IN cmp_expression
                          | term OP_IS cmp_expression
                          | term OP_EQ cmp_expression
                          | term OP_NE cmp_expression
                          | term OP_GT cmp_expression
                          | term OP_GE cmp_expression
                          | term OP_LT cmp_expression
                          | term OP_LE cmp_expression
                          | term"""
        if len(tok) == 4:
            tok[0] = ComparisonBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    def p_term(self, tok):
        """term : factor OP_PLUS term
                | factor OP_MINUS term
                | factor OP_TIMES term
                | factor OP_DIVIDE term
                | factor OP_MODULO term
                | factor"""
        if len(tok) == 4:
            tok[0] = MathBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    def p_factor(self, tok):
        """factor : IPV4
                  | IPV6
                  | INTEGER
                  | FLOAT
                  | VARIABLE
                  | CONSTANT
                  | LBRACK list RBRACK
                  | LPAREN expression RPAREN"""
        if len(tok) == 2:
            tok[0] = self._create_factor_rule(tok[1])
        else:
            tok[0] = tok[2]

    def p_list(self, tok):
        """list : IPV4
                | IPV6
                | INTEGER
                | FLOAT
                | VARIABLE
                | CONSTANT
                | IPV4 COMMA list
                | IPV6 COMMA list
                | INTEGER COMMA list
                | FLOAT COMMA list
                | VARIABLE COMMA list
                | CONSTANT COMMA list"""
        node = self._create_factor_rule(tok[1])
        if len(tok) == 2:
            tok[0] = ListRule(node)
        else:
            tok[0] = ListRule(node, tok[3])

    def p_error(self, tok):
        print("Syntax error at '%s'" % tok.value)


#
# Perform the demonstration.
#
if __name__ == "__main__":

    import pprint

    TEST_DATA = "1 and 1 or 1 xor 1"

    # Build the parser and try it out
    DEMO_PARSER = MentatFilterParser()
    DEMO_PARSER.build()

    print("Parsing: {}".format(TEST_DATA))
    pprint.pprint(DEMO_PARSER.parse(TEST_DATA))
