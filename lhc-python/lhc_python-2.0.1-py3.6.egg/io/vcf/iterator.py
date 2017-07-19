from collections import OrderedDict, namedtuple
from typing import Iterator
from lhc.binf.genomic_coordinate import GenomicPosition

Variant = namedtuple('Variant', ('pos', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'format', 'samples'))


class VcfIterator:
    __slots__ = ('iterator', 'header', 'samples')

    def __init__(self, iterator: Iterator[str]):
        self.iterator = iterator
        self.header, self.samples = get_header(iterator)

    def __iter__(self):
        return self

    def __next__(self):
        parts = next(self.iterator).rstrip('\r\n').split('\t')
        info = dict(i.split('=', 1) if '=' in i else (i, i) for i in parts[7].split(';'))
        format = None if len(parts) < 9 else parts[8].split(':')
        return GenomicPosition(parts[0], int(parts[1]) - 1, data={
            'id': parts[2],
            'ref': parts[3],
            'alt': parts[4].split(','),
            'qual': get_float(parts[5]),
            'filter': set(parts[6].split(',')),
            'info': info,
            'format': format,
            'samples': get_samples(self.samples, parts[9:], format)
        })

    def __getstate__(self):
        return self.iterator, self.header, self.samples

    def __setstate__(self, state):
        self.iterator, self.header, self.samples = state


def get_header(iterator):
    header = OrderedDict()
    line = next(iterator)
    while line.startswith('##'):
        key, value = line[2:].strip().split('=', 1)
        if key not in header:
            header[key] = set()
        header[key].add(value)
        line = next(iterator)
    samples = line.rstrip('\r\n').split('\t')[9:]
    return header, samples


def get_float(string):
    try:
        return float(string)
    except:
        pass


def get_samples(names, parts, format):
    samples = {}
    for name, part in zip(names, parts):
        samples[name] = {} if part == '.' else dict(zip(format, part.split(':')))
    return samples
