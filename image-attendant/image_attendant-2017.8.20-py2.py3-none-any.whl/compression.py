from __future__ import division, print_function, unicode_literals, absolute_import

import io

import numpy as np

from . import image_io
from . import utility


def compress(data, fmt, **kwargs):
    """Compress image, return data buffer.

    fmt: 'png', 'jpeg', etc.

    Alpha channel will be ignored if fmt == 'jpeg'.

    Returns a byte buffer of compressed data.

    Parameter options: http://pillow.readthedocs.org/handbook/image-file-formats.html
    """
    # Enforce 8-byte data
    data = setup_uint8(data)

    fmt = fmt.lower()
    if fmt == 'jpg':
        fmt = 'jpeg'

    if fmt == 'jpeg':
        if data.ndim == 3:
            if data.shape[2] == 4:
                # Discard alpha channel for JPEG compression.
                data = data[:, :, :2]

    buff = io.BytesIO()
    image_io.write(buff, data, fmt, **kwargs)

    data_comp = buff.getvalue()

    return data_comp



def decompress(data_comp):
    """Decompress image from supplied byte data.
    """
    buff = io.BytesIO(data_comp)
    img = PIL.Image.open(buff)

    data = np.asarray(img)

    return data

#------------------------------------------------

if __name__ == '__main__':
    pass
