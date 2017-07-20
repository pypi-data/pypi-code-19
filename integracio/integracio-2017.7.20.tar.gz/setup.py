#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Extension

setup(
    name='integracio',
    version='2017.7.20',
    description='pyFAI on steroids',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/integracio',
    license='GPLv3',
    install_requires=[
        'numpy>=1.9',
    ],
    include_package_data=True,
    package_dir={'integracio': ''},
    py_modules=[
        'integracio.__init__',
        'integracio.poni',
        'integracio.igracio',
    ],
    ext_modules=[
        Extension(
            'integracio._cgracio', [
                'src/cgraciomodule.c',
                'src/splitbbox.c',
                'src/twoth.c',
            ],
            extra_compile_args=['-O3'],
        )
    ],
)
