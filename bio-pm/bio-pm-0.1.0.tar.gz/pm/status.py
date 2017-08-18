# -*- coding: utf-8 -*-
"""
PM status data structure module.

Provides a orderable data structure for point mutation status. 
e.g. Y > Conserved is True; Y(aa_pm=0) > Y(aa_pm=None) is True.

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

        stdseq -- pairwised standar sequence of seq

        pattern -- pattern object

        length --

        gaps --

        nt_pm --

        aa_pm -- amino mutation amount. If in a translating model, 
                 aa_pm will be an valid int, else None

        """

        self.pairwised_seq = seq
        self.pairwised_stdseq = stdseq
        self.seq = None if seq is None else seq.replace('-', '')
        self.stdseq = None if stdseq is None else stdseq.replace('-', '')
        self.length = length
        self.pattern = pattern
        self.gaps = gaps
        self.nt_pm = nt_pm
        self.aa_pm = aa_pm
        self.score = self._score()

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

    def _is_valid_operand(self, other):
        """Check"""

        if isinstance(other, NA):
            std = None if self.stdseq is None else self.stdseq.upper()
            other_std = None if other.stdseq is None else other.stdseq.upper()
            if other_std != std:
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
