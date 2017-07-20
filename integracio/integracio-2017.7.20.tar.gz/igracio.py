#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import threading
import numpy as np
from . import poni, _cgracio


class IGracio:
    __units = {'t': 0, 'q': 1}

    def __init__(self):
        self._i = None
        self.pos = None
        self._poni = None
        self._poni_checksum = 0
        self._units = 't'
        self._azimuth = 0, 0
        self._radial = 0, 0
        self.__lock = threading.RLock()
        self.dim1 = 0
        self.dim2 = 0

    def _check_poni_checksum(self, poni_text):
        checksum = binascii.crc32(poni_text.encode())
        res = checksum == self._poni_checksum
        self._poni_checksum = checksum
        return res

    @property
    def poni(self):
        return self._poni

    @poni.setter
    def poni(self, poni_text):
        with self.__lock:
            if not self._check_poni_checksum(poni_text):
                self._poni = poni.Poni(poni_text)
                self._i = None
                self.pos = None

    def _initialization(self, shape):
        with self.__lock:
            if (self.dim1, self.dim2) != shape:
                self.dim1, self.dim2 = shape
                self._i = None
                self.pos = None
            if self._i is None and self._poni is not None:
                self._poni.units = self.__units.get(self._units, 0)
                self._poni.radial = self._radial
                self._i = _cgracio._integration(self.dim1, self.dim2, self._poni.geometry())
                # noinspection PyTypeChecker
                self.pos = np.asarray(self._i)

    def _integrate(self, image, azmin, azmax):
        image = image if isinstance(image, np.ndarray) else image.array
        self._initialization(image.shape)
        if azmin is None and azmax is None:
            azmin, azmax = self._azimuth
        results = np.asarray(_cgracio._results(self._i, image.astype(np.float32), azmin, azmax))
        return self.pos, results[0], results[1]

    def __call__(self, image, azmin=None, azmax=None):
        # if we integrate by azimuthal slices (oh, god), then the azimuth property does not work :(
        return self._integrate(image, azmin, azmax)

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, units):
        with self.__lock:
            if units != self._units:
                self._units = units
                self._i = None
                self.pos = None

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, azimuth):
        if azimuth is None:
            azimuth = 0, 0
        with self.__lock:
            if self._azimuth != azimuth:
                self._azimuth = azimuth

    @property
    def radial(self):
        return self._radial

    @radial.setter
    def radial(self, radial):
        if radial is None:
            radial = 0, 0
        with self.__lock:
            if self._radial != radial:
                self._radial = radial
                self._i = None
                self.pos = None
