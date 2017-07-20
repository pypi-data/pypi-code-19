from typing import Iterable, Iterator, Tuple, TypeVar

T = TypeVar('T')


def pairs(iterable: Iterable[T]) -> Iterator[Tuple[T, T]]:
    it = iter(iterable)
    a = next(it)
    while True:
        b = next(it)
        yield a, b
        a = b
