from time import monotonic

from .screen import Screen
from .terminal import write
from .utils import Point, PointList, Rectangle


class PPGR:
    def __init__(self, line_format, fail_bad_line=False, wait=None, time_scale=None, limit=None):
        self.format = line_format
        self.fail_bad_line = fail_bad_line
        self.ps = PointList(limit)

        self.wait = wait
        if self.wait is not None:
            self.wait /= 1000

        self.time_scale = time_scale
        if self.time_scale is None:
            self.t0 = monotonic()

        self.screen = Screen()
        self.t = 0

    def _prep_screen(self, max_x=None, min_x=None, max_y=None, min_y=None):
        """Preps the canvas so that it can be drawn."""

        def f(l1, l2):
            try:
                return l1 / l2
            except ZeroDivisionError:
                return 1

        def scale(p):
            """Transform point p from internal coordinates to screen coordinates."""

            return Point(
                fact.x * (p.x - bounds.x1),
                size.y - fact.y * (p.y - bounds.y1))

        self.screen.size = None, None
        size = Point(*self.screen.size)
        bounds = self.ps.bounds(Rectangle(min_x, min_y, max_x, max_y))
        fact = Point(
            f(size.x, abs(bounds.x1 - bounds.x2)),
            f(size.y, abs(bounds.y1 - bounds.y2)))

        for p in map(scale, self.ps.points()):
            self.screen(*p)

    def _update_t(self):
        if self.time_scale is None:
            self.t = monotonic() - self.t0
        else:
            self.t += self.time_scale

    def line(self, line):
        # TODO better error handling
        # TODO better support for --fail-bad-line
        # TODO add support for histograms (difficult?)
        f = {
            "a": lambda a: f["d"](a) if len(a) >= 2 else f["t"](a),
            "t": lambda a: Point(self.t, a.pop()),
            "d": lambda a: Point(a.pop(), a.pop())}

        _line = line

        try:
            line = list(map(float, line.strip().split()))
        except (ValueError, TypeError) as e:
            if self.fail_bad_line:
                raise Exception("bad line: {}".format(_line))
            else:
                return

        a = list(reversed(line))

        out = []
        for i in self.format:
            try:
                if i == "s":
                    a.pop()
                    continue
                out.append(f[i](a))
            except IndexError as e:
                if self.fail_bad_line:
                    raise Exception("bad line: {} failed".format(_line))

        self.ps.extend(out)
        self._update_t()

    def show(self, max_x=None, min_x=None, max_y=None, min_y=None, no_animate=False, newline=False):
        self._prep_screen(max_x, min_x, max_y, min_y)
        write(
            self.screen,
            wait=None if no_animate else self.wait,
            end="\n" if newline else "")
