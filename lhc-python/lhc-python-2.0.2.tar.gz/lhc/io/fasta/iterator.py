from lhc.binf.genomic_coordinate import GenomicInterval


class FastaIterator:

    __slots__ = ('iterator', 'header', 'sequence')

    def __init__(self, iterator):
        self.iterator = iterator
        self.header = next(iterator).rstrip('\r\n')[1:]
        self.sequence = []

    def __iter__(self):
        return self

    def __next__(self):
        header = self.header
        if header is None:
            raise StopIteration

        sequence = self.sequence
        for line in self.iterator:
            if line.startswith('>'):
                self.header = line.rstrip('\r\n')[1:]
                self.sequence = []
                return header, ''.join(sequence)
            else:
                sequence.append(line.rstrip('\r\n'))
        self.header = None
        return header, ''.join(sequence)

    def __getstate__(self):
        return self.iterator, self.header, self.sequence

    def __setstate__(self, state):
        self.iterator, self.header, self.sequence = state


class FastaFragmentIterator:

    __slots__ = ('_iterator', '_header', '_position')

    def __init__(self, iterator):
        self._iterator = iterator
        self._header = next(iterator).rstrip('\r\n')[1:]
        self._position = 0

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self._iterator)
        while line.startswith('>'):
            self._header = line.rstrip('\r\n')[1:]
            self._position = 0
            line = next(self._iterator)
        sequence = line.rstrip('\r\n')
        position = self._position
        self._position += len(sequence)
        return GenomicInterval(position, self._position, chromosome=self._header, data=sequence)

    def __getstate__(self):
        return self._iterator, self._header, self._position

    def __setstate__(self, state):
        self._iterator, self._header, self._position = state
