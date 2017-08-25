#!/usr/bin/env python
# coding: utf-8


from setuptools import setup, find_packages

__AUTHOR__ = 'Nicolas Piaget'
__AUTHOR_EMAIL__ = 'nicolas.piaget@env.ethz.ch'

readme = open('README').read()

setup(name='Lagranto',
      version='0.1.3',
      author=__AUTHOR__,
      author_email=__AUTHOR_EMAIL__,
      maintainer=__AUTHOR__,
      maintainer_email=__AUTHOR_EMAIL__,
      url='https://lagranto.readthedocs.io/en/latest/',
      download_url='https://git.iac.ethz.ch/npiaget/Lagranto',
      description='Library to work with trajectories.',
      long_description=readme,
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      install_requires=[
          'path.py',
          'cartopy',
          'numpy',
          'netCDF4',
          'matplotlib'
      ],
      scripts=['bin/quickview.py'],
      tests_require=['pytest'],
      extras_require={
          'docs':  ['Sphinx', 'sphinx-rtd-theme'],
          'testing': ['pytest'],
      },
      include_package_data=True,
      license='GPL-3.0+',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering :: Atmospheric Science'
      ],
      keywords=['data', 'science', 'meteorology', 'climate trajectories'],
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
      )
