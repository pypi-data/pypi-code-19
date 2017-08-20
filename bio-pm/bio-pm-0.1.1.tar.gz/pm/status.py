# -*- coding: utf-8 -*-
"""
PM status data structure module.

Provides a orderable data structure for point mutation status. 
e.g. Y > Conserved is True; Y(aa_pm=0) > Y(aa_pm=None) is True.

NOTE:
    PM status objects with inconsistent stdseq are not orderable,
    and it regards sequences which gaps, '-', has been removed from
    the orignal stdseq as the stdseq to compare. So status with 
    stdseq='ATG-AAT' and status with stdseq='ATGAAT' is comparable.

Class:

Y
Conserved
PM
NA

Const:

SCORE_MATIX
matix used to calculate score of status, see NA._score(self)

MAX_BASE
max length of sequence allowed. If the real sequence length is excess, then
the order of the status might be wrong.

"""

SCORE_MATIX = {'Y': 6.0, 
               'Conserved': 4.0, 
               'PM': 2.0, 
               'NA': 0.0, 
               'gaps': -16.0, 
               'aa_pm': -1.0, 
               'nt_pm': -0.2
              }
MAX_BASE = 10000000


class NA(object):
    """Base object of PM status

    """
    
    __status__ = "NA"

    def __init__(self, seq=None, stdseq=None, pattern=None, length=0, gaps=0, nt_pm=0, aa_pm=None):
        """
        
        Args:

        seq -- sequence

        stdseq -- standar sequence(might be gaps contained)

        pattern -- pattern object, see pm.pattern

        length -- length of pairwised seq and stdseq

        gaps -- nucleotide gaps number

        nt_pm -- nucleotide mutation amout

        aa_pm -- amino mutation amount. If in a translating model, 
                 aa_pm will be an valid int, else None

        """

        self.seq = seq
        self.stdseq = stdseq
        self.length = length
        self.pattern = pattern
        self.gaps = gaps
        self.nt_pm = nt_pm
        self.aa_pm = aa_pm
        self.score = self._score()
        self._cached_non_gaps_stdseq = None

    def __str__(self):
        """Convert to string."""

        return self.__status__

    def _score(self):
        """Calculate score of this status"""

        gap = 1 if self.gaps > 0 else 0
        aa_pm = MAX_BASE if self.aa_pm is None else self.aa_pm
        score = SCORE_MATIX[self.__status__] \
                + SCORE_MATIX['gaps'] * gap \
                + SCORE_MATIX['nt_pm'] * self.nt_pm / MAX_BASE \
                + SCORE_MATIX['aa_pm'] * aa_pm / MAX_BASE
        return score

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented

        return self.score == other.score

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented

        return self.score < other.score

    def __le__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented

        return self.score <= other.score

    def __gt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented

        return self.score > other.score

    def __ge__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented

        return self.score >= other.score

    def get_stdseq_without_gaps(self):
        """Removes gaps from self.stdseq and caches it"""
        if self._cached_non_gaps_stdseq is None \
                and self.stdseq is not None:
            self._cached_non_gaps_stdseq = self.stdseq.replace(
                    '-', '').upper()
        return self._cached_non_gaps_stdseq

    def _is_valid_operand(self, other):
        """Check"""

        if isinstance(other, NA):
            if other.get_stdseq_without_gaps() != \
                    self.get_stdseq_without_gaps():
                raise TypeError("unorderable when stdseqs are inconsistent.")
            return True

        return False

    def __repr__(self):
        if self.stdseq is not None and len(self.stdseq) > 60:
            s = self.stdseq[0:27] + "..." + self.stdseq[-27:]
        else:
            s = self.seq
        return "<pm.status.{} object with: gaps={}, nt_pm={}, aa_pm={}, " \
               "stdseq='{}'>".format(self.__status__, self.gaps, 
                                  self.nt_pm, self.aa_pm, s)


class Y(NA):
    
    __status__ = "Y"


class Conserved(NA):
    
    __status__ = "Conserved"

    def __init__(self, *args, **kwargs):
        super(Conserved, self).__init__(*args, **kwargs)
        assert self.aa_pm == 0, "aa_pm > 0 in Conserved."


class PM(NA):
    
    __status__ = "PM"
