
# Copyright (C) 2010-2017 - Andreas Maier 
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)



import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'

from ._imageutils import ImageUtil
from ._pygrid import PyGrid
from ._pyconrad import PyConrad
from .constants import java_float_dtype
from ._pyconradfabric import *