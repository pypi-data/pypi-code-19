
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

from ._pyconrad import PyConrad
from ._pygrid import PyGrid

class ImageUtil:

    ###################
    ## Image Wrapper ##
    ###################

    @staticmethod
    def numpy_from_grid(grid):
        return PyGrid.from_grid(grid).numpy()

    @staticmethod
    def grid_from_numpy(array):
        return PyGrid.from_numpy(array).grid()

    #################
    ## Save Images ##
    #################

    @staticmethod
    def save_grid_as_tiff(grid, path):
        PyConrad.get_instance().classes.stanford.rsl.conrad.utils.ImageUtil.saveAs(grid, path)

    @staticmethod
    def save_numpy_as_tiff(array, path):
        grid = ImageUtil.grid_from_numpy(array)
        PyConrad.get_instance().classes.stanford.rsl.conrad.utils.ImageUtil.saveAs(grid, path)

    #################
    ## Load Images ##
    #################

    @staticmethod
    def grid_from_tiff(path):
        grid = PyConrad.get_instance().classes.stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus(PyConrad.get_instance().ij.openImage(path))
        return grid

    @staticmethod
    def array_from_tiff(path):
        grid = PyConrad.get_instance().classes.stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus(PyConrad.get_instance().ij.openImage(path))
        return ImageUtil.numpy_from_grid(grid)

