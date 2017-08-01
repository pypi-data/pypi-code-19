"""Test `ctorrepr` module."""

from itertools import chain
from mock import patch, Mock
import pytest
from ctorrepr import CtorRepr


class CtorReprUT(CtorRepr):
    """CtorRepr instance under test."""


def test_ctorrepr_calls_collect_repr_args():
    """`CtorRepr` should call _collect_repr_args()."""
    sut = CtorReprUT()
    with patch.object(sut, '_collect_repr_args') as collector:
        repr(sut)
        assert collector.called


def test_ctorrepr_passes_args_and_kwargs_of_right_types():
    """`CtorRepr` should pass list/dict as args/kwargs to the collector."""
    sut = CtorReprUT()

    def collect(args, kwargs):
        assert isinstance(args, list)
        assert isinstance(kwargs, dict)
    with patch.object(sut, '_collect_repr_args', side_effect=collect) as c:
        repr(sut)
        assert c.called


def test_ctorrepr_passes_empty_args_and_kwargs():
    """`CtorRepr` should pass empty args/kwargs."""
    sut = CtorReprUT()

    def collect(args, kwargs):
        assert len(args) == 0
        assert len(kwargs) == 0
    with patch.object(sut, '_collect_repr_args', side_effect=collect) as c:
        repr(sut)
        assert c.called


class MyInt (int):
    """My integer."""

    def __repr__(self):
        """
        Return the representation of this object.

        This is a passthrough method, but do not remove: `int`.`__repr__`
        cannot be patched.
        """
        return super().__repr__()


@pytest.fixture
def expected_args():
    """``(1000, 1010, 1020, ..., 1980, 1990)``."""
    def generate():
        for i in range(1000, 2000, 10):
            m = Mock()
            m.__repr__ = Mock()
            m.__repr__.return_value = repr(i)
            yield m
    return tuple(generate())


@pytest.fixture
def expected_kwargs():
    """``{'@': 0, 'A': 10, 'B': 20, ..., 'Y': 250, 'Z': 260}``."""
    def generate_items():
        for i, c in enumerate('@ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            m = Mock()
            m.__repr__ = Mock()
            m.__repr__.return_value = repr(10 * i)
            yield c, m
    return dict(generate_items())


def test_ctorrepr_calls_repr_on_all_args(expected_args, expected_kwargs):
    """`CtorRepr` should call `__repr__()` on all args and kwargs."""
    def collect(args, kwargs):
        args[:0] = expected_args
        kwargs.update(expected_kwargs)
    sut = CtorReprUT()
    with patch.object(sut, '_collect_repr_args', collect):
        for m in chain(expected_args, expected_kwargs.values()):
            m.reset_mock()
        repr(sut)
        for i, m in enumerate(expected_args):
            assert m.__repr__.called, ("SUT did not repr args[{!r}]".format(i))
        for k, m in expected_kwargs.items():
            assert m.__repr__.called, ("SUT did not repr kwargs[{!r}]"
                                       .format(k))


def test_ctorrepr_output(expected_args, expected_kwargs):
    """`CtorRepr` should emit the right output."""
    def collect(args, kwargs):
        args[:0] = expected_args
        kwargs.update(expected_kwargs)
    sut = CtorReprUT()
    with patch.object(sut, '_collect_repr_args', side_effect=collect):
        r = repr(sut)
    start = 'CtorReprUT('
    end = ')'
    assert r.startswith(start)
    assert r.endswith(end)
    args_repr = r[len(start):-len(end)]
    args_repr0 = args_repr
    sep = ''
    for arg in expected_args:
        assert args_repr.startswith(sep)
        args_repr = args_repr[len(sep):]
        sep = ', '
        arg_repr = repr(arg)
        assert args_repr.startswith(arg_repr)
        args_repr = args_repr[len(arg_repr):]
    item_reprs = {'{}={!r}'.format(k, v) for k, v in expected_kwargs.items()}
    while item_reprs:
        assert args_repr.startswith(sep)
        args_repr = args_repr[len(sep):]
        sep = ', '
        for item_repr in item_reprs:
            if args_repr.startswith(item_repr):
                break
        else:
            assert False, ("remaining args repr {!r} starts with none of "
                           "remaining item reprs {!r} (original repr is {!r})"
                           .format(args_repr, item_reprs, args_repr0))
        item_reprs.remove(item_repr)
        args_repr = args_repr[len(item_repr):]
    assert not args_repr
