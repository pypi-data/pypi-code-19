import bisect

from functools import lru_cache


class InOrderAccessIntervalSet(object):
    def __init__(self, iterator):
        self._iterator = iterator
        self._stops = []
        self._items = []
        self._item = next(self._iterator)
        pass

    @lru_cache()
    def __getitem__(self, key):
        stops = self._stops
        items = self._items

        while len(stops) > 0 and stops[0] <= key.start:
            stops.pop(0)
            items.pop(0)

        item = self._item
        try:
            while item.start < key.stop:
                if key.start < item.stop:
                    index = bisect.bisect_right(stops, item.stop)
                    stops.insert(index, item.stop)
                    items.insert(index, item)
                item = next(self._iterator)
        except StopIteration:
            pass
        self._item = item

        return sorted(items)
