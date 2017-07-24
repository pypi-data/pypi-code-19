# -*- coding: utf-8 -*-
"""
========
utility
========

This module contains useful utility functions, decorators, and plotting helpers
that are useful throughout the ``kpfm`` package.

**Should my function go here?**
If you find yourself wanting it in many IPython notebooks, yes!
Just add a docstring and make sure the function is useful on its own
(not dependent on any external data, doesn't make assumptions that limit
broader usefulness of the code).
"""

from __future__ import division, print_function, absolute_import
import io
import os
import errno
import six
import h5py
import scipy
from distutils.version import LooseVersion
from decorator import decorator

# Fix errors on readthedocs by defining a dummy version of
# next_fast_len if scipy is "mocked" (see docs/conf.py)
try:
    if LooseVersion(scipy.__version__) > LooseVersion("0.18"):
        from scipy import fftpack
        next_fast_len = fftpack.next_fast_len
    else:
        from scipy.signal import signaltools
        next_fast_len = signaltools._next_regular
except TypeError:
    def next_fast_len(x):
        return x





def silent_remove(filename):
    """If ``filename`` exists, delete it. Otherwise, return nothing.
       See http://stackoverflow.com/q/10840533/2823213."""
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occured


def align_labels(axes_list, lim, axis='y'):
    """Align matplotlib axis labels to the same horizontal (y-axis)
    or vertical (x-axis) position.
    """
    for ax in axes_list:
        if axis == 'y':
            t = ax.yaxis.label.get_transform()
            x,y = ax.yaxis.label.get_position()
            ax.yaxis.set_label_coords(lim, y, t)
        else:
            t = ax.xaxis.label.get_transform()
            x,y = ax.xaxis.label.get_position()
            ax.xaxis.set_label_coords(x, lim, t)


def color2gray(x):
    """Convert an RGB or RGBA (Red Green Blue Alpha) color tuple
       to a grayscale value."""
    if len(x) == 3:
        r, g, b = x
        a = 1
    elif len(x) == 4:
        r, g, b, a = x
    else:
        raise ValueError("Incorrect tuple length")
    return (r * 0.299 + 0.587*g + 0.114*b) * a

@decorator
def txt_filename(f, fname_or_fh, *args, **kwargs):
    """Decorator to allow seamless use of filenames rather than
    file handles for functions that operate on a text file.

    Usage
    ----- 
    To use this decorator, write the function to take a file object
    as the function's first argument."""
    if isinstance(fname_or_fh, six.string_types):
        with io.open(fname_or_fh, 'r') as fh:
            return f(fh, *args, **kwargs)
    else:
        return f(fname_or_fh, *args, **kwargs)

@decorator
def h5filename(f, fname_or_fh, *args, **kwargs):
    """Decorator to allow seamless use of filenames rather than
    file handles for functions that operate on an HDF5 file.

    Usage
    ----- 
    To use this decorator, write the function to take an HDF5 file handle as
    the function's first argument.

    Example: We create a simple function and HDF5 file.

    >>> @h5filename
    >>> def h5print(fh):
    >>>     print(fh.values())
    >>>
    >>> fh = h5py.File('test.h5')
    >>> fh['x'] = 2

    We can call the function on the file handle

    >>> h5print(fh)
    [<HDF5 dataset "x": shape (), type "<i8">]
    
    or call the function on the filename

    >>> fh.close()
    >>> h5print('test.h5')
    [<HDF5 dataset "x": shape (), type "<i8">]

    """
    if isinstance(fname_or_fh, six.string_types):
        with h5py.File(fname_or_fh, 'r') as fh:
            return f(fh, *args, **kwargs)
    else:
        return f(fname_or_fh, *args, **kwargs)


def h5ls_str(g, offset='', print_types=True):
    """Prints the input file/group/dataset (g) name and begin iterations on its
    content.
    
    See goo.gl/2JiUQK."""
    string = []
    if isinstance(g, h5py.File):
        string.append(offset+repr(g.file))
    elif isinstance(g, h5py.Dataset):
        if print_types:
            string.append(offset+g.name+'  '+repr(g.shape)+'  '+(g.dtype.str))
        else:
            string.append(offset+g.name+'  '+repr(g.shape))
    elif isinstance(g, h5py.Group):
        string.append(offset+g.name)
    else:
        raise ValueError('WARNING: UNKNOWN ITEM IN HDF5 FILE'+g.name)
    if isinstance(g, h5py.File) or isinstance(g, h5py.Group):
        for key, subg in dict(g).items():
            string.append(h5ls_str(subg, offset + '    ',
                                   print_types=print_types))
    return "\n".join(string)


def h5ls(*args):
    """List the contents of an HDF5 file object or group.
    Accepts a file / group handle, or a string interpreted as the hdf5
    file path."""
    for arg in args:
        if isinstance(arg, six.string_types):
            fh = h5py.File(arg, mode='r')
            print(h5ls_str(fh))
            fh.close()
        else:
            print(h5ls_str(arg))


def prnDict(aDict, br='\n', html=0,
            keyAlign='l',   sortKey=0,
            keyPrefix='',   keySuffix='',
            valuePrefix='', valueSuffix='',
            leftMargin=4,   indent=1, braces=True):
    '''Return a string representive of aDict in the following format::
    
    {
     key1: value1,
     key2: value2,
     ...
     }

Spaces will be added to the keys to make them have same width.

Parameters
----------

sortKey: 0 or 1
    set to 1 if want keys sorted;
keyAlign: 
    either 'l' or 'r', for left, right align, respectively.
keyPrefix, keySuffix, valuePrefix, valueSuffix: string
    The prefix and suffix to wrap the keys or values. Good for formatting
    them for html document (for example, keyPrefix='<b>', keySuffix='</b>').
    Note: The keys will be padded with spaces to have them equally-wide.
    The pre- and suffix will be added OUTSIDE the entire width.
html: 0 or 1
    If set to 1, all spaces will be replaced with '&nbsp;', and
    the entire output will be wrapped with '<code>' and '</code>'.
br: string
    Determine the carriage return. If html, it is suggested to set
    br to '<br>'. If you want the html source code easy to read,
    set br to ``'<br>\n'``.


References
----------

version: 04b52
author : Runsun Pan
require: odict() # an ordered dict, if you want the keys sorted.
         Dave Benjamin 
         http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/161403'''
   
    if aDict:

        #------------------------------ sort key
        if sortKey:
            dic = aDict.copy()
            keys = dic.keys()
            keys.sort()
            aDict = OrderedDict()
            for k in keys:
                aDict[k] = dic[k]

        #------------------- wrap keys with ' ' (quotes) if str
        tmp = ['{']
        ks = [type(x)==str and "'%s'"%x or x for x in aDict.keys()]

        #------------------- wrap values with ' ' (quotes) if str
        vs = [type(x)==str and "'%s'"%x or x for x in aDict.values()] 

        maxKeyLen = max([len(str(x)) for x in ks])

        for i in range(len(ks)):

            #-------------------------- Adjust key width
            k = {1            : str(ks[i]).ljust(maxKeyLen),
                 keyAlign=='r': str(ks[i]).rjust(maxKeyLen) }[1]

            v = vs[i]
            tmp.append(' '* indent+ '%s%s%s:%s%s%s,' %(
                        keyPrefix, k, keySuffix,
                        valuePrefix,v,valueSuffix))

        tmp[-1] = tmp[-1][:-1] # remove the ',' in the last item
        tmp.append('}')

        if leftMargin:
          tmp = [ ' '*leftMargin + x for x in tmp ]

        if not braces:
            tmp = tmp[5:-2]

        if html:
            return '<code>%s</code>' %br.join(tmp).replace(' ','&nbsp;')
        else:
            return br.join(tmp)
    else:
        return '{}'

from kpfm.util.readtxt import kpfm_data