import gzip

from ..iterator import VcfIterator


class IndexedVcfFile(object):
    def __init__(self, fname, index):
        self.index = index
        self.it = VcfIterator(gzip.open(fname) if fname.endswith('gz') else open(fname))

    def fetch(self, chr, start, stop):
        return [self.it.parse_entry(VcfIterator.parse_line(line)) for line in self.index.fetch(chr, start, stop)]
