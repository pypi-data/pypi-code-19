'''
Created on 09. Okt. 2016

@author: chof
'''

from setuptools import setup
import os

packageDescription = ''

with open('README.rst', 'r') as f:
    packageDescription += f.read()

setup(name             = 'dbversions',
      version          = '0.7.1',
      author           = 'Christian Hofbauer',
      author_email     = 'chof@gmx.at',
      description      = 'A python tool and package that helps to keep a ' + 
                         'corresponding db version for each branch of a ' + 
                         'git repository.',
      long_description = packageDescription,
      license          = 'New BSD License',
      packages         = ['dbversions'],
      package_dir      = { '' : 'src' },
      package_data     = { 'dbversions' : ['data/templates/*.json']},
      setup_requires = [ 'GitPython >= 2.0.8'], 
      install_requires = [ 'GitPython >= 2.0.8'], 
      scripts=['src/dbconfig.py', 
               'src/dbversions_init.py', 
               'src/dbversions_postcheckout.py'] )