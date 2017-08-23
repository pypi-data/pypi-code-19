#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from glob import glob
import subprocess
from setuptools import setup


try:
    import compile
    compile.main()
except ImportError:
    pass


dirname = 'SNBLToolBox'
file_frozen = '{}/frozen.py'.format(dirname)
we_run_setup = False
if not os.path.exists(file_frozen):
    we_run_setup = True
    hash_ = subprocess.Popen(['hg', 'id', '-i'], stdout=subprocess.PIPE).stdout.read().decode().strip()
    print('SNBL Toolbox mercurial hash is {}'.format(hash_))
    frozen = open(file_frozen, 'w')
    frozen.write('hg_hash = "{}"'.format(hash_))
    frozen.close()

modules = glob('{}/ui/*.py'.format(dirname))
try:
    modules.remove('{}/ui/compile.py'.format(dirname))
except ValueError:
    pass
modules += glob('{}/*.py'.format(dirname))
modules += glob('{}/roerik/*.py'.format(dirname))
modules = [s.replace('/', '.').split('.py')[0] for s in modules]

print(modules)
setup(
    name='snbl-toolbox',
    version='2017.8.23',
    description='SNBL Toolbox',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/snbltb',
    license='GPLv3',
    install_requires=[
        'numpy',
        'cryio',
        'pyqtgraph>=0.10.0',
        'crymon',
    ],
    include_package_data=True,
    entry_points={
        'gui_scripts': [
            'snbl={}.__init__:main'.format(dirname),
        ],
    },
    py_modules=modules,
)

if we_run_setup:
    os.remove(file_frozen)
