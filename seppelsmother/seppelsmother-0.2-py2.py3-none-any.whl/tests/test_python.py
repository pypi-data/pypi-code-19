import os
from ast import parse

import pytest

from seppelsmother.python import PythonFile
from seppelsmother.python import Visitor


case_func = """
def a():
    pass
"""
ctx_func = ['', 'a(F)', 'a(F)']

case_class = """
class A:

    def method(self):
        pass

    x = 3
"""
ctx_class = ['', 'A(C)', 'A(C)', 'A(C).method(F)', 'A(C).method(F)', 'A(C)', 'A(C)']

case_decorated_function = """
x = 5

@dec
def a():
    pass
"""
ctx_decorated_function = ['', '', '', 'a(F)', 'a(F)', 'a(F)']

case_double_decorated_function = """
x = 5

@dec1
@dec2
def a():
    pass
"""
ctx_double_decorated_function = ['', '', '', 'a(F)', 'a(F)', 'a(F)', 'a(F)']

case_inner_func = """

def a():
    def b():
        pass
    x = None
"""
ctx_inner_func = ['', '', 'a(F)', 'a(F).b(F)', 'a(F).b(F)', 'a(F)']

case_decorated_method = """
class Foo:
    @dec
    def bar(self):
        pass
"""
ctx_decorated_method = ['', 'Foo(C)', 'Foo(C).bar(F)', 'Foo(C).bar(F)', 'Foo(C).bar(F)']

VISITOR_CASES = [
    (case_func, ctx_func),
    (case_class, ctx_class),
    (case_decorated_function, ctx_decorated_function),
    (case_double_decorated_function, ctx_double_decorated_function),
    (case_inner_func, ctx_inner_func),
    (case_decorated_method, ctx_decorated_method),
]
IDS = ['func', 'class', 'decorated_func',
       'dbl_dec', 'inner_func', 'decorated_method']


@pytest.mark.parametrize('code,expected', VISITOR_CASES, ids=IDS)
def test_visitor(code, expected):
    ast = parse(code)
    visitor = Visitor(prefix='')
    visitor.visit(ast)
    assert visitor.lines == expected


CONTEXT_CASES = [
    (case_func, 'a(F)', (2, 4)),
    (case_class, 'A(C)', (2, 8)),
    (case_class, 'A(C).method(F)', (4, 6)),
    (case_decorated_method, 'Foo(C)', (2, 6)),
]
CONTEXT_IDS = ['func', 'class', 'class_inner', 'decorated_method']


@pytest.mark.parametrize(
    "code,context,expected", CONTEXT_CASES, ids=CONTEXT_IDS)
def test_context_range(code, context, expected):

    pf = PythonFile('test.py', prefix='', source=code)
    assert pf.context_range(context) == expected


def test_default_prefix():

    assert PythonFile('test.py', source='').prefix == 'test'
    assert PythonFile('a/b/c.py', source='').prefix == 'a.b.c'
    assert PythonFile('a/b/c.pyc', source='').prefix == 'a.b.c'
    assert PythonFile('a/b/c.pyo', source='').prefix == 'a.b.c'
    assert PythonFile('a/b/c.pyw', source='').prefix == 'a.b.c'
    assert PythonFile('a/b/c/__init__.py', source='').prefix == 'a.b.c'


def test_prefix_for_absolute_paths():
    path = os.path.abspath('seppelsmother/tests/demo.py')
    assert PythonFile(path).prefix == 'seppelsmother.tests.demo'
