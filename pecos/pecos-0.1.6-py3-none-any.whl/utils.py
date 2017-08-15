"""
The utils module contains helper functions.
"""
import pandas as pd
import numpy as np
from pandas.tseries.frequencies import to_offset
import logging
import os

logger = logging.getLogger(__name__)
        
def round_index(dt, frequency, how='nearest'):
    """
    Round datetime index.
    
    Parameters
    ----------
    dt : DatetimeIndex
        Time series index
    
    frequency : int
        Expected time series frequency, in seconds
    
    how : string (optional)
        Method for rounding, default = 'nearest'.  Options include:
        
        - nearest = round the index to the nearest expected integer
        - floor= round the index to the largest expected integer such that the integer <= index
        - ceiling = round the index to the smallest expected integer such that the integer >= index
        
    Returns
    -------
    rounded _dt : DatetimeIndex
        Rounded time series index
    """
    freq=str(frequency) + 's'
    freq = to_offset(freq).nanos
    
    if how=='nearest':
        rounded_dt = pd.DatetimeIndex(((np.round(dt.asi8/(float(freq)))*freq).astype(np.int64)))
    elif how=='floor':
        rounded_dt = pd.DatetimeIndex(((np.floor(dt.asi8/(float(freq)))*freq).astype(np.int64)))
    elif how=='ceiling':
        rounded_dt = pd.DatetimeIndex(((np.ceil(dt.asi8/(float(freq)))*freq).astype(np.int64)))
    else:
        logger.info("Invalid input, index not rounded")
        rounded_dt = dt

    return rounded_dt

def convert_html_to_image(html_filename, image_filename, image_format='png', quality=100, zoom=1):
    """
    Convert html file to image file using wkhtmltoimage.
    See http://wkhtmltopdf.org/ for more information.
    
    Parameters
    ----------
    html_filename : string
        HTML file name, with full path
    
    image_filename : string
        Image file name, with full path
    
    image_format : string  (optional)
        Image format, default = 'png'
    
    quality : int (optional)
        Image quality, default = 100
    
    zoom : int (optional)
        Zoom factor, default = 1
    """
    os.system('wkhtmltoimage --format ' + image_format + 
                           ' --quality ' + str(quality) + 
                           ' --zoom ' + str(zoom) + ' ' + 
                            html_filename + ' ' + image_filename)