
import sys
import subprocess

from distutils.core import setup
from distutils.extension import Extension

from Cython.Build import cythonize


ext_modules = cythonize(
    [Extension("cpexcel", ["src/cpexcel.pyx"], libraries=["xlsxwriter"])])



setup(name="cpxlsxwriter", version="1.0.1", ext_modules=cythonize(ext_modules),packages=['Cython'])
