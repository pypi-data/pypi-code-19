from lhc.collections import MultiDimensionMap
from lhc.interval import Interval


class VcfSet(object):
    def __init__(self, iterator):
        self.data = list(iterator)
        self.ivl_index = MultiDimensionMap([str, Interval])
        for i, variant in enumerate(self.data):
            ivl = Interval(variant.position, variant.position + len(variant.data['ref']))
            self.ivl_index[(variant.chromosome, ivl)] = i

    def fetch(self, chr, start, stop=None):
        if stop is None:
            stop = start + 1
        idxs = self.ivl_index[(chr, Interval(start, stop))]
        return [self.data[v] for v in idxs]
