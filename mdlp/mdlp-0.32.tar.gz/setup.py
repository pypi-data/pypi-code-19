from distutils.core import setup
from Cython.Build import cythonize
import numpy
from setuptools import find_packages
from distutils.extension import Extension

extensions = [Extension("mdlp.cmdlp", ["mdlp/*.pyx"], language='c++')]
setup(name='mdlp',
      packages=find_packages(),
      version='0.32',
      description='MDLP',
      long_description='MDLP Discretization Algorithm',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Operating System :: OS Independent',
          'Intended Audience :: Science/Research',
      ],
      author='Henry Lin, Arseniy Kustov',
      author_email='me@airysen.co',
      url='https://github.com/airysen/mdlp',
      license='BSD-3',
      python_requires='>=3',
      install_requires=['scipy','numpy', 'sklearn'],
      ext_modules=cythonize(extensions),
      include_package_data=True,
      include_dirs=[numpy.get_include()]
      )
