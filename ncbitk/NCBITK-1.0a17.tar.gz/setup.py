from setuptools import setup, find_packages
from os import path

setup(
    name='NCBITK',
    packages=['NCBITK'],
    version='1.0a17',
    license='MIT',
    description="A tool kit for accessing NCBI's GenBank",
    author='Andrew Sanchez',
    author_email='inbox.asanchez@gmail.com',
    url='https://github.com/andrewsanchez/NCBITK',
    keywords='NCBI bioinformatics',
    install_requires=[
        'click',
        'numpy>=1.12.0',
        'biopython>=1.68',
        'pandas>=0.19.2',
        'python-dateutil>=2.6.0',
        'pytz>=2016.10',
        'six>=1.10.0',
    ],
    entry_points={
        'console_scripts': [
            'ncbitk=NCBITK.__main__:main',
        ],
    },
    classifiers=[
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'Development Status :: 3 - Alpha',
    ]
)
