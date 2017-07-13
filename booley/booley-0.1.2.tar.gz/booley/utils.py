# -*- coding: utf-8 -*-


def flatten(L):
    ret = []
    for i in L:
        if isinstance(i, list):
            ret.extend(flatten(i))
        else:
            ret.append(i)
    return ret


def parse_booley_expression(expression, context):
    from .parsers import Booley
    parser = Booley()
    return parser.parse(expression, context)
