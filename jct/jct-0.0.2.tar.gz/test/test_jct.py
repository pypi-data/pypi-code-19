import os
import json
from jct import *


# Config Tests
def test_valid_empty():
    assert Config() == {}


def test_valid_defaults():
    x = {"test": 123}
    assert Config(**x) == x


def test_bad_config():
    assert Config() == {}


def test_valid_config_path_default():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, 'configs', 'default.json')) as f:
        f = json.load(f)
        c = Config(**f)
        assert c == f
        assert c.get('foo') == 'bar'
        assert c.get('test.another') == 'another value'
        assert c.get('test.bad.bad.value') is None
        assert c.get('test.bad.bad.value', True) is True
        assert c.get('test.more.final.value') == 123
        assert c.get('test.more.final.value') == c['test']['more']['final']['value']


# Jct Tests
def test_bad_default_default():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    assert Jct(env='asf', default_file="asf.json", config_paths=[os.path.join(dir_path, 'configs')]) == {}


def test_period_gets():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = 'configs'
    c = Jct(env='default', config_paths=[os.path.join(dir_path, path)])
    assert c.get('foo') == 'bar'
    assert c.get('test.another') == 'another value'
    assert c.get('test.bad.bad.value') is None
    assert c.get('test.bad.bad.value', True) is True
    assert c.get('test.more.final.value') == 123
    assert c.get('test.more.final.value') == c['test']['more']['final']['value']


def test_merge():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = 'configs'
    c = Jct(env='test', config_paths=[os.path.join(dir_path, path)])
    assert c.get('foo') == 'bar'
    assert c.get('test.another') == 'another value'
    assert c.get('test.bad.bad.value') is None
    assert c.get('test.bad.bad.value', True) is True
    assert c.get('test.more.final.value') == 456
    assert c.get('test.more.final.value') == c['test']['more']['final']['value']
    assert c.get('test.test_only') == "test only param"
    assert c.get('boo') == "far"


def test_empty_paths():
    assert Jct(config_paths=[]) == {}


def test_unknown_env():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    c = Jct(env='unknown', config_paths=[os.path.join(dir_path, 'configs')])
    with open(os.path.join(dir_path, 'configs', 'default.json')) as f:
        f = json.load(f)
        assert c == f
