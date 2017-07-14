# -*- coding: utf-8 -*-
"""
This module contains all functions that handle 
- (base) sequence generation,
- quality score generation.

"""
import os
import numpy as np
from numba import njit, int64, float64


BASES = np.array([65, 67, 71, 84], dtype=np.uint8)

def random_seq(length, p=None, excluded_motif=None,
      _BASES=BASES, _choice=np.random.choice):
    """
    Create a random sequence of given length from ACGT with given probabilities p.
    Use p=None for the uniform distribution.
    Use a single float (e.g. 0.5) to specify a GC-content (0.5 is equivalent to uniform).
    Use a numpy float64 array of length 4 to specify an arbitrary distribution.

    Optionally, ensure that the sequence does not contain a given excluded motif.
    Specify excluded_motif=None (default) if no motif exclusion is desired.
    NOTE: Specifying a short (frequent) motif for exclusion may lead to long running times!

    Return a bytes object with the nucleotide sequence (from b'ACGT')
    that does not contain the excluded motif.
    """
    if isinstance(p, float): 
        p = get_p_from_gc_content(p)
    # now p is either None or an np.ndarray of size 4
    seq = _choice(_BASES, length, p=p).tobytes()
    if excluded_motif is None:
        return seq
    motiflength = len(excluded_motif)
    while True:
        if excluded_motif not in seq:
            return seq
        newpart = _choice(_BASES, motiflength, p=p).tobytes()
        seq = seq.replace(excluded_motif, newpart)


def get_p_from_gc_content(gc_content):
    """
    return None if p=0.5, 
    or otherwise an np.array with four probabilities for ACGT
    """
    if gc_content == 0.5:
        p = None  # optimize uniform case
    else:
        pcg = gc_content / 2.0
        pat = 0.5 - pcg
        p = np.array([pat, pcg, pcg, pat], dtype=np.double)
    return p



class QualityModel:

    def __init__(self, path, read_length):
        """
        read model from given path on disk,
        this should be a text file with matrix of size `|qualityvalues| x 100`
        containing one quality distribution per column,
        i.e., column j corresponds to read position j.
        """
        # initialize quality_profile by reading it from disk;
        # Adjust it later to a matrix of dimensions readlength x |qualityvalues|,
        # such that row i contains quality distribution at read position i.
        profile = np.loadtxt(path).T
        # find the first row that does not sum to 1;
        # the row before is the last valid probability vector!
        plength = len(profile)
        for pos, probs in enumerate(profile):
            if not np.isclose(np.sum(probs), 1.0):
                plength = pos                
                break
        # store the last valid row (if it exists)
        if plength == 0:
            raise RuntimeError("ERROR: quality model '{}' doesn't contain probabilities in first column".format(path))
        profile = profile[:plength,:]
        if plength > read_length:
            # trim model down to read length
            profile = profile[:read_length,:]
        elif plength < read_length:
            # fill missing positions with last model
            last = profile[plength-1,:]
            profile = np.vstack( (profile, np.tile(last, (read_length-plength, 1))) )
        assert profile.shape[0] == read_length, (profile.shape[0], read_length)
        self.cumprofile = np.cumsum(profile, axis=1)
        # prepare quality values to choose from: 33, 34, ...
        # this is an implicit PHRED -> Sanger conversion
        qnumber = len(profile[0])
        self.values = np.arange(33, 33+qnumber, dtype=np.int8)


    def get_quality_values(self):
        """return bytes with printable quality values"""
        plength = self.cumprofile.shape[0]
        u = np.random.rand(plength)  # random numbers
        ##print("Generating {} random numbers".format(plength))
        qualities = np.zeros(plength, dtype=np.uint8)
        _find_quality_values(u, self.cumprofile, self.values, qualities)
        return qualities.tobytes()


@njit(locals=dict(m=int64, n=int64, pos=int64, q=int64, x=float64))
def _find_quality_values(u, cumprofile, values, outbuffer):
    m = len(u)
    n = len(values)
    for pos in range(m):
        x = u[pos]
        for q in range(n):
            if cumprofile[pos,q] >= x:
                break
        outbuffer[pos] = values[q]


# global interface to quality generation
def initialize_quality_model(path, read_length):
    global _QUALITY_MODEL
    if os.path.exists(path):
        _QUALITY_MODEL = QualityModel(path, read_length)
    elif path in ("L100-Q70", "L101-Q70", "L110-Q70"):
        quality_model_path = os.path.join(os.path.dirname(__file__), "quality_profiles")
        _QUALITY_MODEL = QualityModel(os.path.join(quality_model_path, "{}.qmodel".format(path)), read_length)
    else:
        raise ValueError("Invalid quality model. The quality model has to be either a predefined model ('L100-Q70', 'L101-Q70', 'L110-Q70') or a path to a .qmodel file.")

def generate_qualities():
    return _QUALITY_MODEL.get_quality_values()

