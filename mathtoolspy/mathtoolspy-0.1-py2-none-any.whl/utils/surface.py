# -*- coding: utf-8 -*-

#  mathtoolspy
#  ------------
#  A fast, efficient Python library for mathematically operations, like
#  integration, solver, distributions and other useful functions.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/businessdate
#  License: APACHE Version 2 License (see LICENSE file)


import bisect
from math_fcts import interpolation_bilinear, interpolation_linear


class Surface(object):
    """ A matrix with interpolation and extrapolation. """

    def __init__(self, xaxis, yaxis, values):
        '''
        The values has to be a float matrix implementing the method get_item(i, j).
        @params xaxis: list of float values.
        @params yaxis: list of float values.
        @params values: some object implementing a get_item(i, j) method or nested list.
        '''
        self.xaxis = xaxis
        self.yaxis = yaxis
        if hasattr(values, 'get_item'):
            self.values = values.get_item
        else:
            self.values = (lambda x, y: values[x][y])
        self.nx = len(self.xaxis)
        self.ny = len(self.yaxis)
        self.x0 = xaxis[0]
        self.y0 = yaxis[0]

    def get_value(self, x, y):
        ix = bisect.bisect_left(self.xaxis, x)  # x <= self.xaxis[ix]
        iy = bisect.bisect_left(self.yaxis, y)

        if ix > 0 and ix < self.nx and iy > 0 and iy < self.ny:
            # x between, y between
            x1 = self.xaxis[ix - 1]
            x2 = self.xaxis[ix]
            y1 = self.yaxis[iy - 1]
            y2 = self.yaxis[iy]
            z11 = self.values(ix - 1, iy - 1)
            z21 = self.values(ix, iy - 1)
            z22 = self.values(ix, iy)
            z12 = self.values(ix - 1, iy)
            return interpolation_bilinear(x, y, x1, x2, y1, y2, z11, z21, z22, z12)
        elif ix == 0 and iy > 0 and iy < self.ny:
            # x left, y between
            y1 = self.yaxis[iy - 1]
            y2 = self.yaxis[iy]
            z1 = self.values(0, iy - 1)
            z2 = self.values(0, iy)
            return interpolation_linear(y, y1, y2, z1, z2)
        elif ix == self.nx and iy > 0 and iy < self.ny:
            # x right, y between
            y1 = self.yaxis[iy - 1]
            y2 = self.yaxis[iy]
            z1 = self.values(self.nx - 1, iy - 1)
            z2 = self.values(self.nx - 1, iy)
            return interpolation_linear(y, y1, y2, z1, z2)
        elif ix > 0 and ix < self.nx and iy == 0:
            # x between, y left
            x1 = self.xaxis[ix - 1]
            x2 = self.xaxis[ix]
            z1 = self.values(ix - 1, 0)
            z2 = self.values(ix, 0)
            return interpolation_linear(x, x1, x2, z1, z2)
        elif ix > 0 and ix < self.nx and iy == -1:
            # x between, y right
            x1 = self.xaxis[ix - 1]
            x2 = self.xaxis[ix]
            z1 = self.values(ix - 1, self.ny - 1)
            z2 = self.values(ix, self.ny - 1)
            return interpolation_linear(x, x1, x2, z1, z2)
        elif ix == 0 and iy == 0:
            # left lower edge
            return self.values(0, 0)
        elif ix == self.nx and iy == 0:
            # right lower edge
            return self.values(self.nx - 1, 0)
        elif ix == 0 and iy == self.ny:
            # left upper edge
            return self.values(0, self.ny - 1)
        else:
            # right upper edge
            return self.values(self.nx - 1, self.ny - 1)

    def __call__(self, x, y):
        return self.get_value(x, y)
