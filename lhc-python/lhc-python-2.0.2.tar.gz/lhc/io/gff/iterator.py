from lhc.binf.genomic_coordinate import GenomicInterval as Interval
from lhc.binf.genomic_coordinate import NestedGenomicInterval as NestedInterval
from lhc.binf.genomic_coordinate.nested_genomic_interval_factory import NestedGenomicIntervalFactory


class GffLineIterator:

    __slots__ = ('iterator', 'line_no', 'filter')

    def __init__(self, iterator, filter=None):
        self.iterator = iterator
        self.line_no = 0
        self.filter = filter if filter else set()

    def __iter__(self):
        return self

    def __next__(self) -> Interval:
        line = None
        while True:
            line = self.parse_line(next(self.iterator))
            self.line_no += 1
            if line.data['type'] != 'chromosome' or line.data['type'] in self.filter:
                break
        return line

    @staticmethod
    def parse_line(line) -> Interval:
        parts = line.rstrip('\r\n').split('\t')
        return Interval(int(parts[3]) - 1, int(parts[4]),
                        chromosome=parts[0],
                        strand=parts[6],
                        data={
                            'source': parts[1],
                            'type': parts[2],
                            'score': parts[5],
                            'phase': parts[7],
                            'attr': GffLineIterator.parse_attributes(parts[8])
                        })

    @staticmethod
    def parse_attributes(attr):
        res = {}
        for part in attr.split(';'):
            if part == '':
                continue
            k, v = part.split('=', 1) if '=' in part else part
            res[k] = v.split(',')
        return res

    def __getstate__(self):
        return self.iterator, self.line_no

    def __setstate__(self, state):
        self.iterator, self.line_no = state


class GffIterator:

    __slots__ = ('iterator', 'factory')

    def __init__(self, iterator, header=False):
        self.iterator = iterator
        self.factory = NestedGenomicIntervalFactory()

        if header:
            line = next(self.iterator)
            self.factory.add_interval(_get_interval(line, 0),
                                      parents=line.data['attr'].get('Parent', None))

    def __iter__(self):
        return self

    def __next__(self):
        if self.factory.drained():
            raise StopIteration

        try:
            while not self.factory.has_complete_interval():
                line = next(self.iterator)
                self.factory.add_interval(_get_interval(line, self.iterator.line_no),
                                          parents=line.data['attr'].get('Parent', None))
        except StopIteration:
            self.factory.close()

        if not self.factory.has_complete_interval():
            raise StopIteration
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
    attr = line.data['attr']
    id = attr.get('ID', default_id)
    name = attr.get('transcript_id', id)[0] if line.data['type'] in {'mRNA', 'exon', 'transcript'} else \
        attr.get('protein_id', id)[0] if line.data['type'] == 'CDS' else \
        attr.get('ID', id)[0] if line.data['type'] == 'protein' else \
        attr.get('Name', id)[0]
    return name
