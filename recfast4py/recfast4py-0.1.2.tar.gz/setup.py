#!/usr/bin/env python
# encoding: utf-8

import sys
from setuptools import setup, Extension

try:
    import numpy.distutils.misc_util
except ImportError:
    print("please install numpy first")
    sys.exit(1)


try:
    desc = open("README.rst").read()
except IOError:
    desc = ""

required = ["numpy"]

setup(
    name="recfast4py",
    version="0.1.2",
    author="Joel Akeret",
    author_email="jakeret@phys.ethz.ch",
    url='http://refreweb.phys.ethz.ch/software/recfast4py/0.1.2',
    packages=["recfast4py"],
    description=("A slightly modified version of Recfast++ to do the "
                 "recombination computation"),
    long_description=desc,
    install_requires=required,
    ext_modules=[Extension("recfast4py._recfast",
                           sources=["recfast4py/_recfast.cpp",
                                    "recfast4py/cosmology.Recfast.cpp",
                                    "recfast4py/evalode.Recfast.cpp",
                                    "recfast4py/recombination.Recfast.cpp",
                                    "recfast4py/ODE_solver.Recfast.cpp",
                                    "recfast4py/DM_annihilation.Recfast.cpp",
                                    "recfast4py/Rec_corrs_CT.Recfast.cpp"]
                           )],
    include_dirs=numpy.distutils.misc_util.get_numpy_include_dirs(),
    package_data={'recfast4py': ['data/*.dat']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
