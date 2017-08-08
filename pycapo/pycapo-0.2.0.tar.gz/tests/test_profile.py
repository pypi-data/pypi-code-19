# -*- coding: utf-8 -*-

import pytest

from pycapo import CapoConfig


# Tests for specifying the profile when you instantiate a CapoConfig.

def test_missing_profile_argument(monkeypatch):
    """
    If you create a CapoConfig and don't pass it a profile or have the
    CAPO_PROFILE environment variable set it shoudl throw a ValueError.
    """
    monkeypatch.delenv('CAPO_PROFILE', raising=False)
    with pytest.raises(ValueError):
        CapoConfig()


def test_profile_precedence(monkeypatch):
    """
    If CapoConfig is made with profile as both parameter and environment
    variable, the parameter should take precedence.
    """
    monkeypatch.setenv('CAPO_PROFILE', 'bogus')
    config = CapoConfig(profile='dude')
    assert config.profile == 'dude'
