from pathlib import Path

import pytest

from workaround.handle import (
    get_examples,
    iter_locations,
    read_file,
)
from workaround.handlers import get_handlers

from .conftest import BUILTIN_HANDLERS

EXAMPLE_FILES = sorted((Path(__file__).parent / 'test_files').iterdir())


def test_get_examples():
    results = dict(get_examples())
    assert set(results.keys()) == set(get_handlers().keys())
    assert all(results.values())


def test_iter_locations(tmpdir):
    tmpdir = Path(str(tmpdir))
    directory = tmpdir / 'test'
    directory.mkdir()

    for p in ('test1.py', 'test2.py', 'test3.py'):
        (directory / p).touch()

    (directory / 'test2').mkdir()

    for location in iter_locations([tmpdir]):
        assert location.is_file()


@pytest.mark.parametrize('path', EXAMPLE_FILES)
def test_read_files(path):
    results = list(read_file(path))
    assert len(results) == 6
    assert set(r[0].__class__ for r in results) == set(BUILTIN_HANDLERS)
