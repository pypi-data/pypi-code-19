from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from . import sources
from .source_list import SourceList

DIR = object()


@contextmanager
def temp_dir_structure(structure: dict):
    # TODO: turn this into a proper pytest fixture thingy.
    with TemporaryDirectory() as p_str:
        p = Path(p_str)
        for name, contents in structure.items():
            path = p / name
            if contents is DIR:
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                mode = 'wb' if isinstance(contents, bytes) else 'w'
                with path.open(mode) as f:
                    f.write(contents)
                    f.flush()
                    print(contents)
        try:
            yield p
        finally:
            pass  # tempdir will get destroyed by the TemporaryDirectory CM


def test_source_list_normal(monkeypatch):
    monkeypatch.setenv('FOO', 'bar')
    s = {'settings.ini': "[settings]\nBAZ: qux\n"}
    with temp_dir_structure(s) as p:
        source_list = SourceList(search_path=[str(p)])
    assert source_list['FOO'] == 'bar'
    assert source_list['BAZ'] == 'qux'
    with pytest.raises(KeyError):
        source_list['EGGS']  # noqa


def test_source_list_ambient_override(monkeypatch):
    monkeypatch.setenv('FOO', 'bar')
    s = {'settings.ini': "[settings]\nFOO: baz\n"}
    with temp_dir_structure(s) as p:
        source_list = SourceList(search_path=[str(p)])
    assert source_list['FOO'] == 'bar'


def test_source_list_file_override(monkeypatch):
    monkeypatch.setenv('FOO', 'baz')
    s = {'settings.ini': "[settings]\nFOO: bar\n"}
    with temp_dir_structure(s) as p:
        source_list = SourceList(
            search_path=[str(p)],
            input_sources=(sources.IniFileSource(),
                           sources.EnvironmentSource()),
        )
    assert source_list['FOO'] == 'bar'


def test_source_list_multiple_files():
    s = {
        'a/settings.ini': "[settings]\nFOO: bar\n",
        'b/settings.ini': "[settings]\nFOO: baz\n",
    }
    with temp_dir_structure(s) as p:
        source_list = SourceList(search_path=[str(p / 'a'), str(p / 'b')])
    assert source_list['FOO'] == 'bar'


def test_search_path_order_takes_precedence_over_file_source_order():
    s = {
        'a/second.ini': "[settings]\nFOO: bar\n",
        'b/first.ini': "[settings]\nFOO: baz\n",
    }
    with temp_dir_structure(s) as p:
        source_list = SourceList(
            search_path=[str(p / 'a'), str(p / 'b')],
            input_sources=(sources.IniFileSource(filename='first.ini'),
                           sources.IniFileSource(filename='second.ini'))
        )
    assert source_list['FOO'] == 'bar'


def non_contiguous_file_sources_not_allowed():
    with pytest.raises(ValueError):
        SourceList(search_path=(), input_sources=(sources.IniFileSource(),
                                                  sources.EnvironmentSource(),
                                                  sources.IniFileSource()))
