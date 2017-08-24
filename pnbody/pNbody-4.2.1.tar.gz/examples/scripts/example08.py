'''
 @package   pNbody
 @file      example08.py
 @brief     Read and display a snapshot
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

from pNbody import *
nb = Nbody('gadget.dat',ftype='gadget')
nb.show(size=(25,25),
           obs=None,
           shape=(256,256),
	   palette='rainbow4',
	   mode='m',
	   view='xz',
	   mn=0,
	   mx=0,
	   scale='log',
	   filter_name='gaussian',
	   filter_opts=[1,1],save='img.fits')
