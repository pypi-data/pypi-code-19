# lextab.py. This file automatically created by PLY (version 3.9). Don't edit!
_tabversion   = '3.8'
_lextokens    = set(('SUBSET', 'SQ_LPARENT', 'TRUE', 'LPARENT', 'SQ_RPARENT', 'NE', 'LT', 'NUM', 'COMMA', 'RPARENT', 'GT', 'STRING', 'EQU', 'GE', 'LE', 'IN', 'VAR', 'EQ', 'AND', 'FALSE', 'NOT', 'OR'))
_lexreflags   = 0
_lexliterals  = '+-/*!;'
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_STRING>"[^"]*")|(?P<t_NUM>(\\d+(\\.\\d*)?|\\.\\d+)([eE][+-]?\\d+)?(kb|gb|mb|tb|pb|Kb|Gb|Mb|Tb|Pb)?)|(?P<t_VAR>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<t_LE>\\<\\=)|(?P<t_AND>\\&\\&)|(?P<t_OR>\\|\\|)|(?P<t_GE>\\>\\=)|(?P<t_EQ>\\=\\=)|(?P<t_NE>\\!\\=)|(?P<t_LT>\\<)|(?P<t_COMMA>\\,)|(?P<t_RPARENT>\\))|(?P<t_SQ_LPARENT>\\[)|(?P<t_EQU>\\=)|(?P<t_SQ_RPARENT>\\])|(?P<t_GT>\\>)|(?P<t_LPARENT>\\()', [None, ('t_STRING', 'STRING'), ('t_NUM', 'NUM'), None, None, None, None, ('t_VAR', 'VAR'), (None, 'LE'), (None, 'AND'), (None, 'OR'), (None, 'GE'), (None, 'EQ'), (None, 'NE'), (None, 'LT'), (None, 'COMMA'), (None, 'RPARENT'), (None, 'SQ_LPARENT'), (None, 'EQU'), (None, 'SQ_RPARENT'), (None, 'GT'), (None, 'LPARENT')])]}
_lexstateignore = {'INITIAL': ' \t\n'}
_lexstateerrorf = {'INITIAL': 't_error'}
_lexstateeoff = {}
