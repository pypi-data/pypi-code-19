from lex import tokens, lexer
import ply.yacc as yacc
from ast import *

def p_fields(p):
    '''fields       : expr
                    | fields field_split expr'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_field_split(p):
    '''field_split  : COMMA
                    | WHITE COMMA
                    | COMMA WHITE
                    | WHITE COMMA WHITE'''

def p_const(p):
    '''const        : INT
                    | FLOAT
                    | STR'''
    p[0] = ValueExpr(p[1])

def p_field_picker(p):
    '''field_picker : DOT KEYWORD
                    | LBRACKET INT RBRACKET
                    | LBRACKET STR RBRACKET'''
    p[0] = FieldPicker(p[2])

def p_field_getter(p):
    '''field_getter : field_picker
                    | field_getter field_picker'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[1])

def p_cmp_op(p):
    '''cmp_op       : EQ
                    | NE
                    | LT
                    | GT
                    | LE
                    | GE
                    | IN'''
    p[0] = p[1]

def p_cmp_op_not_in(p):
    '''cmp_op       : NOT IN'''
    p[0] = 'not in'

def p_expr(p):
    '''expr         : const
                    | field_getter'''
    p[0] = p[1] if isinstance(p[1], ValueExpr) else ValueExpr(p[1])

def p_cmp(p):
    '''cmp          : expr cmp_op expr'''
    p[0] = Compare(p[1], p[3], p[2].strip())

def p_cmp_paren(p):
    '''cmp          : LPAREN cond_expr RPAREN'''
    p[0] = p[2]

def p_cmp_not(p):
    '''cmp          : NOT cmp'''
    p[0] = CondExpr()
    p[0].terms.append(p[2])
    p[0].not_expr = True

def p_cond_term_single(p):
    '''cond_term    : cmp'''
    p[0] = CondTerm()
    p[0].exprs.append(p[1])

def p_cond_term_and(p):
    '''cond_term    : cond_term AND cmp'''
    p[0] = p[1]
    p[1].exprs.append(p[3])

def p_cond_expr_single(p):
    '''cond_expr    : cond_term'''
    p[0] = CondExpr()
    p[0].terms.append(p[1])

def p_cond_expr_or(p):
    '''cond_expr    : cond_expr OR cond_term'''
    p[0] = p[1]
    p[0].terms.append(p[3])

def p_query_all(p):
    '''query        : SELECT fields'''
    p[0] = Query(p[2], CondExpr())

def p_query_where(p):
    '''query        : SELECT fields WHERE cond_expr'''
    p[0] = Query(p[2], p[4])

parser = yacc.yacc(start='query')


def parse(qstr):
    lexer.input(qstr)
    while False:
        token = lexer.token()
        if not token:
            break
        print token
    return parser.parse(qstr)

if __name__ == '__main__':
    import sys
    query = sys.stdin.read().strip()
    lexer.input(query)
    while True:
        token = lexer.token()
        if not token:
            break
        print token
    result = parser.parse(query)
    print result
