from collections import namedtuple

Point = namedtuple("Point", ("x", "y"))
Rectangle = namedtuple("Rectangle", ("x1", "y1", "x2", "y2"))


class PointList:
    """
    More like a "LimitableOrderedPointList", but that just sounds too much like Java.
    """

    def __init__(self, limit=None):
        if limit is not None and limit <= 0:
            raise ValueError("Limit must be larger than 0.")

        self.limit = limit

        self._ps = []
        self._min_x = None
        self._min_y = None
        self._max_x = None
        self._max_y = None

    def __len__(self):
        return len(self._ps)

    def _update(self, p):
        if self._min_x is None:
            self._min_x = p.x
        elif self._min_x > p.x:
            self._min_x = p.x

        if self._min_y is None:
            self._min_y = p.y
        elif self._min_y > p.y:
            self._min_y = p.y

        if self._max_x is None:
            self._max_x = p.x
        elif self._max_x < p.x:
            self._max_x = p.x

        if self._max_y is None:
            self._max_y = p.y
        elif self._max_y < p.y:
            self._max_y = p.y

    def _recalculate_bounds(self):
        self._min_x = None
        self._min_y = None
        self._max_x = None
        self._max_y = None
        for p in self._ps:
            self._update(p)

    def _over_limit(self):
        return self.limit is not None and len(self) > self.limit

    def _remove_extra(self):
        self._ps[:] = self._ps[len(self._ps) - self.limit:]
        self._recalculate_bounds()

    def add(self, p):
        self._ps.append(p)

        if self._over_limit():
            self._remove_extra()
        else:
            self._update(p)

    def extend(self, ps):
        self._ps.extend(ps)

        if self._over_limit():
            self._remove_extra()
        else:
            for p in self._ps[-len(ps):]:
                self._update(p)

    def points(self):
        for p in self._ps:
            yield p

    def bounds(self, b=None):
        if len(self._ps) > 0:
            # assert that none of mins or maxs are None
            assert(4 == len(list(
                filter(lambda x: x is not None, (
                    self._min_x, self._min_y,
                    self._max_x, self._max_y)))))
        elif len(self._ps) == 0:
            return Rectangle(0, 0, 0, 0)

        if b is None:
            b = Rectangle(None, None, None, None)

        return Rectangle(
            self._min_x if b.x1 is None else b.x1,
            self._min_y if b.y1 is None else b.y1,
            self._max_x if b.x2 is None else b.x2,
            self._max_y if b.y2 is None else b.y2)
