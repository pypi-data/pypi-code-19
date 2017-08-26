from typing import Callable, Tuple, Iterable, TypeVar, Optional

from .curried import curried

T = TypeVar('T')
S = TypeVar('S')


@curried
def tmap(func: Callable[[T], S], iterable: Iterable[T]) -> Tuple[S, ...]:
    return tuple(map(func, iterable))


@curried
def tfilter(func: Callable[[T], bool], iterable: Iterable[T]) -> Tuple[T, ...]:
    return tuple(filter(func, iterable))


def find(func: Callable[[T], bool], iterable: Iterable[T]) -> Optional[T]:
    try:
        return next(filter(func, iterable))
    except(StopIteration):
        return None
