#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes


class CGeometry(ctypes.Structure):
    _fields_ = [
        ('distance', ctypes.c_float),
        ('poni1', ctypes.c_float),
        ('poni2', ctypes.c_float),
        ('pixelsize1', ctypes.c_float),
        ('pixelsize2', ctypes.c_float),
        ('rot1', ctypes.c_float),
        ('rot2', ctypes.c_float),
        ('rot3', ctypes.c_float),
        ('wavelength', ctypes.c_float),
        ('units', ctypes.c_int),
        ('radmin', ctypes.c_float),
        ('radmax', ctypes.c_float),
    ]


class PoniException(ValueError):
    pass


class Poni:
    PONI_KEYS = 'pixelsize1', 'pixelsize2', 'distance', 'poni1', 'poni2', 'rot1', 'rot2', 'rot3', 'wavelength'

    def __init__(self, poni_text):
        self._poni_text = poni_text
        self._data = {}
        self._cgeometry = None
        self._read()
        self._parse()

    def _read(self):
        for i, line in enumerate(self._poni_text.splitlines()):
            if line.startswith('#') or ':' not in line:
                continue
            words = line.split(':', 1)
            key = words[0].strip().lower()
            try:
                value = words[1].strip()
            except IndexError:
                raise PoniException('Line {} of poni file seems to be corrupted'.format(i))
            else:
                self._data[key] = value

    def _parse(self):
        for key in Poni.PONI_KEYS:
            value = self._data.get(key, 0)
            if value:
                try:
                    value = float(value)
                except ValueError:
                    raise PoniException('The poni file seems to be corrupted, '
                                        'the key "{}" -> "{}" cannot be read'.format(key, value))
                else:
                    self._data[key] = value
                    self.__dict__[key] = value
            else:
                raise PoniException('The poni file seems to be invalid, '
                                    'it does not contain key "{}"'.format(key))
        self._cgeometry = CGeometry(**self._data)
        self._cgeometry.units = 0
        self._cgeometry.radmin = 0
        self._cgeometry.radmax = 0

    def geometry(self):
        return self._cgeometry

    @property
    def units(self):
        return self._cgeometry.units

    @units.setter
    def units(self, units):
        self._cgeometry.units = units

    @property
    def wavelength(self):
        return self._cgeometry.wavelength * 1e10

    @wavelength.setter
    def wavelength(self, wl):
        self._cgeometry.wavelength = wl * 1e-10

    @property
    def radial(self):
        return self._cgeometry.radmin, self._cgeometry.radmax

    @radial.setter
    def radial(self, radial):
        if radial is None:
            radial = 0, 0
        self._cgeometry.radmin, self._cgeometry.radmax = radial
