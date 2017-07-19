from functools import total_ordering
from lhc.order import natural_key


class ChromosomeIdentifier:
    def __init__(self, parts):
        self.parts = tuple(parts)

    def __str__(self):
        return ''.join(str(part) for part in self.parts)

    def __hash__(self):
        return hash(self.parts)

    def __eq__(self, other):
        return self.parts == other.parts

    def __lt__(self, other):
        return self.parts < other.parts


@total_ordering
class GenomicPosition:

    def __init__(self, chromosome, position, *, strand='+', data=None):
        self.chromosome = chromosome if isinstance(chromosome, ChromosomeIdentifier) else ChromosomeIdentifier(natural_key(chromosome))
        self.position = position
        self.strand = strand
        self.data = data

    def __str__(self):
        return '{}:{}:{}'.format(self.chromosome, self.strand, self.position + 1)

    def __repr__(self):
        return 'GenomicPosition({})'.format(self)

    def __hash__(self):
        return hash((self.chromosome, self.position))

    def __eq__(self, other):
        return self.chromosome == other.chromosome and self.position == other.position and\
            self.strand == other.strand

    def __lt__(self, other):
        return (self.chromosome < other.chromosome) or\
            (self.chromosome == other.chromosome) and (self.position < other.position)

    def __add__(self, other):
        """
        Add an integer to the current position
        :param int other: integer to add
        :return: new position
        :rtype: GenomicPosition
        """
        return GenomicPosition(self.chromosome, self.position + other, strand=self.strand)

    def __sub__(self, other):
        """
        Subtract either an integer from the current position
        :param int other: integer to subtract
        :return: new position
        :rtype: GenomicPosition
        """
        if isinstance(other, GenomicPosition):
            return self.get_distance_to(other)
        return GenomicPosition(self.chromosome,
                               self.position - other if self.strand == '+' else self.position + other,
                               strand=self.strand)

    def get_distance_to(self, other):
        """
        Get the distance between two positions
        :param GenomicPosition other: other position
        :return: distance between positions
        :rtype: int
        """
        if self.chromosome != other.chromosome:
            raise ValueError('Positions on different chromosomes: "{}" and "{}"'.format(self.chromosome, other.chromosome))
        return self.position - other.position
