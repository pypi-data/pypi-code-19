from dev_cache import cached_to_file


@cached_to_file()
def foo(a, b, c):
    return a, b, c


def test_basic():
    foo(1, 1, 1)
    foo(1, 1, 1)
    assert foo(1, 2, 1) == (1, 2, 1)
