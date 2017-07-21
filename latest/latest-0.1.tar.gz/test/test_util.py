import os

try:
    import configparser
except:
    import ConfigParser as configparser

import pytest

from latest.util import *
from latest.config import create_config


@pytest.fixture(params=[
    (bool(), True, False, False),
    (int(), True, False, False),
    (float(), True, False, False),
    (complex(), True, False, False),
    (str(), True, False, False),
    (list(), False, True, False),
    (tuple(), False, True, False),
    (set(), False, True, False),
    (frozenset(), False, True, False),
    (dict(), False, False, True),
    (object(), False, False, True),
])
def typecheck_data(request):
    return request.param


def test_typecheck(typecheck_data):
    (obj, isscalar, isvector, istensor) = typecheck_data
    assert is_scalar(obj) == isscalar
    assert is_vector(obj) == isvector
    assert is_tensor(obj) == istensor


@pytest.fixture(params=[
    ('.', os.getcwd()),
    ('~', os.path.expanduser('~')),
])
def path_data(request):
    return request.param


def test_path(path_data):
    (loc, result) = path_data
    assert path(loc) == result


@pytest.fixture
def data():
    return {
        'a': 0,
        'b': [0, 1],
        'c': {'x': 0, 'y': 1},
    }


@pytest.fixture(params=[
    (data(), str(), '/', data()),
    (data(), 'a', '/', 0),
    (data(), 'b', '::', [0, 1]),
    (data(), 'c', '\\', {'x': 0, 'y': 1}),
    (data(), 'c\\x', '\\', 0),
    (data(), 'c::y', '::', 1),
    (data(), 'c::z', '::', None),
    (data(), 'd', '::', None),
])
def select_data(request):
    return request.param


def test_select(select_data):
    (data, path, sep, result) = select_data
    try:
        assert select(data, path, sep=sep) == result
    except KeyError:
        assert not result


@pytest.fixture
def parser(config_file):
    parser = configparser.RawConfigParser()
    parser.read(config_file)
    return parser


@pytest.fixture(params=[
    ('section', 'key', 'def', 'value'),
    ('section', 'false_key', 'def', 'def'),
    ('false_section', 'key', 'def', 'def'),
])
def getopt_data(request):
    return request.param


def test_getopt(parser, getopt_data):
    (section, key, default, result) = getopt_data
    assert getopt(parser, section, key, default=default) == result


def test_guess_data_fmt(config, data_file):
    (filename, fmt) = data_file
    assert guess_data_fmt(filename, config.default_data_fmt) == fmt



