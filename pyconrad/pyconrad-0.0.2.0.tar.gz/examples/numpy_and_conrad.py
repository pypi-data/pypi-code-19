
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

from pyconrad import PyConrad, PyGrid, java_float_dtype
import numpy as np

pyconrad = PyConrad()
pyconrad.setup()

phantom = pyconrad.get_phantom_package().MickeyMouseGrid2D(200,200)

# Create PyGrid from Grid2D
pygrid1 = PyGrid.from_grid(phantom)
# use Java method
pygrid1.grid().show()
# use Python method
from scipy.misc import imshow
imshow(pygrid1.numpy()) # or imshow(pygrid1)

# Create PyGrid from numpy array (must be of type pyconrad.java_float_dtype)
array = np.random.rand(4,2,3).astype(java_float_dtype)
pygrid2 = PyGrid.from_numpy(array)

# Manipulate data in using CONRAD at Position (x,y,z) = (1,2,4)
pygrid2.grid().setValue(5.0, [0,1,3])

# Print this pixel using Python indexes [z,y,x]
print("Before update: %f" % pygrid2[3,1,0])
# Python data must be synchronized with CONRAD
pygrid2.update_numpy()
print("After update: %f" % pygrid2[3,1,0])

# Manipulate pixel using python
pygrid2[1,1,1] = 3.0
# Update CONRAD data
pygrid2.update_grid()

# Print
print(pygrid2)

