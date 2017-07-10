#coding: u8

import six
import ply.lex as lex

tokens = (
    'WHITE',
    'WHERE',
    'INT',
    'FLOAT',
    'STR',
    'DOT',
    'COMMA',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'SELECT',
    'AND',
    'OR',
    'NOT',
    'IN',
    'EQ',
    'NE',
    'GT',
    'LT',
    'GE',
    'LE',
    'KEYWORD',
)

t_WHITE     = r'\s+'
t_DOT       = r'\.'
t_COMMA     = r'\,'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_EQ        = r'\s*==\s*'
t_NE        = r'\s*!=\s*'
t_GT        = r'\s*\>\s*'
t_LT        = r'\s*\<\s*'
t_GE        = r'\s*\>=\s*'
t_LE        = r'\s*\<=\s*'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    pass

def t_FLOAT(t):
    r'(\+|\-)?\d+.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'(\+|\-)?\d+'
    t.value = int(t.value)
    return t

def t_STR(t):
    r'"(\\.|[^"])*"'
    t.value = eval(t.value)
    return t

def t_SELECT(t):
    r'select\s+'
    return t

def t_WHERE(t):
    r'\s+where\s+'
    return t

def t_AND(t):
    r'\s+and\s+'
    return t

def t_OR(t):
    r'\s+or\s+'
    return t

def t_NOT(t):
    r'not\s+'
    return t

def t_IN(t):
    r'in'
    return t

def t_KEYWORD(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    return t

lexer = lex.lex()

if __name__ == '__main__':
    import sys
    data = sys.stdin.read()
    lexer.input(data)
    while True:
        token = lexer.token()
        if not token:
            break
        six.print_(token)
