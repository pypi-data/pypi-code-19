#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from . import ImageError


class NotNumpyMask(ImageError):
    pass


class NumpyMask():
    def __init__(self, filepath):
        self.filepath = filepath
        try:
            self.array = np.load(filepath)['arr_0']
        except TypeError:
            raise NotNumpyMask('The file "{}" does not contain numpy mask array')
