from collections import namedtuple
from itertools import chain
from lhc.binf.genomic_coordinate import GenomicInterval as Interval, NestedGenomicInterval as NestedInterval
from lhc.binf.genomic_coordinate.nested_genomic_interval_factory import NestedGenomicIntervalFactory


GtfLine = namedtuple('GtfLine', ('chr', 'source', 'type', 'start', 'stop', 'score', 'strand', 'phase', 'attr'))


class GtfLineIterator:
    def __init__(self, iterator):
        self.iterator = iterator
        self.line_no = 0
        self.hdr = self.parse_header()

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            line = self.parse_line(next(self.iterator))
            self.line_no += 1
            if line.data['type'] != 'chromosome':
                break
        return line

    def close(self):
        if hasattr(self.iterator, 'close'):
            self.iterator.close()

    def parse_header(self):
        hdrs = []
        line = next(self.iterator)
        line_no = 1
        while line.startswith('#'):
            hdrs.append(line)
            line = self.iterator.readline()
            line_no += 1
        self.line_no = line_no
        self.iterator = chain([line], self.iterator)
        return hdrs

    @staticmethod
    def parse_line(line):
        parts = line.rstrip('\r\n').split('\t')
        return Interval(int(parts[3]) - 1, int(parts[4]),
                        chromosome=parts[0],
                        strand=parts[6],
                        data={
                            'source': parts[1],
                            'type': parts[2],
                            'score': parts[5],
                            'phase': parts[7],
                            'attr': GtfLineIterator.parse_attributes(parts[8])
                        })

    @staticmethod
    def parse_attributes(attr):
        parts = (part.strip() for part in attr.split(';'))
        parts = [part.split(' ', 1) for part in parts if part != '']
        for part in parts:
            part[1] = part[1][1:-1] if part[1].startswith('"') else int(part[1])
        return dict(parts)


class GtfIterator:

    __slots__ = ('iterator', 'factory')

    def __init__(self, iterator, header=False):
        self.iterator = iterator
        self.factory = NestedGenomicIntervalFactory()

        if header:
            line = next(self.iterator)
            self.factory.add_interval(_get_interval(line, 0), parents=_get_parent(line))

    def __iter__(self):
        return self

    def __next__(self) -> NestedInterval:
        if self.factory.drained():
            raise StopIteration

        try:
            while not self.factory.has_complete_interval():
                line = next(self.iterator)
                self.factory.add_interval(_get_interval(line, self.iterator.line_no), parents=_get_parent(line))
        except StopIteration:
            self.factory.close()

        return self.factory.get_complete_interval()

    def __getstate__(self):
        return self.iterator, self.factory

    def __setstate__(self, state):
        self.iterator, self.factory = state


def _get_interval(line, line_no):
    name = _get_name(line, default_id=str(line_no))
    data = {'type': line.data['type'], 'attr': line.data['attr'], 'name': name}
    return NestedInterval(line.start, line.stop, strand=line.strand, data=data)


def _get_name(line, *, default_id=None):
    return line.data['attr']['gene_name'] if line.data['type'] == 'gene' else \
        line.data['attr']['transcript_id'] if line.data['type'] == 'transcript' else \
        default_id


def _get_parent(line):
    if line.data['type'] == 'gene':
        return None
    elif line.data['type'] == 'transcript':
        return [line.data['attr']['gene_name']]
    elif 'transcript_id' in line.data['attr']:
        return [line.data['attr']['transcript_id']]
