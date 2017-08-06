# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

__author__ = 'christoph.statz <at> tu-dresden.de'

from setuptools import find_packages, setup
from setuptools.extension import Extension

import numpy
import visit

numpy_include = numpy.get_include()
visit_include = visit.get_include()
visit_lib = visit.get_library_dirs()

simV2 = Extension("visitsimv2._simV2",
    sources = [
        "src/simV2_PyObject.cxx",
        "src/simV2_custom.cxx",
        "src/simV2_wrap.cxx"
    ],
    include_dirs = [
        "src/",
        "src/libsim",
        numpy_include
    ] + visit_include,
    library_dirs = visit.get_library_dirs(),
    libraries = ['simV2']
)

setup(setup_requires=['pbr>=1.9'], pbr=True, ext_modules=[simV2])
