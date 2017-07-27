import re
import os.path as osp
import six
import inspect
from docrep import DocstringProcessor


docstrings = DocstringProcessor()


def dir_contains(dirname, path, exists=True):
    """Check if a file of directory is contained in another.

    Parameters
    ----------
    dirname: str
        The base directory that should contain `path`
    path: str
        The name of a directory or file that should be in `dirname`
    exists: bool
        If True, the `path` and `dirname` must exist

    Notes
    -----
    `path` and `dirname` must be either both absolute or both relative
    paths"""
    if exists:
        dirname = osp.abspath(dirname)
        path = osp.abspath(path)
        if six.PY2 or six.PY34:
            return osp.exists(path) and osp.samefile(
                osp.commonprefix([dirname, path]), dirname)
        else:
            return osp.samefile(osp.commonpath([dirname, path]), dirname)
    return dirname in osp.commonprefix([dirname, path])


def isstring(s):
    return isinstance(s, six.string_types)


def get_next_name(old, fmt='%i'):
    """Return the next name that numerically follows `old`"""
    nums = re.findall('\d+', old)
    if not nums:
        raise ValueError("Could not get the next name because the old name "
                         "has no numbers in it")
    num0 = nums[-1]
    num1 = str(int(num0) + 1)
    return old[::-1].replace(num0[::-1], num1[::-1], 1)[::-1]


docstrings.params['get_value_note'] = """
    If the key goes some
    levels deeper, keys may be separated by a ``'.'`` (e.g.
    ``'namelists.weathergen'``). Hence, to insert a ``','``, it must
    be escaped by a preceeding ``'\'``."""


@docstrings.dedent
def go_through_dict(key, d, setdefault=None):
    """
    Split up the `key` by . and get the value from the base dictionary `d`

    Parameters
    ----------
    key: str
        The key in the `config` configuration. %(get_value_note)s
    d: dict
        The configuration dictionary containing the key
    setdefault: callable
        If not None and an item is not existent in `d`, it is created by
        calling the given function

    Returns
    -------
    str
        The last level of the key
    dict
        The dictionary in `d` that contains the last level of the key
    """
    patt = re.compile(r'(?<!\\)\.')
    sub_d = d
    splitted = patt.split(key)
    n = len(splitted)
    for i, k in enumerate(splitted):
        if i < n - 1:
            if setdefault is not None:
                sub_d = sub_d.setdefault(k, setdefault())
            else:
                sub_d = sub_d[k]
        else:
            return k, sub_d


def get_module_path(mod):
    """Convenience method to get the directory of a given python module"""
    return osp.dirname(inspect.getabsfile(mod))


def get_toplevel_module(mod):
    return mod.__name__.split('.')[0]


def safe_list(l):
    """
    Function to create a list

    Parameters
    ----------
    l: iterable or anything else
        Parameter that shall be converted to a list.

        - If string or any non-iterable, it will be put into a list
        - if iterable, it will be converted to a list

    Returns
    -------
    list
        `l` put (or converted) into a list"""
    if isstring(l):
        return [l]
    try:
        return list(l)
    except TypeError:
        return [l]
