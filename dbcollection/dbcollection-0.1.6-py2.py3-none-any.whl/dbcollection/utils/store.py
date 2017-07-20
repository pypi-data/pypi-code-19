"""
Utility functions to store data in a hdf5.
"""

import numpy as np

def hdf5_save_list_chunks(handler, field_name, data, val=-1):
    """
    Store a list into a hdf5 file in a chunked way
    """
    nrows = len(data)
    ncols = max([len(l) for l in data])
    dset = handler.create_dataset(field_name,
                                  (nrows, ncols),
                                  dtype=np.float,
                                  chunks=True,
                                  fillvalue=val)
    for i in range(nrows):
        dset[i] = data[i]
