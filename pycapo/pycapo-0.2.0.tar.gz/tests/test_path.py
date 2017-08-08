# -*- coding: utf-8 -*-

from pycapo import CapoConfig, DEFAULT_CAPO_PATH


# Tests for specifying the path when you instantiate a CapoConfig.

def test_missing_path_argument(monkeypatch):
    """
    Do we get default path when we should? If a CapoConfig is created
    without being passed a path or having the CAPO_PATH environment variable
    set, it should revert to the default.
    """
    monkeypatch.delenv('CAPO_PATH', raising=False)
    config = CapoConfig(profile='test')
    assert config.getpath() == DEFAULT_CAPO_PATH


def test_path_precedence(monkeypatch):
    """
    If CapoConfig is made with path as both parameter and environment,
    the parameter should take precedence.
    """
    monkeypatch.setenv('CAPO_PATH', '/foo')
    config = CapoConfig(profile='test', path='/bar')
    assert config.getpath() == '/bar'
