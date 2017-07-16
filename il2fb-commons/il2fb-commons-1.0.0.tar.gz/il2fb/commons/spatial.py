# coding: utf-8

from .structures import BaseStructure


class Point2D(BaseStructure):
    __slots__ = ['x', 'y', ]

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "<Point2D '{0};{1}'>".format(self.x, self.y)


class Point3D(BaseStructure):
    __slots__ = ['x', 'y', 'z', ]

    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        return "<Point3D '{0};{1};{2}'>".format(self.x, self.y, self.z)
