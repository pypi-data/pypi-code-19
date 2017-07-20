#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from glob import glob
import subprocess
from setuptools import setup

package_name = 'bubble'
we_run_setup = False
if not os.path.exists('frozen.py'):
    we_run_setup = True
    hash_ = subprocess.Popen(['hg', 'id', '-i'], stdout=subprocess.PIPE).stdout.read().decode().strip()
    print('Bubble mercurial hash is {}'.format(hash_))
    frozen = open('frozen.py', 'w')
    frozen.write('hg_hash = "{}"'.format(hash_))
    frozen.close()

modules = glob('bclient/ui/*.py')
try:
    modules.remove('bclient/ui/compile.py')
except ValueError:
    pass
modules += glob('bclient/*.py')
modules += glob('bcommon/*.py')
modules += glob('bserver/*.py')
modules += ['frozen.py', '__init__.py']
modules = ['{}.{}'.format(package_name, s.replace('/', '.').split('.py')[0]) for s in modules]


setup(
    name='bubble-dubble',
    version='2017.7.20',
    description='Azimuthal powder integration',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/bubble',
    license='GPLv3',
    install_requires=[
        'numpy>=1.9',
        'cryio>=2016.11.20',
        'integracio>=2016.12.14',
        'decor>=2017.5.12',
        'pyqtgraph>=0.10.0',
        'Pillow',
    ],
    include_package_data=True,
    package_dir={'bubble': ''},
    entry_points={
        'console_scripts': [
            'bubbles={}.bserver.__init__:main'.format(package_name),
        ],
        'gui_scripts': [
            'bubblec={}.bclient.__init__:main'.format(package_name),
        ],
    },
    py_modules=modules,
)

if we_run_setup:
    os.remove('frozen.py')
