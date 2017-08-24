#!/usr/bin/env python

'''
 @package   pNbody
 @file      plot_spherical.py
 @brief     Plot a spherical profile given with the command line
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''
import sys

import Ptools as pt

from pNbody import plummer



stats = pt.io.read_dmp(sys.argv[1])

r = stats['r']
nn = stats['nn']
rho = stats['rho']
phi = stats['phi']
sigma = stats['sigma']

###################
# plot
###################



#############
# number per bins
#############
pt.subplot(2,2,1)

pt.plot(r,nn)
pt.semilogx()
pt.semilogy()
pt.xlabel('Radius')
pt.ylabel('Number')

#############
# density
#############
pt.subplot(2,2,2)

pt.plot(r,rho,'b')
pt.semilogx()
#pt.semilogy()
pt.xlabel('Radius')
pt.ylabel('Density')

#############
# potential
#############
pt.subplot(2,2,3)

pt.plot(r,phi,'b')
pt.semilogx()
#pt.semilogy()
pt.xlabel('Radius')
pt.ylabel('Potential')

#############
# sigma
#############
pt.subplot(2,2,4)

pt.plot(r,sigma,'b')
pt.semilogx()
#pt.semilogy()
pt.xlabel('Radius')
pt.ylabel('Sigma')

pt.show()



