#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from setuptools import setup


DIR = os.path.dirname(__file__)


with open(os.path.join(DIR, 'rco/__init__.py')) as f:
    version = re.search(r'__version__\s+=\s+[\'\"]+(.*)[\'\"]+', f.read()).group(1)


def main ():
    setup (
        name = 'python-rco',
        version = version,
        description = 'RC Online services library',
        long_description = 'RC Online services library',
        author = 'Ruslan V. Uss',
        author_email = 'unclerus@gmail.com',
        license = 'LGPLv3',
        packages = ('rco',),
        install_requires = ['cherrybase >= 0.5.1', 'pgpxmlrpc >= 1.2.3', 'regnupg >= 0.4.2']
    )


if __name__ == "__main__":
    main ()
