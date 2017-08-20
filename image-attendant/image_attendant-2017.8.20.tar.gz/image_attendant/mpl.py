from __future__ import division, print_function, unicode_literals, absolute_import

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.backends.backend_agg import FigureCanvasAgg

from .utility import image_data_mode, setup_uint8
from .compression import compress


def figure_to_image(fig, fmt='raw', dpi=None):
    """Generate compressed-image representation of a Matplotlib figure.
    Nothing gets displayed to the screen.

    See here for partial inspiration: https://gist.github.com/rduplain/1641344
    """

    if dpi:
        dpi_original = fig.get_dpi()
        fig.set_dpi(dpi)

    # Render figure to buffer as uncompressed RGBA
    canvas = FigureCanvasAgg(fig)
    buff, (num_samples, num_lines) = canvas.print_to_buffer()
    num_colors = 4

    data = np.frombuffer(buff, dtype=np.uint8)
    data.shape = num_lines, num_samples, num_colors

    mode = image_data_mode(data)
    if mode.lower() != 'rgba':
        raise ValueError('Unexpected image mode: {:s}'.format(mode))

    if dpi:
        fig.set_dpi(dpi_original)

    if mode == 'raw':
        # Raw data
        return data
    else:
        # Compress
        data_comp = compress(data, mode=mode, fmt=fmt)
        return data_comp



def figure_to_file(fig, fname, fmt='png', dpi=None):
    """Write selected figure to image file
    """
    b, e = os.path.splitext(fname)

    if fmt:
        e = '.' + fmt.lower()
    else:
        fmt = e[1:].lower()

    f_out = b + e

    data_comp = figure_to_image(fig, fmt=fmt, dpi=dpi)

    with open(f_out, 'wb') as fp:
        fp.write(data_comp)

#------------------------------------------------

if __name__ == '__main__':
    pass

