import pytest

from latest.config import config as Config
from latest.exceptions import *
from latest.core import *


@pytest.fixture(scope='module')
def context():
    return {
        'scalar': 0,
        'list': [0, 1],
        'dict': {'x': 0, 'y': 1},
        'dict_of_dicts': {'x': {'i': 0, 'j': 1}, 'y': {'i': 1, 'j': 0}},
        'list_of_dicts': [{'x': 0, 'y': 1}, {'x': 1, 'y': 0}],
    }


@pytest.fixture(params=[
    ('ns={namespace}, join={,}', {'ns': 'namespace', 'join': ','}),
])
def parse_options_data(request):
    return request.param


def test_parse_options(parse_options_data):
    (options_string, options) = parse_options_data
    assert parse_options(options_string) == options


@pytest.fixture(params=[
    ('2*2', '4'),
    ('scalar*2', str(context()['scalar']*2)),
    ('list[0]+list[1]', str(context()['list'][0]+context()['list'][1])),
    ('dict["x"]', str(context()['dict']['x'])),
    ('dict_of_dicts["x"]["i"]', str(context()['dict_of_dicts']['x']['i'])),
    ('scalar*', CodeError),
    ('x', ContextError),
])
def code_data(request):
    return request.param


def test_eval_code(context, code_data):
    (code, result) = code_data
    try:
        assert eval_code(code, context) == result
    except Exception as e:
        assert e.__class__ == result


@pytest.fixture(params=[
    ('', [context()]),
    (None, [context()]),
    ('scalar', [{'_value': 0}]),
    ('list', [{'_index': 0, '_value': 0}, {'_index': 1, '_value': 1}]),
])
def ns_data(request):
    return request.param


def test_eval_ns(context, ns_data):
    (path, ctxs) = ns_data
    assert eval_ns(path, context) == ctxs


@pytest.fixture(params=[
    (' 2*2 ', None, '4'),
    (' scalar ', '', str(context()['scalar'])),
    (' str(_index) + str(_value) ', 'list', Config.join_items.join(str(i) + str(item) for i, item in enumerate(context()['list']))),
    (' x + y ', 'dict', str(context()['dict']['x'] + context()['dict']['y'])),
    (' i ', 'dict_of_dicts' + Config.ns_operator + 'y', str(context()['dict_of_dicts']['y']['i'])),
])
def cmd_data(request):
    return request.param


def test_eval_cmd(context, cmd_data):
    (code, namespace, result) = cmd_data
    assert eval_cmd(code, context, ns=namespace) == result


@pytest.fixture(params=[
    (r'\latest{$ scalar $}', str(context()['scalar'])),
    (r'normal text, \latest{$ "code" $}, normal text and \latest[ns={dict}]{$ y $} code again...', 'normal text, code, normal text and 1 code again...'),
])
def expr_data(request):
    return request.param


def test_eval_expr(context, expr_data):
    (expr, result) = expr_data
    assert eval_expr(expr, context) == result


@pytest.fixture(params=[
    (r'latest \latest{$ "is" $} a nice \latest{$ "a"+"p"*2 $}!', None, r'latest is a nice app!'),
    (r'x + y = \latest{$ x + y $}', 'dict', r'x + y = ' + str(context()['dict']['x'] + context()['dict']['y'])),
    (r'x = \latest{$ x $}', 'list_of_dicts', Config.join_items.join('x = ' + str(ctx['x']) for ctx in context()['list_of_dicts'])),
])
def env_data(request):
    return request.param


def test_eval_env(context, env_data):
    (env, namespace, result) = env_data
    assert eval_env(env, namespace, context) == result


@pytest.fixture(params=[
    (r'\begin{latest}{dict_of_dicts.x}i = \latest{$ i $}\end{latest}', 'i = 0'),
    (r'\latest{$scalar$},\begin{latest}{dict}\latest{$x$}\end{latest}', str(context()['scalar']) + ',' + str(context()['dict']['x'])),
])
def latest_data(request):
    return request.param


def test_eval_latest(context, latest_data):
    (code, result) = latest_data
    assert eval_latest(code, context) == result


