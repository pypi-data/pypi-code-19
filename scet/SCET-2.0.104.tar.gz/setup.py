#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
from glob import glob
from configparser import ConfigParser
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


install_requires = [
    'pygubu',
    'python-sql',
    'pymysql',
]

dependency_links = [
]

extras_require = {
    'PDF':  ['weasyprint', 'lxml'],
}

py_modules = [
]

packages = [
    'scet',
]

package_dir = {
}

package_data = {
    'scet':[
        path.join('BaseDeDatos', '*.sql'),
        path.join('InterfacesGraficas', '*.ui'),
        path.join('Recursos', '*.png'),
        path.join('Reportes', '*'),
        'metadata.cfg',
    ]
}

data_files = [
]

scripts = [
]

entry_points = {
    'gui_scripts': [
        'scet = scet.main:main',
    ],
}

classifiers = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Pick your license as you wish (should match "license" above)
     'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3',
],


# Leer metadatos
metadata = ConfigParser()
metadata.read('metadata.cfg')
datos = dict(metadata['metadata'])

# Ejecutar empaquetado
setup(
    install_requires = install_requires,
    dependency_links = dependency_links,
    extras_require = extras_require,
    py_modules = py_modules,
    packages = packages,
    package_dir = package_dir,
    package_data = package_data,
    data_files = data_files,
    scripts = scripts,
    entry_points = entry_points,

    #~ classifiers = classifiers,
    long_description = open('README').read(),
    license = 'MIT',
    **datos
)
