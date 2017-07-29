#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='neurofeatures',
      version='0.0.1',
      description='Generic feature extraction package for neuroimaging features (examples include: connectivity from rs-fmri, regional mean fractional anisotropy, structural covariance etc)',
      long_description='Generic feature extraction package for neuroimaging features (examples include: connectivity from rs-fmri, regional mean fractional anisotropy, structural covariance etc); neurofeatures',
      author='Pradeep Reddy Raamana',
      author_email='raamana@gmail.com',
      url='https://github.com/raamana/neurofeatures',
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]), # ['neuropredict'],
      install_requires=['numpy', 'pyradigm', 'nibabel', 'networkx', 'medpy'],
      classifiers=[
              'Intended Audience :: Science/Research',
              'Programming Language :: Python',
              'Topic :: Software Development',
              'Topic :: Scientific/Engineering',
              'Operating System :: Microsoft :: Windows',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Operating System :: MacOS',
              'Programming Language :: Python :: 2.7',
          ],
      entry_points={
          "console_scripts": [
              "neurofeatures=neurofeatures.__main__:main",
          ]
      }

     )
