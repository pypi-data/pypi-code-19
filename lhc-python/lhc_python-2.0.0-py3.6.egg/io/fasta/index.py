import pysam


class IndexedFastaSet(object):
    def __init__(self, filename):
        self.tabix_index = pysam.FastaFile(filename)

    def __getitem__(self, key):
        return self.fetch(str(key.chromosome), key.start.position, key.stop.position)

    def fetch(self, chr, start, stop=None):
        if stop is None:
            stop = start + 1
        return self.tabix_index.fetch(chr, start, stop)
