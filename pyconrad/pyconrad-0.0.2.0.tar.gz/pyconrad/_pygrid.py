
# Copyright (C) 2010-2017 - Andreas Maier 
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

import numpy as np
import jpype
from ._pyconrad import PyConrad
from .constants import java_float_dtype

class PyGrid:

    def __init__(self, shape):
        self.__numericpackage = PyConrad.get_instance().classes.stanford.rsl.conrad.data.numeric
        if len(shape) == 1:
            self.__grid = self.__numericpackage.Grid1D(shape[0])
        elif len(shape) == 2:
            self.__grid = self.__numericpackage.Grid2D(shape[1], shape[0])
        elif len(shape) == 3:
            self.__grid = self.__numericpackage.Grid3D(shape[2], shape[1], shape[0])
        elif len(shape) == 4:
            self.__grid = self.__numericpackage.Grid4D(shape[3], shape[2], shape[1], shape[0])
        else:
            raise Exception('shape dimension not supported')
        self.__numpy = np.zeros( shape, java_float_dtype )
        if shape[0] != 0:
            self.__dbuffer = jpype.nio.convertToDirectBuffer(self.__numpy)
        self.shape = shape
        self.typestr = ">f4"
        self.__array_interface__ = { "shape": shape, "typestr": ">f4", "version" : 3, "data": self.__numpy.data}

    @staticmethod
    def from_numpy(array):
        instance = PyGrid([0,0])
        shape = array.shape
        instance.__array_interface__ = { "shape": shape, "dtype": ">f4", "version" : 3, "data":array.data}
        instance.__numpy = array
        instance.__dbuffer = jpype.nio.convertToDirectBuffer(array)
        instance.shape = array.shape

        if len(shape) == 1:
            instance.__grid = instance.__numericpackage.Grid1D(shape[0])
        elif len(shape) == 2:
            instance.__grid = instance.__numericpackage.Grid2D(shape[1], shape[0])
        elif len(shape) == 3:
            instance.__grid = instance.__numericpackage.Grid3D(shape[2], shape[1], shape[0])
        elif len(shape) == 4:
            instance.__grid = instance.__numericpackage.Grid4D(shape[3], shape[2], shape[1], shape[0])
        else:
            raise Exception('shape dimension not supported')
        instance.update_grid()
        assert array.dtype == java_float_dtype, "Numpy array must be Big Endian 32bit float! Use pyconrad.java_float_dtype!"
        return instance

    @staticmethod
    def from_grid(grid):
        instance = PyGrid([0,0])
        instance.__grid = grid
        size = list(reversed(grid.getSize()[:]))
        instance.__numpy = np.zeros(size, java_float_dtype)
        instance.__dbuffer = jpype.nio.convertToDirectBuffer(instance.__numpy)
        instance.shape = instance.__numpy.shape
        instance.__array_interface__ = { "shape": instance.shape, "typestr": ">f4", "version" : 3, "data":instance.__numpy.data}
        instance.update_numpy()
        return instance

    def grid(self):
        return self.__grid

    def numpy(self):
        return self.__numpy

    def update_numpy(self):
        assert (self.__numpy.shape == self.shape)
        shape = self.shape
        if shape[0] == 0:
            return

        fBuffer = self.__dbuffer.asFloatBuffer()
        if len(shape) == 1 or len(shape) == 2:
            fBuffer.put(self.__grid.getBuffer())
        elif len(shape) == 3:
            fBuffer = self.__dbuffer.asFloatBuffer()
            for z in range(0,shape[0]):
                subgrid = self.__grid.getSubGrid(z).getBuffer()
                fBuffer.put(subgrid) #TODO: stride == 0?

        elif len(shape) == 4:
            fBuffer = self.__dbuffer.asFloatBuffer()
            for f in range(shape[0]):
                for z in range(shape[1]):
                    fBuffer.put(self.__grid.getSubGrid(f).getSubGrid(z).getBuffer()) #TODO: stride == 0?
        else:
            raise Exception('shape dimension not supported')

    def update_grid(self):
        assert (self.__numpy.shape == self.shape)
        shape = self.shape
        if shape[0] == 0:
            return
        fBuffer = self.__dbuffer.asFloatBuffer()
        if len(shape) == 1 or len(shape) == 2:
            fBuffer.get(self.__grid.getBuffer())
        elif len(shape) == 3:
            for z in range(shape[0]):
                fBuffer.get(self.__grid.getSubGrid(z).getBuffer()) #TODO: stride == 0?
        elif len(shape) == 4:
            for f in range(shape[0]):
                for z in range(shape[1]):
                    fBuffer.get(self.__grid.getSubGrid(f).getSubGrid(z).getBuffer()) #TODO: stride == 0?
        else:
            raise Exception('shape dimension not supported')

    def save_numpy(self, name):
        from scipy.misc import imsave
        imsave(name, self.__numpy)

    def shape(self):
        return self.shape

    def __str__(self):
        return "size: " + self.shape.__str__() + "\n" + self.__numpy.__str__()

    def __getitem__(self, item):
        return self.__numpy.__getitem__(item)

    def __setitem__(self, idx, value):
        self.__numpy.__setitem__(idx, value)

    def asarray(self):
        return self.__numpy.asarray()

    def show_grid(self):
        if not PyConrad.get_instance().is_gui_started():
            PyConrad.get_instance().start_conrad()
        self.__grid.show()

    def typestr(self):
        return ">f4"

    def __array__(self, dtype=None):
        return self.__numpy.__array__(dtype)

    def save_grid_as_tiff(self, path):
        ImageUtil.save_grid_as_tiff(self.__grid)

    def from_tiff(self, path):
        grid = ImageUtil.grid_from_tiff(path)
        return self.__class__.from_grid(grid)


