from collections import deque
from itertools import islice


class InOrderAccessSet(object):
    def __init__(self, iterator):
        self._iterator = iterator
        self._items = deque()

    def __getitem__(self, key):
        items = self._items

        while len(items) > 0 and items[0] < key.start:
            items.popleft()

        try:
            while len(items) == 0 or items[-1] < key.stop:
                item = next(self._iterator)
                if key.start <= item:
                    items.append(item)
        except StopIteration:
            pass

        if len(items) > 0 and items[-1] >= key.stop:
            return list(islice(items, 0, len(items) - 1))
        return list(items)
