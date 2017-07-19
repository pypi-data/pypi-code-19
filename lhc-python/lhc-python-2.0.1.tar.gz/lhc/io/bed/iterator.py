from collections import namedtuple
from itertools import chain
from lhc.binf.genomic_coordinate import GenomicInterval as Interval


BedLine = namedtuple('BedLine', ('chr', 'start', 'stop', 'name', 'score', 'strand'))
BedEntry = namedtuple('BedEntry', ('ivl', 'name', 'score'))


class BedLineIterator(object):
    def __init__(self, iterator):
        self.iterator = iterator
        self.line_no = 0
        self.hdrs = self.parse_headers()
    
    def __del__(self):
        self.close()
    
    def __iter__(self):
        return self
    
    def __next__(self) -> Interval:
        line = next(self.iterator)
        if line == '':
            raise StopIteration
        self.line_no += 1
        return self.parse_line(line)

    def seek(self, fpos):
        self.iterator.seek(fpos)

    def close(self):
        if hasattr(self.iterator, 'close'):
            self.iterator.close()

    def parse_headers(self):
        hdrs = []
        line = next(self.iterator)
        line_no = 1
        while line[:5] in {'brows', 'track'}:
            line = next(self.iterator)
            line_no += 1
        if line.startswith('chromosome'):
            line = next(self.iterator)
            line_no += 1
        self.iterator = chain([line], self.iterator)
        self.line_no = line_no
        return hdrs

    @staticmethod
    def parse_line(line) -> Interval:
        parts = line.rstrip('\r\n').split('\t')
        name = parts[3] if len(parts) > 3 else ''
        score = parts[4] if len(parts) > 4 else ''
        strand = parts[5] if len(parts) > 5 else '+'
        return Interval(int(parts[1]) - 1, int(parts[2]),
                        chromosome=parts[0],
                        strand=strand,
                        data={
                            'name': name,
                            'score': score
                        })


class BedEntryIterator(BedLineIterator):
    def __init__(self, iterator):
        super().__init__(iterator)

    def __next__(self):
        line = next(self.iterator)
        self.line_no += 1
        if line == '':
            raise StopIteration
        return self.parse_entry(self.parse_line(line))

    @staticmethod
    def parse_entry(line):
        return Interval(line.start, line.stop, strand=line.strand, data={
            'name': line.data['name'],
            'score': line.data['score']
        })
