'''
 @package   pNbody
 @file      setup.py
 @brief     Install pNbody
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

import sys,os,string,glob

from distutils.sysconfig import *
from distutils.core import setup,Extension
from distutils.command.build_ext import build_ext
from distutils.command.install import install
from distutils.command.install_data import install_data

import numpy


long_description = """\
This module provides lots of tools used
to deal with Nbody particles models.
"""

INCDIRS=['.']
SCRIPTS = glob.glob('scripts/*')

INCDIRS.append(numpy.get_include())
#INCDIRS.append(numpy.get_numarray_include())
#INCDIRS.append(os.path.join(numpy.get_numarray_include(),'numpy'))               

##############################################################
# usefull libraries
##############################################################

M_LIB        = "m"
GSL_LIB      = "gsl"
GSLCBLAS_LIB = "gslcblas"





##############################################################
# variables for ptree
##############################################################
WITH_PTREE = False  
MPICH_DIR = "/cvos/shared/apps/ofed/1.2.5.3/mpi/gcc/mvapich2-0.9.8-15/lib"
MPICH_LIB = "mpich"
MPICH_INC = "/cvos/shared/apps/ofed/1.2.5.3/mpi/gcc/mvapich2-0.9.8-15/include"


##############################################################
# variables for cooling
##############################################################
WITH_COOLING_WITH_METALS = True  

##############################################################
# variables for gsl
##############################################################
WITH_GSL = False




class pNbody_install_data (install_data):
  def finalize_options (self):
    if self.install_dir is None:
      install_lib = self.get_finalized_command('install_lib')
      self.warn_dir = 0
      self.install_dir = os.path.normpath(os.path.join(install_lib.install_dir,"pNbody"))
      
      
      
######################
# extensions  
      

ext_modules = []

ext_modules.append(Extension("pNbody.nbodymodule",   ["src/nbodymodule/nbodymodule.c"],		include_dirs=INCDIRS,libraries=[M_LIB]))
ext_modules.append(Extension("pNbody.myNumeric",     ["src/myNumeric/myNumeric.c"],		include_dirs=INCDIRS,libraries=[M_LIB]))
ext_modules.append(Extension("pNbody.mapping",       ["src/mapping/mapping.c"],			include_dirs=INCDIRS,libraries=[M_LIB]))    
ext_modules.append(Extension("pNbody.montecarlolib", ["src/montecarlolib/montecarlolib.c"],	include_dirs=INCDIRS,libraries=[M_LIB]))	     
ext_modules.append(Extension("pNbody.iclib",         ["src/iclib/iclib.c"],			include_dirs=INCDIRS,libraries=[M_LIB]))  
ext_modules.append(Extension("pNbody.treelib",       ["src/treelib/treelib.c"],			include_dirs=INCDIRS,libraries=[M_LIB]))
ext_modules.append(Extension("pNbody.nbdrklib",      ["src/nbdrklib/nbdrklib.c"],		include_dirs=INCDIRS,libraries=[M_LIB]))	     
ext_modules.append(Extension("pNbody.peanolib",      ["src/peanolib/peanolib.c"],		include_dirs=INCDIRS,libraries=[M_LIB])) 	     


ext_modules.append(Extension("pNbody.coolinglib",    ["src/coolinglib/coolinglib.c"],		include_dirs=INCDIRS,libraries=[M_LIB]))	     
ext_modules.append(Extension("pNbody.cosmolib",      ["src/cosmolib/cosmolib.c"],		include_dirs=INCDIRS,libraries=[M_LIB]))     
ext_modules.append(Extension("pNbody.asciilib",      ["src/asciilib/asciilib.c"],		include_dirs=INCDIRS,libraries=[M_LIB]))	     

ext_modules.append(Extension("pNbody.asciilib",      ["src/asciilib/asciilib.c"],		include_dirs=INCDIRS,libraries=[M_LIB]))	     

ext_modules.append(Extension("pNbody.tessel",        ["src/tessel/tessel/tessel.c"],		include_dirs=INCDIRS,libraries=[M_LIB]))	     

ext_modules.append(Extension("pNbody.libtipsy",      ["src/libtipsy/libtipsy.c"],		include_dirs=INCDIRS,libraries=[M_LIB]))	     

ext_modules.append(Extension("pNbody.thermodynlib",  ["src/thermodynlib/thermodynlib.c"],       include_dirs=INCDIRS,libraries=[M_LIB]))	     


if WITH_PTREE:

  ext_modules.append(Extension("pNbody.ptreelib", ["src/ptreelib/domain.c",
  	     "src/ptreelib/endrun.c",
  	     "src/ptreelib/forcetree.c",
  	     "src/ptreelib/ngb.c",
  	     "src/ptreelib/peano.c",
  	     "src/ptreelib/ptreelib.c",
  	     "src/ptreelib/potential.c",
  	     "src/ptreelib/gravtree.c",
  	     "src/ptreelib/density.c",
  	     "src/ptreelib/sph.c",
  	     "src/ptreelib/io.c",
  	     "src/ptreelib/system.c"],
  	     include_dirs=["src/ptreelib/",MPICH_INC],library_dirs=[MPICH_DIR],libraries=[MPICH_LIB]))         

if WITH_COOLING_WITH_METALS:
  # need gsl
  ext_modules.append(Extension("pNbody.cooling_with_metals",["src/cooling_with_metals/cooling_with_metals.c"],include_dirs=INCDIRS,libraries=[GSL_LIB,GSLCBLAS_LIB,M_LIB]))


if WITH_GSL:
  ext_modules.append(Extension("pNbody.pygsl",["src/pygsl/pygsl.c"],include_dirs=INCDIRS,libraries=[GSL_LIB,M_LIB]))




######################
# list of packages


packages = [
  'pNbody',
  'pNbody.SSP'
  ]
  
##############
## data
##############
data_files = []
data_files.append(('config',glob.glob('./config/*parameters')))
data_files.append(('config/rgb_tables',glob.glob('./config/rgb_tables/*')))
#data_files.append(('config/formats',glob.glob('./config/*.py')))		# trick to avoid rpm problems
data_files.append(('config/formats',glob.glob('./config/formats/*.py')))
data_files.append(('config/extensions',glob.glob('./config/extensions/*.py')))
data_files.append(('plugins',glob.glob('./config/*.py')))			# trick to avoid rpm problems
data_files.append(('plugins',glob.glob('./config/plugins/*.py')))
data_files.append(('config/opt/SSP',glob.glob('./config/opt/SSP/*[txt,dat]')))
data_files.append(('config/opt/SSP/P94_salpeter',glob.glob('./config/opt/SSP/P94_salpeter/*')))
data_files.append(('fonts',glob.glob('./fonts/*')))
#data_files.append(('tests',glob.glob('./tests/*')))
#data_files.append(('doc',glob.glob('./doc/man.ps')))

# examples
data_files.append(('examples',glob.glob('./examples/*.dat')))
data_files.append(('examples',glob.glob('./examples/*.py')))			    
data_files.append(('examples/scripts',glob.glob('./examples/scripts/*.py')))

# examples ic
data_files.append(('examples/ic',glob.glob('./examples/ic/*.py')))
data_files.append(('examples/ic',glob.glob('./examples/ic/Readme')))

#data_files.append(('examples/scripts/mpi',glob.glob('./examples/scripts/mpi/*')))
#data_files.append(('examples/films',glob.glob('./examples/films/*')))


     

setup 	(       name	       	= "pNbody",
       		version         = "4.2.1",
       		author	      	= "Revaz Yves",
       		author_email    = "yves.revaz@epfl.ch",
		url 		= "http://obswww.unige.ch/~revaz/pNbody/index.html",
       		description     = "pNbody module",
		
		packages 	= packages,
		
		cmdclass        = {'install_data': pNbody_install_data},
		
                ext_modules 	= ext_modules,

		data_files      = data_files,
			    
                scripts = SCRIPTS			    
 	)
		
