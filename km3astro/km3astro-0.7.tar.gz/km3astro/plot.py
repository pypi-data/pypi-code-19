"""Plotting utilities.
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import astropy.coordinates as coord
from astropy.units import degree


def ra_dec(skycoord):
    """Take (ra, dec) from skycoord in matplotlib-firendly format.

    This wraps the ra because astropy's convention differs from matplotlib.
    """
    ra = skycoord.ra.wrap_at(180 * degree).radian
    dec = skycoord.dec.radian
    return ra, dec


def projection_axes(projection='aitoff', **figargs):
    fig = plt.figure(**figargs)
    ax = fig.add_subplot(111, projection=projection)
    ax.grid(color='lightgrey')
    return ax
