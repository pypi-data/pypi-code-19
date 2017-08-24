from pyconrad import PyGrid, PyConrad, ImageUtil
import numpy as np

PyConrad.get_instance().setup(min_ram='400M')

phantom_package = PyConrad.get_instance().classes.stanford.rsl.tutorial.phantoms
shape = [230, 330]

pygrid = PyGrid(shape)
print(pygrid)

try:
    numpyIn = np.random.rand(shape[0],shape[1]).astype(PyGrid.java_float_type())
    pygrid2 = PyGrid.from_numpy(numpyIn)

    numpyOut = ImageUtil.wrapGrid2D(pygrid2.grid())
    print(pygrid2)
    print(numpyOut)
    assert np.allclose(numpyIn,numpyOut)

    pygrid2.grid().setAtIndex(3,3, 0.4)
    pygrid2.update_numpy()
    numpyOut = ImageUtil.wrapGrid2D(pygrid2.grid())
    assert np.allclose(pygrid2.numpy(),numpyOut)
    print("Test from_numpy passed")
except Exception as ex:
    print(ex)
    print("Test from_numpy failed")

try:
    gridIn = phantom_package.MickeyMouseGrid2D(shape[1], shape[0])
    # gridIn = PyConrad.numeric_package().Grid2D(shape[1], shape[0])

    pygrid = PyGrid.from_grid(gridIn)
    pygrid[3:8,10:20] = 1.
    pygrid.update_grid()
    pygrid.show_grid()
    # numpyOut = pygrid.numpy()


    from scipy.misc import imshow
    imshow(pygrid)

    print(pygrid[1:4,5:8])
    print("Test from_grid passed")
except Exception as ex:
    print(ex)
    print("Test from_grid failed")

shape3D = [ 830, 335,542]

# try:
gridIn = phantom_package.Sphere3D(shape3D[2],shape3D[1], shape3D[0])
# gridIn = PyConrad.numeric_package().Grid2D(shape[1], shape[0])

pygrid = PyGrid.from_grid(gridIn)
# pygrid[3:8,10:20,...] = 1.
pygrid.update_grid()
pygrid.show_grid()

import matplotlib.pyplt as plt

numpyOut = pygrid.numpy()

plt.imshow( pygrid[100])



print(pygrid[1:4,5:8])
# except Exception as ex:
#     print(ex)
#     print("Test from_grid failed")

PyConrad.get_instance().terminate()
