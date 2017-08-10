"""Packaging settings."""

from setuptools import find_packages, setup

from clwcli import __version__

setup(
    name='clwcli',
    version=__version__,
    description='''
        A command line interface program to perform daily tasks at Clearway
    ''',
    url='https://github.com/darkamenosa/clw-cli',
    author='Tuyen Ho',
    author_email='tuyenho@clearway.vn',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='cli',
    entry_points='''
        [console_scripts]
        clw=clwcli.cli:main
    ''',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=['boto3', 'click'],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
)
