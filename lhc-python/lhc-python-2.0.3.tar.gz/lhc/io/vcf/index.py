import gzip
import pysam

from lhc.binf.genomic_coordinate import GenomicPosition
from lhc.io.vcf.iterator import VcfIterator, get_float, get_samples


class IndexedVcfFile(object):
    def __init__(self, filename):
        self.iterator = VcfIterator(gzip.open(filename, 'rt') if filename.endswith('gz') else open(filename, encoding='utf-8'))
        self.tabix_file = pysam.TabixFile(filename)

    def __getitem__(self, key):
        return self.fetch(str(key.chromosome), key.start.position, key.stop.position)

    def fetch(self, chr, start, stop):
        variants = []
        for line in self.tabix_file.fetch(chr, start, stop):
            parts = line.rstrip('\r\n').split('\t')
            info = dict(i.split('=', 1) if '=' in i else (i, i) for i in parts[7].split(';'))
            format = None if len(parts) < 9 else parts[8].split(':')
            variants.append(GenomicPosition(parts[0], int(parts[1]) - 1, data={
                'id': parts[2],
                'ref': parts[3],
                'alt': parts[4].split(','),
                'qual': get_float(parts[5]),
                'filter': set(parts[6].split(',')),
                'info': info,
                'format': format,
                'samples': get_samples(self.iterator.samples, parts[9:], format)
            }))
        return variants
