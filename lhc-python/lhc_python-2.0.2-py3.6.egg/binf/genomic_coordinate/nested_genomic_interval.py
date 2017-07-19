from .genomic_interval import GenomicInterval
from lhc.binf.sequence.reverse_complement import reverse_complement


class NestedGenomicInterval(GenomicInterval):
    def __init__(self, start, stop, *, chromosome=None, strand='+', data=None):
        super().__init__(start, stop, chromosome=chromosome, strand=strand, data=data)
        self.children = []

    def __str__(self):
        return '{}:{}..{}'.format(self.chromosome, self.start, self.stop)

    def __len__(self):
        if len(self.children) == 0:
            return self.stop - self.start
        return sum(len(child) for child in self.children)

    def switch_strand(self):
        super().switch_strand()
        for child in self.children:
            child.switch_strand()

    # Position functions
    
    def get_abs_pos(self, pos):
        intervals = self.children if self.strand == '+' else reversed(self.children)
        fr = 0
        for interval in intervals:
            length = len(interval)
            if fr <= pos < fr + length:
                return interval.get_abs_pos(pos - fr)
            fr += length
        raise IndexError('relative position {} not contained within {}'.format(pos, self))
    
    def get_rel_pos(self, pos, types=None):
        if len(self.children) == 0:
            if types is None or self.data['type'] in types:
                return pos - self.start.position
            else:
                raise ValueError('Position in interval but not of right type.')

        rel_pos = 0
        intervals = iter(self.children) if self.strand == '+' else reversed(self.children)
        for interval in intervals:
            if interval.start.position <= pos < interval.stop.position:
                return rel_pos + interval.get_rel_pos(pos, types=types)
            if types is None or interval.data['type'] in types:
                rel_pos += len(interval)
        raise IndexError('absolute position {} not contained within {}'.format(pos, self))
    
    # Sequence functions
    
    def get_sub_seq(self, sequence_set, *, types=None):
        res = ''
        if len(self.children) > 0:
            res = ''.join(child.get_sub_seq(sequence_set, types=types) for child in self.children)
        elif types is None or self.data['type'] in types:
            res = super().get_sub_seq(sequence_set)
        return res if self.strand == '+' else reverse_complement(res)

    def get_5p(self):
        return self.children[0].get_5p() if self.strand == '+' else\
            self.children[-1].get_5p()

    def get_3p(self):
        return self.children[-1].get_3p() if self.strand == '+' else\
            self.children[0].get_3p()
