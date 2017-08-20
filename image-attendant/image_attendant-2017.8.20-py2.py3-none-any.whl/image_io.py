from __future__ import division, print_function, unicode_literals, absolute_import

import os
import io
import urllib

import numpy as np
import PIL.Image
import requests


def read(fp):
    """Read image data from file-like object using PIL.  Return Numpy array.
    """
    with open(fp, 'rb') as fpp:
        img = PIL.Image.open(fpp)
        data = np.asarray(img)

    return data



def write(fp, data, fmt=None, **kwargs):
    """Write image data from Numpy array to file-like object.

    File format is automatically determined from fp if it's a filename, otherwise you
    must specify format via fmt keyword, e.g. fmt = 'png'.

    Parameter options: http://pillow.readthedocs.org/handbook/image-file-formats.html
    """
    img = PIL.Image.fromarray(data)
    img.save(fp, format=fmt, **kwargs)



def normalize_url(url):
    parts = urllib.parse.urlsplit(url)
    url_nice = parts.geturl()

    return url_nice



def download(url, verbose=False):
    """Download compressed image data from URL.

    http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests/13137873#13137873
    """
    url = normalize_url(url)

    resp = requests.get(url)
    if not resp.ok:
        msg = 'Problem fetching data: {}'.format(resp.reason)
        raise requests.RequestException(msg)

    # Binary compressed image data from response content.
    data_comp = resp.content

    # Compression format, e.g. 'image/jpeg' --> 'jpeg'
    fmt = resp.headers['content-type'].split('/')[1]

    return data_comp, fmt

#------------------------------------------------

if __name__ == '__main__':
    pass
