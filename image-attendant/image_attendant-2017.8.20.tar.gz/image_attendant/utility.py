from __future__ import division, print_function, unicode_literals, absolute_import

import numpy as np


def image_data_mode(data):
    """Determine image color mode compatible with PIL / Pillow
    Input data is expected to be 2D or 3D: [num_lines, num_samples, num_bands].
    """
    # Force data to be Numpy ndarray, if not already.
    data = np.asarray(data)

    if data.ndim == 2:
        num_bands = 1
    elif data.ndim == 3:
        num_bands = data.shape[2]
    else:
        raise ValueError('Invalid number of data dimensions: {}'.format(data.ndim))

    if num_bands == 1:
        mode = 'L'
    elif num_bands == 3:
        mode = 'RGB'
    elif num_bands == 4:
        mode = 'RGBA'
    else:
        raise ValueError('Invalid number of bands.')

    return mode



def setup_uint8(data, lohi=None):
    """Ensure data is unsigned bytes

    If data type is not np.uint8 it will be converted by scaling
    min(data) -> 0 and max(data) -> 255.
    """
    data = np.asarray(data)

    # Scale to np.uint8?
    if not (data.dtype == np.uint8) or lohi is not None:
        data = data.astype(np.float32)

        if lohi is None:
            lohi = data.min(), data.max()

        lo, hi = lohi
        if lo == hi:
            raise ValueError('Invalid data range: {}, {}'.format(lo, hi))

        data = (data - lo) / (hi - lo)
        data = np.clip(data, 0, 1)*255
        data = np.round(data).astype(np.uint8)

    return data



def collapse_alpha(data_rgba):
    """Collapse alpha channel

    https://en.wikipedia.org/wiki/Alpha_compositing#Alpha_blending
    """
    data_rgba = np.asarray(data_rgba)

    if data_rgba.dtype != np.uint8:
        # Nothing to do
        return data_rgba

    if data_rgba.ndim != 3:
        # Nothing to do
        return data_rgba

    if data_rgba.shape[2] != 4:
        # Nothing to do
        return data_rgba

    # Convert to float, between 0 and 1.
    data_rgba = data_rgba.astype(np.float32)/255

    data_src = data_rgba[:, :, :3]
    alpha_src = data_rgba[:, :, 3]

    data_bkg = 1
    data_rgb = data_src*alpha_src + data_bkg*(1 - alpha_src)

    data_rgb = np.clip(data_rgb, 0, 1)*255
    data_rgb = np.round(data_rgb).astype(np.uint8)

    # Done
    return data_rgb



def data_url(data_comp, fmt):
    """Assemble compressed image data into URL data string
    """
    data_encode = base64.b64encode(data_comp)

    encoding = 'utf-8'
    template = 'data:image/{:s};charset={};base64,{:s}'

    # The decoding step here is necesary since we need to interpret byte data as text.
    # See this link for a nice explanation:
    # http://stackoverflow.com/questions/14010551/how-to-convert-between-bytes-and-strings-in-python-3
    result = template.format(fmt, encoding, data_encode.decode(encoding=encoding))

    return result



def iter_tiles(img, size):
    """Generator over image tiles
    """

    num_lines, num_samples = img.shape[:2]

    num_chunk_lines = int(num_lines/size)
    chunk_lines = int(np.round(num_lines/num_chunk_lines))
    chunk_lines -= chunk_lines % 2

    num_chunk_samples = int(num_samples/size)
    chunk_samples = int(np.round(num_samples/num_chunk_samples))
    chunk_samples -= chunk_samples % 2

    for j in range(num_chunk_lines):
        j0 = j*chunk_lines
        slice_lines = slice(j0, j0 + chunk_lines)
        for i in range(num_chunk_samples):
            i0 = i*chunk_samples
            slice_samples = slice(i0, i0 + chunk_samples)

            yield img[slice_lines, slice_samples], j0, i0


#------------------------------------------------

if __name__ == '__main__':
    pass
