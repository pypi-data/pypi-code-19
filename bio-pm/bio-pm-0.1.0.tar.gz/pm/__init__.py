# -*- coding: utf-8 -*-
"""
Analyze PM status for nucleotide sequence.

Functions:
analyze

Exception:

TranslationError
Raise when invalid codon found in seq or stdseq in translation model.
Referenced from pm.status.

"""


from .pattern import parse, TranslationError
from .status import Y, Conserved, PM, NA


def analyze(seq, stdseq, translate=True):
    """Analyze the PM between pairwised seq and stdseq.

    Analyze the consistence of nucleotide base between a sequence and it's
    global pairwised stdandar sequence. Calculate out their PM status and 
    mutation pattern.

    Return point mutation object: Y/Convered/PM/NA.

    Args:
    seq -- nucleotide sequence

    stdseq -- glable pairwised standard sequence of seq

    translate -- open translate model, default True.
                 If translate is true, the aligned clones with non-triple 
                 pairwised sequence, produced by blastn, of query(in seqfa) 
                 will be omit. The returned status would be Y/Conserved/PM/NA
                 status object of which aa_pm is not None.

                 If translate is false, any aligned clone meet the filtering 
                 requirement of the `filterfn` will be included. The returned
                 status object would be Y/NA of which aa_pm is None.

    """
        
    length = len(seq)
    if length != len(stdseq):
        raise ValueError("inconsistent length between seq and stdseq")
    pattern = parse(seq, stdseq, translate=translate)
    gaps, nt_pm = 0, 0
    for stdv, v in pattern.mutants.values():
        assert stdv != v, \
            "invalid pattern: consistent base exist in both stdseq and seq."
        if stdv == '-' or v == '-':
            gaps += 1
        else:
            nt_pm += 1
    assert gaps == stdseq.count("-") + seq.count("-"), \
            "inconsistent gaps number between sequence and pattern."

    aa_pm = len([None for stdv, v in pattern.aa_mutants.values() if stdv != v \
                    and stdv != '-' and v != '-']) if translate else None

    if gaps > 0:
        return NA(seq, stdseq, pattern=pattern, length=length, 
                  gaps=gaps, nt_pm=nt_pm, aa_pm=aa_pm)
    if nt_pm == 0:
        return Y(seq, stdseq, pattern=pattern, length=length, 
                 gaps=gaps, nt_pm=nt_pm, aa_pm=aa_pm)
    if not translate:
        return NA(seq, stdseq, pattern=pattern, length=length, 
                  gaps=gaps, nt_pm=nt_pm, aa_pm=aa_pm)
    if aa_pm == 0:
        return Conserved(seq, stdseq, pattern=pattern, length=length, 
                         gaps=gaps, nt_pm=nt_pm, aa_pm=aa_pm)
    else:
        return PM(seq, stdseq, pattern=pattern, length=length, 
                  gaps=gaps, nt_pm=nt_pm, aa_pm=aa_pm)

__all__ = (analyze, TranslationError, )
