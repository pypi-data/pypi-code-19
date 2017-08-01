#!/usr/bin/env python
from os.path import join
import sys

def copy_dir():
    dir_path = 'YOUR_DIR_HERE'
    base_dir = os.path.join('MODULE_DIR_HERE', dir_path)
    for (dirpath, dirnames, files) in os.walk(base_dir):
        for f in files:
            yield os.path.join(dirpath.split('/', 1)[1], f)



if __name__ == '__main__':
    from setuptools import setup

    try:
      from version import __version__
    except:
      __version__ = ''

    
    with open("README.md") as f:
        long_description = f.read()

    with open("LICENSE.txt") as f:
        license = f.read()


    setup(name='waveletspec',
      version='1.3',
        author='Samuel Gill',
        author_email='s.gill@keele.ac.uk',
        license=license,
        url='https://github.com/samgill844/waveletspec',
	packages=['waveletspec'],
    description="Wavelet analysis of echelle spectra",
    long_description = long_description,
    data_files=[ ('waveletspec/Grids', ['data/Grids/dummy_grid.fits']), ('waveletspec/',['README.md', 'LICESNSE.txt'] )],




    classifiers = ['Development Status :: 4 - Beta']
	)   


'''
if (sys.version_info > (3, 0)):
    data_files=[ ('data/Gridss', ['data/Grids/spectrum.fits']), ( ], 
else:
'''
