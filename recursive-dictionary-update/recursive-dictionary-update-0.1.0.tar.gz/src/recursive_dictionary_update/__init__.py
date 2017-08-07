import collections


__version__ = "0.1.0"


def update(d, u):
    """
    Recursively update a nested dictionary.

    Original code from https://stackoverflow.com/a/3233356/1950432.
    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d
