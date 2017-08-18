from io import StringIO

import pytest

from . import sources


def test_ini():
    f = StringIO("""
    [settings]
    foo: bar
    baz = qux
    """)
    s = sources.IniSource(f)
    assert s['foo'] == 'bar'
    assert s['baz'] == 'qux'


def test_env(monkeypatch):
    monkeypatch.setenv('FOO', 'bar')
    monkeypatch.setenv('BAZ', 'qux')
    s = sources.EnvironmentSource()
    assert s['FOO'] == 'bar'
    assert s['BAZ'] == 'qux'


def test_env_with_prefix(monkeypatch):
    monkeypatch.setenv('MYAPP_FOO', 'bar')
    monkeypatch.setenv('MYAPP_BAZ', 'qux')
    monkeypatch.setenv('EGGS', 'spam')
    s = sources.EnvironmentSource(prefix="MYAPP_")
    assert s['FOO'] == 'bar'
    assert s['BAZ'] == 'qux'
    with pytest.raises(KeyError):
        s['EGGS']  # noqa
