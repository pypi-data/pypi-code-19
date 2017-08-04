#! /usr/bin/env python
#
# Copyright (C) 2015 Chris Holdgraf
# <choldgraf@gmail.com>
#
# Adapted from MNE-Python

import os
import setuptools
from numpy.distutils.core import setup
from jekyllmarkdown import __version__

descr = """Defines a JekyllMarkdown converter for nbconvert."""

DISTNAME = 'jekyllmarkdown'
DESCRIPTION = descr
MAINTAINER = 'Chris Holdgraf'
MAINTAINER_EMAIL = 'choldgraf@berkeley.edu'
URL = 'https://github.com/choldgraf/jekyllmarkdown'
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = 'https://github.com/choldgraf/jekyllmarkdown'
VERSION = __version__


if __name__ == "__main__":
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          include_package_data=False,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          long_description=open('README.rst').read(),
          zip_safe=False,  # the package can run out of an .egg file
          classifiers=['Intended Audience :: Science/Research',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved',
                       'Programming Language :: Python',
                       'Topic :: Software Development',
                       'Topic :: Scientific/Engineering',
                       'Operating System :: OSX'],
          platforms='any',
          packages=['jekyllmarkdown'],
          package_data={},
          scripts=[],
          entry_points={
            'nbconvert.exporters': [
                'jekyllmd = jekyllmarkdown:JekyllMarkdownExporter'
            ]
          })
