#!/usr/bin/env python
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy as np


def get_exts():
    result = []
    for name in ['algo', 'converter', 'replaces', 'counter']:
        e = Extension(
            name="tsc.{}".format(name),
            sources=["tsc/{}.pyx".format(name)],
            include_dirs=['tsc/klib', np.get_include()],
            extra_compile_args=['-O3'],
            language='c',
        )
        result.append(e)
    return result


setup(name='tsc',
      version='0.3.4',
      description='TimeSeries Compressor',
      author='Jingchao Hu',
      author_email='jingchaohu@gmail.com',
      url='http://github.com/observerss/tsc',
      packages=find_packages(),
      package_data={'tsc': ['*.pyx', '*.pxd', 'klib/*']},
      include_package_data=True,
      ext_modules=cythonize(get_exts()),
      install_requires=['numpy', 'cython', 'brotli', 'pandas', 'bsc', 'paq'],
      python_requires='>=3.5',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: System :: Archiving :: Compression',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
      ]
      )
