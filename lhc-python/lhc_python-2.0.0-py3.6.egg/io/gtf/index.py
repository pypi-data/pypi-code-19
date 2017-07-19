import pysam

from functools import lru_cache
from lhc.binf.genomic_coordinate.nested_genomic_interval_factory import NestedGenomicIntervalFactory
from lhc.io.gtf.iterator import GtfLineIterator, _get_interval, _get_parent


class IndexedGtfFile(object):
    def __init__(self, filename, max_buffer=16):
        self.tabix_file = pysam.TabixFile(filename)
        self.buffer = {}
        self.max_buffer = max_buffer
        self.factory = NestedGenomicIntervalFactory()

    def __getitem__(self, key):
        return self.fetch(str(key.chromosome), key.start.position, key.stop.position)

    def fetch(self, chr, start, stop):
        genes = []
        for line in self.tabix_file.fetch(chr, start, stop):
            parts = line.rstrip('\r\n').split('\t')
            if parts[2] == 'gene':
                genes.append((parts[0], int(parts[3]) - 1, int(parts[4])))

        features = []
        for chromosome, start, stop in genes:
            self.factory.reset()
            feature = self._get_feature(chromosome, start, stop)
            if feature is not None:
                features.append(feature)
        return features

    @lru_cache(128)
    def _get_feature(self, chromosome, start, stop):
        for line in self.tabix_file.fetch(chromosome, start, stop):
            line = GtfLineIterator.parse_line(line)
            interval = _get_interval(line, 0)
            self.factory.add_interval(interval, parents=_get_parent(line))
            if self.factory.has_complete_interval():
                feature = self.factory.get_complete_interval()
                if feature.start.position == start and feature.stop.position == stop:
                    return feature
        while len(self.factory.tops) > 0:
            feature = self.factory.get_complete_interval()
            if feature.start.position == start and feature.stop.position == stop:
                return feature
        return None
