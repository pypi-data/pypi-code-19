try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


def grouper(n, iterable, fillvalue=None):
    """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx."""
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def wrapit(arg, iterator=list, exclude_iterators=None):
    """Wrap an argument in the specified iterator.
    
    This function is useful in functions for converting arguments into a list
    or some other iterator type.
    
    Parameters
    ----------
    arg:
        The argument to wrap.
    iterator:
        The type of iterator to return.
    exclude_iterators
        A list of iterators to exclude when determining whether the arg is
        an iterator.
        
    Returns
    -------
    wrapped_arg or None
        Returned the arg wrapped in an iterator of type 'iterator'.
        If arg is None, then None is returned.
        
    Examples
    --------
    >>> wrapit('tester')
    ['tester']
    >>> wrapit(1, iterator=tuple)
    (1,)
    >>> wrapit(None)
    >>> wrapit({'a': 1}, exclude_iterators=[dict,])
    [{'a': 1}]
    >>> wrapit({'a': 1})
    ['a']
    """
    if arg is None:
        return None
    elif isinstance(arg, iterator):
        return arg
    elif (exclude_iterators is not None and
          any([isinstance(arg, t) for t in exclude_iterators])):
        return iterator((arg, ))
    elif hasattr(arg, '__iter__') and not isinstance(arg, str):
        return iterator(arg)
    else:
        return iterator((arg, ))
