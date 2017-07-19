#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='pylatus',
    version='2017.7.19',
    packages=['Pylatus', 'Pylatus.gui', 'Pylatus.gui.ui', 'Pylatus.scripo', 'Pylatus.devices', 'Pylatus.controller'],
    url='https://hg.3lp.cx/pylatus',
    license='GPL',
    author='Vadim Dyadkin',
    author_email='diadkin@esrf.fr',
    description='Driver for diffractometers based on SPEC and Pilatus',
    entry_points={
        'gui_scripts': [
            'pylatus=Pylatus:main',
        ],
    },
    install_requires=[
        'pyqtgraph',
        'aspic',
        'cryio',
        'scipy',
        'numpy',
        'auxygen',
    ]
)
