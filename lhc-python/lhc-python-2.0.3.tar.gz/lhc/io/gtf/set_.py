from lhc.collections import MultiDimensionMap
from lhc.interval import Interval


class GtfSet(object):
    def __init__(self, iterator):
        self.key_index = {}
        self.ivl_index = MultiDimensionMap([str, Interval])
        self.data = list(iterator)
        for i, entry in enumerate(self.data):
            self.key_index[entry.data['name']] = i
            self.ivl_index[(entry.chromosome, Interval(entry.start.position, entry.stop.position))] = i

    def __getitem__(self, key):
        return self.data[self.key_index[key]]

    def fetch(self, chr, start, stop):
        return [self.data[v] for v in self.ivl_index[chr, Interval(start, stop)]]
