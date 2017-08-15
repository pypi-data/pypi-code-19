"""
Utility functions to read paramagnetic data.
"""
import gzip
from collections import OrderedDict

from .data_types import PRE
from mollib.utils.data_readers import read_data_string


def read_pre_file(filename):
    """Read data from a partial alignment data file.

    Parameters
    ----------
    filename: str
        The filename to read the data from. The file can be a text file or a 
        gzipped file.
    """
    data = OrderedDict()

    # Read in the filename to a string
    if filename.endswith('.gz'):
        with gzip.open(filename) as f:
            string = f.read()
    else:
        with open(filename) as f:
            string = f.read()

    # Convert the string, if it's in bytes, to a text string. This is needed
    # for Python 3 compatibility.
    if type(string) == bytes:
        string = string.decode('latin-1')

    return read_data_string(string=string, one_atom_cls=PRE)
