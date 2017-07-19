class GbkSequenceSet(object):
    def __init__(self, fileobj):
        fileobj = iter(fileobj)
        locus = None
        for line in fileobj:
            if line.startswith('LOCUS'):
                locus = line.split()[1]
            if line.startswith('ORIGIN'):
                break
        seq = []
        for line in fileobj:
            seq.extend(line.split()[1:])
        self.seq = {locus: ''.join(seq)}

    def __getitem__(self, item):
        return self.seq[item]

    def fetch(self, chr, start, stop):
        return self.seq[chr][start:stop]
