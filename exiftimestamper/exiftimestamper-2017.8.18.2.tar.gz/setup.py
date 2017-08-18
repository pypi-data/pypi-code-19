import sys
from setuptools import setup
from os import path

HERE = path.abspath(path.dirname(__file__))
setup(
    name='exiftimestamper',
    version=open(path.join(HERE, "VERSION")).read().strip(),
    author = "Ernesto Alfonso",
    author_email = "erjoalgo@gmail.com",
    # url='https://github.com/jrfonseca/gprof2dot',
    description="""A command-line tool to update jpeg file timestamps
    based on their 'EXIF DateTimeOriginal' metadata tag """,
    long_description="""A command-line tool to update jpeg file timestamps
    based on their 'EXIF DateTimeOriginal' metadata tag """,
    license="LGPL",

    py_modules=['exiftimestamper'],
    entry_points=dict(console_scripts=['exiftimestamper=exiftimestamper:main']),
    install_requires=['exifread']
)
