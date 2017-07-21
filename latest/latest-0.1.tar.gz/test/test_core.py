import pytest

from latest.exceptions import *
from latest.core import *


@pytest.fixture(scope='module')
def context():
    return {
        'scalar': 0,
        'list': [0, 1],
        'dict': {'x': 0, 'y': 1},
        'dict_of_dicts': {'x': {'i': 0, 'j': 1}, 'y': {'i': 1, 'j': 0}},
    }


_ctx = context()


@pytest.fixture(params=[
    ('2*2', '4'),
    ('scalar*2', str(_ctx['scalar']*2)),
    ('list[0]+list[1]', str(_ctx['list'][0]+_ctx['list'][1])),
    ('dict["x"]', str(_ctx['dict']['x'])),
    ('dict_of_dicts["x"]["i"]', str(_ctx['dict_of_dicts']['x']['i'])),
    ('scalar*', CodeError),
    ('x', ContextError),
])
def code_data(request):
    return request.param


def test_eval_code(config, context, code_data):
    (code, result) = code_data
    try:
        assert eval_code(code, context, config=config) == result
    except Exception as e:
        assert e.__class__ == result


@pytest.fixture(params=[
    ('$scalar$', str(_ctx['scalar'])),
    ('normal text, $"code"$, normal text and $"code again"$...', 'normal text, code, normal text and code again...'),
])
def expr_data(request):
    return request.param


def test_eval_expr(config, context, expr_data):
    (expr, result) = expr_data
    assert eval_expr(expr, context, config=config) == result


@pytest.fixture(params=[
    (r'latest $"is"$ a nice $"a"+"p"*2$!', r'latest is a nice app!'),
    (r'dict::x + y = $x+y$', r'x + y = ' + str(_ctx['dict']['x'] + _ctx['dict']['y'])),
])
def block_data(request):
    return request.param


def test_eval_block(config, context, block_data):
    (block, result) = block_data
    assert eval_block(block, context, config=config) == result


@pytest.fixture(params=[
    ('line1: _\n<%dict_of_dicts::x::line2: i = $i$, j = $j$%>\nline3: _', 'line1: _\nline2: i = 0, j = 1\nline3: _'),
])
def template_data(request):
    return request.param


def test_eval_template(config, context, template_data):
    (template, result) = template_data
    assert eval_template(template, context, config=config) == result


