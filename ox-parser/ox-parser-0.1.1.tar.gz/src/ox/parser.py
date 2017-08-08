from collections import Counter

from sidekick import record, fn


def ply_parser(rules, tokens, start=None):
    """
    Return a parser from a list of (rule, reducer) tuples:

    Args:
        rules:
            A list of (handler, *rules). Each rule must be a single line string 
            with a grammar rule that PLY understands. The handler function is
            called with the inputs on the rhs of the rule as arguments. This 
            function must return a node in the parse tree.
        tokens:
            A list of valid token types.
        start:
            The start/root expression type. It will reduce the AST to the given
            start expression value.
    """

    from ply import yacc

    # We use a similar strategy as in the ply_lexer function, but this time
    # the process is more involving. Let us start with a very basic namespace
    # that does not define any p_<rule>_<id> functions yet.
    namespace = dict(
        tokens=tokens,
        p_error=ply_parser_error,
    )

    # Now we create rules from the input list
    counter = Counter()
    for rule, handler in rules:
        name = rule.partition(':')[0].strip()
        if start is None:
            start = name
        
        rule_id = counter[name] = counter[name] + 1
        rule_name = 'p_%s_%s' % (name, rule_id)
        namespace[rule_name] = make_rule_handler(rule, handler)

    # We build a module-like object from namespace dictionary
    module = record(**namespace)
    yacc_parser = yacc.yacc(module=module, start=start)

    def parser(tokens: list):
        if isinstance(tokens, str):
            raise ValueError('parser receives a list of tokens, not a string!')
        tk_list = list(reversed(tokens))

        def next_token():
            if tk_list:
                return tk_list.pop()

        return yacc_parser.parse(lexer=record(token=next_token))

    return parser


def make_parser(rules, tokens, start=None):
    """
    Alias to ply_parser.
    """
    return fn(ply_parser(rules, tokens, start=start))


# Utility functions
def ply_parser_error(p):
    raise SyntaxError('unexpected token: %r' % p)


def make_rule_handler(rule, handler):
    """
    Convert a handler function func(*args) -> AST into a rule that uses the PLY 
    interface such as::

        def p_rule_name(p):
            "<rule>"

            p[0] = func(*p[1:])
    """

    if handler is None:
        handler = lambda x: x

    def rule_handler(p):
        _, *args = p
        p[0] = handler(*args)

    rule_handler.__doc__ = rule
    return rule_handler


def main(lexer, parser, *args):
    """
    Keep asking a new expression and prints the resulting parse tree.
    """
    from pprint import pprint
    
    while True:
        expr = input('expr: ')
        if expr:
            try:
                tokens = lexer(expr)
                print('tokens:', tokens)
                
                ast = parser(tokens)
                print('ast:', ast)
            except Exception as ex:
                print('error:', ex, '\n')
                continue
            
            if args:
                value = ast
                for func in args:
                    value = func(value)
                print('final:', value)
            print() 
        else:
            break
