from distutils.core import setup
from distutils.extension import Extension
import numpy
import os

def find_version(path):
    import re
    # path shall be a plain ascii text file.
    s = open(path, 'rt').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              s, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Version not found")


extensions = [
        Extension("orderedobject", ["orderedobject.pyx"], include_dirs=["./"]),
]

from Cython.Build import cythonize
extensions = cythonize(extensions)

setup(
    name="orderedobject", version=find_version("orderedobject.pyx"),
    author="Yu Feng",
    description="An orderedobject unreferences its attributes with a deterministic order",
    home_page="https://github.com/rainwoodman/orderedobject",
    install_requires=['cython'],
    license='BSD-2-Clause',
    py_modules = ["test_orderedobject"],
    ext_modules = extensions,
)

