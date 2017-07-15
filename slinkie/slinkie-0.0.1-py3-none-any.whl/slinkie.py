from collections import defaultdict


def _first(items):
    return next(iter(items))


class Slinkie:
    def __init__(self, items):
        self._items = iter(items)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._items)

    def filter(self, selector):
        return Slinkie(filter(selector, self._items))

    def map(self, selector):
        return Slinkie(map(selector, self._items))

    def skip(self, n):
        for i in range(n):
            next(self._items)
        return self

    def take(self, n):
        def inner():
            for _ in range(n):
                yield next(self._items)
        return Slinkie(inner())

    def first(self, selector=None):
        return next(self) if selector is None else next(filter(selector, self._items))

    def first_or_none(self, selector=None):
        return next(self, None) if selector is None else next(filter(selector, self._items), None)

    def last(self, selector=None):
        return list(self if selector is None else filter(selector, self._items))[-1]

    def last_or_none(self, selector=None):
        try:
            return self.last(selector)
        except IndexError:
            return None

    def not_none(self):
        return Slinkie(filter(lambda it: it is not None, self._items))

    def group(self, key):
        grouped = defaultdict(list)

        for it in self._items:
            grouped[key(it)].append(it)

        return Slinkie((k, Slinkie(v)) for k, v in grouped.items())

    def extend(self, items):
        def _inner():
            yield from self
            yield from iter(items)
        return Slinkie(_inner())

    def exclude(self, items, key=None):
        if key:
            keys = list(map(key, items))
        else:
            key = lambda it: it
            keys = items

        return Slinkie(filter(lambda it: key(it) not in keys, self._items))

    def partition(self, n):
        def inner():
            while True:
                result = self.take(n).list()
                if not result:
                    raise StopIteration
                yield Slinkie(result)
        return Slinkie(inner())

    def sort(self, key, reverse=False):
        return Slinkie(sorted(self._items, key=key, reverse=reverse))

    def join(self, glue=''):
        return glue.join(map(str, self._items))

    def len(self):
        return sum(1 for _ in self._items)

    def list(self):
        return list(self._items)

    def tuple(self):
        return tuple(self._items)

    def set(self):
        return set(self._items)

    def dict(self, key=None, value=None):

        if key is None:
            key = lambda it: it[0]

        if value is None:
            value = lambda it: it[1]

        return {key(it): value(it) for it in self._items}

    # Aliases
    where = filter
    select = map
    count = len
    __add__ = extend
    __sub__ = exclude
    __rshift__ = skip