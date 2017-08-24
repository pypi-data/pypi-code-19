import sys


class range_iterator(object):
    __slots__ = ('_start', '_max_idx', '_step', '_current')

    def __init__(self, start, step, count, current=-1):
        """
        Iterator over a `range`, for internal use only

        Argument `current` used for pickle support.
        """
        self._start = start
        self._step = step
        self._max_idx = count - 1
        self._current = current

    def __iter__(self):
        return self

    def _next(self):
        if self._current == self._max_idx:
            raise StopIteration
        self._current += 1
        return self._start + self._step * self._current

    if sys.version_info < (3,):
        next = _next
    else:
        __next__ = _next

    def __length_hint__(self):
        # both stop and current are offset by 1 which cancels out here
        return self._max_idx - self._current

    # Pickling
    def __getstate__(self):
        return self._start, self._max_idx, self._step, self._current

    def __setstate__(self, state):
        self._start, self._max_idx, self._step, self._current = state
