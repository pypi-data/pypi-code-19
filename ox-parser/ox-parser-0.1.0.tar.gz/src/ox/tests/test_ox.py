import pytest
import ox


def test_project_defines_author_and_version():
    assert hasattr(ox, '__author__')
    assert hasattr(ox, '__version__')
