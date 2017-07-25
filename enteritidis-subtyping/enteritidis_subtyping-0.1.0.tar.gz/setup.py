# -*- coding: utf-8 -*-

from distutils.core import setup

from setuptools import find_packages

from enteritidis_subtyping import __version__, program_summary, program_name

classifiers = """
Development Status :: 3 - Alpha
Environment :: Console
License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)
Intended Audience :: Science/Research
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Bio-Informatics
Programming Language :: Python
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: Implementation :: CPython
Operating System :: POSIX :: Linux
""".strip().split('\n')

setup(
    name=program_name,
    version=__version__,
    packages=find_packages(exclude=['tests']),
    url='https://github.com/peterk87/enteritidis_subtyping',
    license='GPLv3',
    author='Peter Kruczkiewicz',
    author_email='peter.kruczkiewicz@gmail.com',
    description=program_summary,
    keywords='Salmonella Enteritidis subtyping',
    classifiers=classifiers,
    package_dir={'enteritidis_subtyping': 'enteritidis_subtyping'},
    package_data={'enteritidis_subtyping': ['data/*.fasta',]},
    install_requires=[
        'numpy>=1.12.1',
        'pandas>=0.20.1',
        'attrs',
    ],
    extras_require={
        'test': ['pytest>=3.0.7',],
    },
    entry_points={
        'console_scripts': [
            'enteritidis_subtyping=enteritidis_subtyping.main:main',
        ],
    }
)
