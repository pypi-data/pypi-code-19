"""
ensures data is what we assert it to be
"""


class NonConformantRowLengths(Exception):
    """nested arrays have different lengths"""

    _msg_tmpl = "Different lengths to array_mean: {}"

    def __init__(self, lengths):
        self.lengths = lengths
        Exception.__init__(self,
                           self._msg_tmpl.format(' '.join([str(l) for l in lengths])))

def ensure_row_length(data):
    """
    ensures that all rows of array `data` are the same
    If so, return that length.
    If not, raise NonConformantArrayLengths
    """
    lengths = set([len(i) for i in data])
    if len(lengths) != 1:
        raise NonConformantRowLengths(lengths)
    return lengths.pop()
