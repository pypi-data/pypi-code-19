import collections


def flatten(l):
    """
    Flatten a list of lists, even if they are irregular.

    Original Code from https://stackoverflow.com/a/2158532/1950432
    """
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el
