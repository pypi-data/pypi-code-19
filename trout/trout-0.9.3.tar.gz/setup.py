import subprocess
from distutils.core import setup, Extension 
from setuptools import find_packages
from distutils.command.install import install as DistutilsInstall
from distutils.command.build import build as DistutilsBuild

def readme():
      with open('README.rst') as f:
	       return f.read()

class Compile_Trout(DistutilsBuild):
    def run(self):
        subprocess.call(( "make"), shell=True)
        DistutilsBuild.run(self)

setup(name='trout',
      version='0.9.3',
      description='trout is a bioinformatics software package that uses suffix trees to compute the distances between genomes. ',
      long_description=readme(),
      classifiers=[
          'Intended Audience :: Science/Research',
          'Environment :: Console',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Operating System :: MacOS',
          'Operating System :: Unix'	   
      ],
      keywords='genome distance metabarcoding',
      url='https://bitbucket.org/NDBL/trout',
      author='Will Markley',
      author_email='wmarkley@nd.edu',
      platforms=[
          'Linux',
          'MacOS'
      ],
      cmdclass={'build': Compile_Trout},
      include_package_data=True,
	  package_data={'': ['README.rst'],
                    '': ['Makefile'],
                    '': ['src/trout-suffix.cpp'],
                    '': ['sam/data/*.fq'],
                    '': ['sam/data/*.lsh']},
      scripts=[
          'src/trout-compare.py',
          'src/trout-match.py',
          'src/trout-matrix.py',
		  'bin/trout-suffix'
      ],
      install_requires=[
          'setuptools',
          'subprocess'
      ]
)
