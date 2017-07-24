def filter_seq_without_none(seqs):
    """filter out all sequences in `seqs` which contain at least one
    `None` value."""
    return (seq for seq in seqs if None not in seq)


def slice_with_default(seq, start, stop=None, step=1, default=None):
    '''Works like slicing with slice syntax, except that a default value
    is appended to the returned tuple in case of negative indices or
    indices outside the range.

    '''
    ret = []
    if stop is None:
        stop = len(seq)
    for i in range(start, stop, step):
        if i < 0 or i >= len(seq):
            ret.append(default)
        else:
            ret.append(seq[i])
    return tuple(ret)


def seq_to_string(seq):
    s = ''
    for c in seq:
        if c is not None:
            s += c
    return s
