import math
import time
from contextlib import contextmanager


class GaugeValue:
    def __init__(self):
        self.val = 0
        self.val_min = float('inf')
        self.val_max = float('-inf')

    def add(self, val):
        new_val = self.val + val
        self.set(new_val)

    def set(self, val):
        self.val_min = min(val, self.val_min)
        self.val_max = max(val, self.val_max)
        self.val = val

    def reset(self):
        self.val_max = self.val_min = self.val


def get_stats(lst):
    if not lst:
        return {}
    lst.sort()
    total = sum(lst)
    length = len(lst)
    avg = total / length
    p95 = math.ceil(length * 95 / 100) - 1
    p5 = math.ceil(length * 5 / 100) - 1
    return {
        'sum': total,
        'avg': avg,
        'max_p95': lst[p95],
        'min_p95': lst[p5]
    }


class LocalStats:
    def __init__(self, default=None):
        self.default = default or {}
        self.metrics = {}
        self.functions = {}

    def incr(self, stat, count=1, rate=1):
        if stat not in self.metrics:
            self.metrics[stat] = 0
        self.metrics[stat] += count / rate

    def decr(self, stat, count=1, rate=1):
        if stat not in self.metrics:
            self.metrics[stat] = 0
        self.metrics[stat] -= count / rate

    def gauge(self, stat, value, delta=False):
        if stat not in self.metrics:
            self.metrics[stat] = GaugeValue()
        if delta:
            self.metrics[stat].add(value)
        else:
            self.metrics[stat].set(value)

    def timing(self, stat, delta):
        if stat not in self.metrics:
            self.metrics[stat] = []
        self.metrics[stat].append(delta)

    @contextmanager
    def timer(self, stat):
        start = time.time()
        yield
        end = time.time()
        self.timing(stat, int((end-start) * 1000))

    def unique(self, stat, value):
        if stat not in self.metrics:
            self.metrics[stat] = set()
        self.metrics[stat].add(value)

    def before_flush(self, stat, func):
        self.functions[stat] = func

    def _flush(self):
        result = {}
        for stat, func in self.functions.items():
            self.gauge(stat, func())
        for k, v in self.metrics.items():
            if isinstance(v, GaugeValue):
                result[k] = v.val
                result['%s_max' % k] = v.val_max
                result['%s_min' % k] = v.val_min
                v.reset()
            elif isinstance(v, (int, float)):
                result[k] = v
                self.metrics[k] = 0
            elif isinstance(v, set):
                result[k] = len(v)
                v.clear()
            elif isinstance(v, list):
                for postfix, val in get_stats(v).items():
                    result['%s_%s' % (k, postfix)] = val
                v.clear()
        return result

    def flush(self):
        data = self._flush()
        data.update(self.default)
        return data
