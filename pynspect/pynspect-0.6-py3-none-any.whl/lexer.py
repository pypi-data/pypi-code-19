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


r"""
This module contains object encapsulation of `PLY <http://www.dabeaz.com/ply/>`__
lexical analyzer for filtering and query language grammar used in Mentat
project.

Currently recognized tokens
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Mathematical operation tokens
    OP_PLUS   = r'\+'
    OP_MINUS  = r'-'
    OP_TIMES  = r'\*'
    OP_DIVIDE = r'/'
    OP_MODULO = r'%'

    # Logical operation tokens
    OP_OR     = r'(or|OR)'
    OP_XOR    = r'(xor|XOR)'
    OP_AND    = r'(and|AND)'
    OP_NOT    = r'(not|NOT)'
    OP_EXISTS = r'(exists|EXISTS|\?)'

    # Priority logical operation tokens
    OP_OR_P  = r'\|\|'
    OP_XOR_P = r'\^\^'
    OP_AND_P = r'&&'

    # Comparison operation tokens
    OP_LIKE = r'(like|LIKE|=~)'
    OP_IN   = r'(in|IN|~~)'
    OP_IS   = r'(is|IS)'
    OP_EQ   = r'(eq|EQ|==)'
    OP_NE   = r'(ne|NE|!=|<>)'
    OP_GT   = r'(gt|GT|>)'
    OP_GE   = r'(ge|GE|>=)'
    OP_LT   = r'(lt|LT|<)'
    OP_LE   = r'(le|LE|<=)'

    # Special tokens
    COMMA  = r'\s*,\s*|\s*;\s*'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACK = r'\['
    RBRACK = r'\]'

    # Contant and variable tokens
    IPV4     = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:\/\d{1,2}|(?:-|..)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})?'
    IPV6     = r'[:a-fA-F0-9]+:[:a-fA-F0-9]*(?:\/\d{1,3}|(?:-|..)[:a-fA-F0-9]+:[:a-fA-F0-9]*)?'
    INTEGER  = r'\d+'
    FLOAT    = r'\d+\.\d+'
    CONSTANT = r'"([^"]+)"|\'([^\']+)\''
    VARIABLE = r'[_a-zA-Z][-_a-zA-Z0-9]*(?:\[(?:\d+|-\d+|\#)\])?(?:\.?[a-zA-Z][-_a-zA-Z0-9]*(?:\[(?:\d+|-\d+|\#)\])?)*'

.. note::

    Implementation of this module is very *PLY* specific, please read the
    appropriate `documentation <http://www.dabeaz.com/ply/ply.html#ply_nn3>`__
    to understand it.

.. todo::

    Consider following options:

    * Support for negative integers and floats
    * Recognize RFC timestamps as constant without quotes for better
      time value input
    * Support for functions (count, max, min, first, last, time, etc.)

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>"


import re
import ply.lex as lex


class MentatFilterLexer():
    """
    Object encapsulation of *PLY* lexical analyzer implementation for
    filtering and query language grammar.
    """

    # List of all reserved words.
    reserved = {
        'or':     'OP_OR',
        'xor':    'OP_XOR',
        'and':    'OP_AND',
        'not':    'OP_NOT',
        'exists': 'OP_EXISTS',

        'like': 'OP_LIKE',
        'in':   'OP_IN',
        'is':   'OP_IS',
        'eq':   'OP_EQ',
        'ne':   'OP_NE',
        'gt':   'OP_GT',
        'ge':   'OP_GE',
        'lt':   'OP_LT',
        'le':   'OP_LE',

        'OR':     'OP_OR',
        'XOR':    'OP_XOR',
        'AND':    'OP_AND',
        'NOT':    'OP_NOT',
        'EXISTS': 'OP_EXISTS',

        'LIKE': 'OP_LIKE',
        'IN':   'OP_IN',
        'IS':   'OP_IS',
        'EQ':   'OP_EQ',
        'NE':   'OP_NE',
        'GT':   'OP_GT',
        'GE':   'OP_GE',
        'LT':   'OP_LT',
        'LE':   'OP_LE',

        '||': 'OP_OR_P',
        '^^': 'OP_XOR_P',
        '&&': 'OP_AND_P',
        '!':  'OP_NOT',
        '?':  'OP_EXISTS',

        '=~': 'OP_LIKE',
        '~~': 'OP_IN',
        '==': 'OP_EQ',
        '!=': 'OP_NE',
        '<>': 'OP_NE',
        '>':  'OP_GT',
        '>=': 'OP_GE',
        '<':  'OP_LT',
        '<=': 'OP_LE',

        '+': 'OP_PLUS',
        '-': 'OP_MINUS',
        '*': 'OP_TIMES',
        '/': 'OP_DIVIDE',
        '%': 'OP_MODULO'
    }

    # List of grammar token names.
    tokens = [
        'EXP_ALL',

        'OP_PLUS',
        'OP_MINUS',
        'OP_TIMES',
        'OP_DIVIDE',
        'OP_MODULO',

        'OP_OR',
        'OP_XOR',
        'OP_AND',
        'OP_NOT',
        'OP_EXISTS',

        'OP_OR_P',
        'OP_XOR_P',
        'OP_AND_P',

        'OP_LIKE',
        'OP_IN',
        'OP_IS',
        'OP_EQ',
        'OP_NE',
        'OP_GT',
        'OP_GE',
        'OP_LT',
        'OP_LE',

        'COMMA',
        'LPAREN',
        'RPAREN',
        'LBRACK',
        'RBRACK',

        'IPV4',
        'IPV6',
        'INTEGER',
        'FLOAT',
        'CONSTANT',
        'VARIABLE'
    ]

    # Regular expressions for simple tokens
    t_COMMA  = r'\s*,\s*|\s*;\s*'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACK = r'\['
    t_RBRACK = r'\]'

    # Regular expression for ignored tokens
    t_ignore = ' \t'


    def build(self, **kwargs):
        """
        Build/rebuild the lexer object.

        (Re)Initialize internal `PLY <http://www.dabeaz.com/ply/>`__ lexer object.
        """
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data, separator = ''):
        """
        Test the lexer on given input string.
        """
        self.lexer.input(data)
        result = ''
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            result = '{}{}{}'.format(result, tok, separator)
        return result


    #---------------------------------------------------------------------------


    # According to the documentation, section 4.3 Specification of tokens
    # (http://www.dabeaz.com/ply/ply.html#ply_nn6), best practice is to
    # reduce the number of required regular expressions. So following
    # is the ugly as hell uber regular expression for unary and binary
    # operators.
    def t_EXP_ALL(self, tok):
        r'(-|\+|\*|/|%|like|LIKE|=~|in|IN|~~|is|IS|eq|EQ|==|ne|NE|!=|<>|ge|GE|>=|gt|GT|>|le|LE|<=|lt|LT|<|or|OR|\|\||xor|XOR|\^\^|and|AND|&&|not|NOT|!|exists|EXISTS|\?)'
        tok.type = self.reserved.get(tok.value)
        tok.value = tok.type
        return tok

    def t_IPV4(self, tok):
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:\/\d{1,2}|(?:-|..)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})?'
        tok.value = (tok.type, tok.value)
        return tok

    def t_IPV6(self, tok):
        r'[:a-fA-F0-9]+:[:a-fA-F0-9]*(?:\/\d{1,3}|(?:-|..)[:a-fA-F0-9]+:[:a-fA-F0-9]*)?'
        tok.value = (tok.type, tok.value)
        return tok

    def t_FLOAT(self, tok):
        r'\d+\.\d+'
        tok.value = (tok.type, float(tok.value))
        return tok

    def t_INTEGER(self, tok):
        r'\d+'
        tok.value = (tok.type, int(tok.value))
        return tok

    def t_VARIABLE(self, tok):
        r'[_a-zA-Z][-_a-zA-Z0-9]*(?:\[(?:\d+|-\d+|\#)\])?(?:\.?[a-zA-Z][-_a-zA-Z0-9]*(?:\[(?:\d+|-\d+|\#)\])?)*'
        tok.value = (tok.type, tok.value)
        return tok

    def t_CONSTANT(self, tok):
        r'"([^"]+)"|\'([^\']+)\''
        tok.value = (tok.type, re.sub('["\']', '', tok.value))
        return tok

    def t_newline(self, tok):
        r'\n+'
        tok.lexer.lineno += len(tok.value)

    def t_error(self, tok):
        print("Illegal character '%s'" % tok.value[0])
        tok.lexer.skip(1)

    def reset_lineno(self):
        """
        Reset internal line counter.
        """
        self.lexer.lineno = 1

    def input(self, text):
        """
        Proxy method for underlying Lexer object interface.
        """
        self.lexer.input(text)

    def token(self):
        """
        Proxy method for underlying Lexer object interface.
        """
        return self.lexer.token()


#
# Perform the demonstration by parsing text containing all possible tokens.
#
if __name__ == "__main__":

    TEST_DATA = """
        1 + 1 - 1 * 1 % 1
        OR 2 or 2 || 2
        XOR 3 xor 3 ^^ 3
        AND 4 and 4 && 4
        NOT 5 not 5 ! 5
        EXISTS 6 exists 4 ? 6
        LIKE 7 like 7 =~ 7
        IN 8 in 8 ~~ 8
        IS 9 is 9
        EQ 10 eq 10 == 10
        NE 11 ne 11 <> 11 != 11
        GT 12 gt 12 > 12
        GE 13 ge 13 >= 13
        LT 14 lt 14 < 14
        LE 15 le 15 <= 15
        (127.0.0.1 eq ::1 eq 2001:afdc::58 eq Source.Node eq "Value 525.89:X><" eq 'Value 525.89:X><')
        [1, 2, 3 , 4]
    """

    # Build the lexer and try it out
    DEMO_LEXER = MentatFilterLexer()
    DEMO_LEXER.build()
    print(DEMO_LEXER.test(TEST_DATA, "\n"))
