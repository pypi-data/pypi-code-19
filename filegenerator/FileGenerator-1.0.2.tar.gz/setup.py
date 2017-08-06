#!/usr/bin/env python
from setuptools import setup
setup(
  name             = 'FileGenerator',
  version          = '1.0.2',
  description      = 'Universal file generation toolbox',
  author           = 'Josiah Kerley',
  author_email     = 'josiah@kerley.io',
  url              = 'http://josiahkerley.github.io/projects/2016/06/18/filegen.html',
  install_requires = [
    "pyyaml",
    "jinja2",
    "argparse",
    "nose"
  ],
  zip_safe         = False,
  packages         = [
    'FileGen'
  ],
  entry_points     = {
    "console_scripts": [
      "filegen = FileGen:shell_start"
    ]
  },
)