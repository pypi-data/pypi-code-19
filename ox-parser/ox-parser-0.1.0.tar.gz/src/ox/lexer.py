import re
from functools import wraps

from sidekick import Record, field, record, fn

# Helps mocking/patching during tests
_import = __import__
_input = input
_print = print


def make_lexer(rules, which='auto'):
    """
    A lexer factory.  
    
    This function expects to receive a list of (tok_type, regex) strings and 
    returns a function that tokenizes a input string into a sequence of tokens.

    Args:
        rules:
            A list of rules.
        which ('auto', 'ply' or 'simple'):
            lexer factory type.
    """

    if which == 'auto':
        # The default is the ply lexer, unless PLY is not installed.
        try: 
            _import('ply')
            which = 'ply'
        except:
            which = 'simple'
    
    if which == 'ply':
        lexer = ply_lexer(rules)
    elif which == 'simple':
        lexer = simple_lexer(rules)
    else:
        raise ValueError('invalid lexer: %r' % which)

    return fn(wraps(lexer)(lambda expr: list(lexer(expr))))


def tokenize(rules, expr, which='auto'):
    """
    Tokenize expression using the given rules.

    If you want to run the lexer more than once, it is probably better to
    call the make_lexer() function prior passing the input expression.

    Args:
        rules:
            A list of rules (see :func:`make_lexer`)
        expr (str):
            The input string.
        which:
            Select the lexer strategy.
    """

    return make_lexer(rules, which=which)(expr)


def simple_lexer(rules):
    """
    A very simple lexer factory based on a recipe on Python's regex module.
    """
    
    # This is a simplified version of the techique described at
    # https://docs.python.org/3/library/re.html#writing-a-lexer
    
    regex = '|'.join(r'(?P<%s>%s)' % item for item in rules)
    regex += r'|(?P<whitespace>\s+)|(?P<error>.+)'
    regex = re.compile(regex)
    
    def lexer(expr):
        for match in re.finditer(regex, expr):
            typ = match.lastgroup
            value = match.group(typ)
            
            if typ == 'whitespace':
                continue
            elif typ == 'error':
                raise SyntaxError('invalid value: %r' % value)
            
            yield Token(typ, value)
    
    lexer.which = 'simple'
    return lexer


def ply_lexer(rules):
    """
    A lexer factory that uses PLY own lexer module to build tokens.

    It has the same interface as the simple_lexer() function.
    """

    from ply import lex
    
    # PLY documentation asks us to define a series of constants or functions
    # named as t_TOK_NAME in a module. This is not necessary and any 
    # introspectable Python object that exposes those constants via getattr
    # is good enough. We use a record() object here and let PLY instrospect it
    # by pretending it is a module :)  
    namespace = record(
        tokens=[x for x, _ in rules],
        t_ignore=' \t',
        t_error=ply_lexer_error,
        **{'t_' + x: y for (x, y) in rules}
    )
    ply_lexer = lex.lex(module=namespace)
    
    def lexer(expr):
        ply_lexer.input(expr)
        
        while True:
            tok = ply_lexer.token()
            if tok is None:
                break
            yield Token(tok.type, tok.value, tok.lineno, tok.lexpos, lexer)

    lexer.which = 'ply'
    return lexer


# Utility functions and types
def ply_lexer_error(lex):
    raise SyntaxError("Illegal character '%s'" % lex.value[0])


def main(lexer):
    """
    Keep asking a new expression and return the token stream.
    """
    
    while True:
        expr = _input('expr: ')
        if expr:
            _print(list(lexer(expr)))
        else:
            break


class Token(Record):
    """
    Represents a token.

    Used internally by all lexers.
    """

    type = field()
    value = field()
    lineno = field(default=None)
    lexpos = field(default=None)
    lexer = field(default=None)

    def __repr__(self):
        return '%s(%s)' % (self.type, self.value)

    def __eq__(self, other):
        if type(other) is Token:
            return self.type == other.type and self.value == other.value
        return NotImplemented