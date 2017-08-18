from fractions import Fraction

import pytest
from hypothesis import given, strategies

from .na import NA

real_numbers = strategies.one_of(
    strategies.integers(),
    strategies.floats(),
    strategies.fractions(),
    strategies.decimals(),
)

single_values = strategies.one_of(
    real_numbers,
    strategies.none(),
    strategies.booleans(),
    strategies.complex_numbers(),
    strategies.characters(),
    # technically text and binary are containers, but for Hypothesis
    # purposes they're basically single values
    strategies.text(),
    strategies.binary(),
)

containers = strategies.one_of(
    strategies.tuples(),
    strategies.tuples(single_values),
    strategies.tuples(single_values, single_values),
    strategies.tuples(single_values, single_values, single_values),
    strategies.lists(single_values),
    strategies.sets(single_values),
    strategies.frozensets(single_values),
    strategies.dictionaries(single_values, single_values),
)

anything = strategies.one_of(single_values, containers)


def test_repr():
    assert repr(NA) == "NA"


def test_str():
    assert str(NA) == "NA"


def test_bytes():
    assert bytes(NA) == b"NA"


def test_format():
    assert "{}".format(NA) == "NA"
    assert "{:x}".format(NA) == "NA"
    assert "{:02f}".format(NA) == "NA"
    assert "{: <}".format(NA) == "NA"
    assert "{:totally-invalid-fspec}".format(NA) == "NA"


def test_bool():
    assert not bool(NA)
    assert not NA


def test_float():
    assert float(NA) == 0.0


def test_complex():
    assert complex(NA) == 0 + 0j


def test_round():
    assert round(NA) == 0.0
    assert round(NA, 2) == 0.0


def test_call():
    assert NA() is NA
    assert NA(1, 2, 'eggs', 'spam') is NA
    assert NA(1, 2, foo='eggs', bar='spam') is NA


def test_attrs():
    assert NA.someattr is NA
    NA.foo = 1
    assert NA.foo is NA
    del NA.bar
    assert NA.bar is NA
    assert dir(NA) == []


@pytest.mark.skip("Weird error in Hypothesis about hashing NaN")
@given(anything)
def test_ordering(x):
    assert NA < x
    assert x > NA
    assert NA <= x
    assert x >= NA
    assert NA != x
    assert x != NA
    assert NA != NA
    assert not NA == x
    assert not x == NA
    assert not NA > x
    assert not x < NA
    assert not NA >= x
    assert not x <= NA


@pytest.mark.skip("Weird error in Hypothesis about hashing NaN")
@given(anything, anything)
def test_container(x, y):
    assert NA[x] is NA
    NA[x] = y
    assert NA[x] is NA
    del NA[x]
    assert NA[x] is NA
    assert y not in NA


def test_iter():
    assert len(list(iter(NA))) == 0  # noqa
    assert len(list(reversed(NA))) == 0  # noqa


@pytest.mark.skip("Weird error in Hypothesis about hashing NaN")
@given(anything)
def test_numeric_opers(x):
    assert NA + x is NA
    assert x + NA is NA
    assert NA - x is NA
    assert x - NA is NA
    assert NA * x is NA
    assert x * NA is NA
    assert NA @ x is NA
    assert x @ NA is NA
    assert NA / x is NA
    assert x / NA is NA
    assert NA // x is NA
    if not (isinstance(x, (complex, Fraction))):
        assert x // NA is NA
    assert NA % x is NA
    if not (isinstance(x, (complex, str, bytes))):
        assert x % NA is NA
    assert NA ** x is NA
    assert x ** NA is NA
    assert NA << x is NA
    assert x << NA is NA
    assert NA >> x is NA
    assert x >> NA is NA
    assert NA & x is NA
    assert x & NA is NA
    assert NA ^ x is NA
    assert x ^ NA is NA
    assert NA | x is NA
    assert x | NA is NA
    assert -NA is NA
    assert +NA is NA
    assert abs(NA) is NA
    assert ~NA is NA


@given(real_numbers)
def test_divmod(x):
    assert divmod(NA, x) == (NA, NA)
    if not isinstance(x, Fraction):
        assert divmod(x, NA) == (NA, NA)


def test_context_manager():
    y = None
    with NA as x:
        y = x
    assert y is NA


def test_context_manager_exc():
    with NA:
        raise ValueError('should not propagate')


@pytest.mark.asyncio
async def test_await():
    assert (await NA) is NA


@pytest.mark.asyncio
async def test_async_iter():
    n = 0
    async for _ in NA:  # noqa
        n += 1
    assert n == 0


@pytest.mark.asyncio
async def test_async_context_manager():
    y = None
    async with NA as x:
        y = x
    assert y is NA


@pytest.mark.asyncio
async def test_async_context_manager_exc():
    async with NA:
        raise ValueError('should not propagate')
