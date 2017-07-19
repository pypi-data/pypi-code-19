#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from .config import Config


LAMBDA = 12.398419739640717  # c * h / ev * 1e7
DEFAULT_WAVELENGTH = 0.7  # Mo K-alpha
DEFAULT_MONODSPACING = 3.1356  # Si 111


def wavelength(mono):
    """mono angle --> wave length"""
    if Config.MonoDspacing:
        return 2 * float(Config.MonoDspacing) * math.sin(math.radians(mono))
    else:
        return DEFAULT_WAVELENGTH


def energy(mono):
    """mono angle --> energy"""
    return LAMBDA / wavelength(mono)


def angle(wl):
    """wave length --> mono angle"""
    if Config.MonoDspacing:
        d = float(Config.MonoDspacing)
    else:
        d = DEFAULT_MONODSPACING
    return math.degrees(math.asin(wl / d / 2))
