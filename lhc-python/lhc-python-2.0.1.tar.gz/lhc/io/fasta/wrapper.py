from lhc.binf.genomic_coordinate import GenomicInterval


class FastaWrapper:

    __slots__ = ('_fileobj', '_wrap', '_chunk_size', '_chunk', '_header', '_position', '_chunk_position')

    def __init__(self, fileobj, wrap=200, chunk_size=2 ** 16):
        self._fileobj = fileobj
        self._wrap = wrap
        self._chunk_size = chunk_size
        self._chunk = fileobj.read(chunk_size)
        self._header = None
        self._position = 0
        self._chunk_position = 0

    def __iter__(self):
        return self

    def __next__(self):
        chunk = self._chunk
        chunk_position = self._chunk_position

        if chunk_position >= len(chunk):
            chunk = self._fileobj.read(self._chunk_size)
            if chunk == '':
                raise StopIteration

        while chunk_position < len(chunk) and chunk[chunk_position] == '>':
            newline_position = chunk.find('\n', chunk_position)
            if newline_position != -1:
                self._header = chunk[chunk_position + 1:newline_position]
                chunk_position = newline_position + 1
            else:
                chunks = [chunk[chunk_position + 1:]]
                chunk = self._fileobj.read(self._chunk_size)
                newline_position = chunk.find('\n')
                while chunk != '' and newline_position == -1:
                    chunks.append(chunk)
                    chunk = self._fileobj.read(self._chunk_size)
                    newline_position = chunk.find('\n')
                chunks.append(chunk[:newline_position])
                self._header = ''.join(chunks)
                chunk_position = newline_position + 1
            self._position = 0

        wrap = self._wrap
        chunks = []
        while chunk_position < len(chunk) and chunk[chunk_position] != '>':
            newline_position = chunk.find('\n', chunk_position)
            if newline_position == -1:
                if chunk_position + wrap <= len(chunk):
                    chunks.append(chunk[chunk_position:chunk_position + wrap])
                    chunk_position += wrap
                    break
                else:
                    chunks.append(chunk[chunk_position:])
                    wrap -= len(chunk) - chunk_position
                    chunk = self._fileobj.read(self._chunk_size)
                    chunk_position = 0
            else:
                if chunk_position + wrap <= newline_position:
                    chunks.append(chunk[chunk_position:chunk_position + wrap])
                    chunk_position += wrap
                    chunk_position += chunk[chunk_position] == '\n'
                    break
                else:
                    chunks.append(chunk[chunk_position:newline_position])
                    wrap -= newline_position - chunk_position
                    chunk_position = newline_position + 1
        sequence = ''.join(chunks)
        fragment = GenomicInterval(self._position, self._position + len(sequence),
                                   chromosome=self._header, data=sequence)
        self._chunk = chunk
        self._chunk_position = chunk_position
        self._position += len(sequence)
        return fragment

    def __getstate__(self):
        return self._fileobj, self._wrap, self._chunk_size, self._chunk, self._header, self._position,\
               self._chunk_position

    def __setstate__(self, state):
        self._fileobj, self._wrap, self._chunk_size, self._chunk, self._header, self._position, \
        self._chunk_position = state
