"""In-memory fake replacements for objects in striemann.metrics.

For use in tests.
"""

__all__ = [
    'metric_id',
    'FakeTimer',
    'FakeMetrics',
]

from striemann.metrics import MetricId


def metric_id(service_name, tags, fields):
    return MetricId(service_name, frozenset(tags), frozenset(fields.items()))


class FakeTimer:

    def __init__(self, service_name, tags, attributes, metrics):
        self.metric_id = metric_id(service_name, tags, attributes)
        self.metrics = metrics

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.metrics.append((self.metric_id, 1))


class FakeMetrics:

    def __init__(self):
        self.metrics = []

    def recordGauge(self, service_name, value, tags=[], **kwargs):
        self.metrics.append((metric_id(service_name, tags, kwargs), value))

    def time(self, service_name, tags=[], **kwargs):
        return FakeTimer(service_name, tags, kwargs, self.metrics)
