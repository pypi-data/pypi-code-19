"""
filter functions for statistics
"""

from .conformity import ensure_row_lengths

__all__ = ['mean', 'array_mean', 'median']

def mean(data):
    """return arithemetic mean of a vector"""

    return sum(data)/float(len(data))


def array_mean(data):
    if not data:
        return []
    ensure_row_lengths(data)
    return [mean(i) for i in zip(*data)]


def median(data):
    length = len(data)
    index = length/2
    if length % 2:
        return data[index]
    else:
        return 0.5*(data[index-1] + data[index])

