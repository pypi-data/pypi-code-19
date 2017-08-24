#!/usr/bin/env python

'''
 @package   pNbody
 @file      plot_cylindrical_model_exponnential.py
 @brief     Plot exponential distribution
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

import sys

import Ptools as pt
from numpy import *




stats = pt.io.read_dmp(sys.argv[1])

n      =   stats['n']	 
M      =   stats['M']	 
G      =   stats['G']	 
hR     =   stats['hR']   
hz     =   stats['hz']   
Rmax   =   stats['Rmax'] 
Zmax   =   stats['Zmax'] 
eps    =   stats['eps']  
nz     =   stats['nz']   
nr     =   stats['nr']   
rmin   =   stats['rmin'] 
rmax   =   stats['rmax'] 
zmin   =   stats['zmin'] 
zmax   =   stats['zmax'] 


###################
# plot
###################


r = stats['R']
nn = sum(stats['nn'],axis=1)
rho = stats['rho']
phi = stats['phi']
sigma_z = stats['sigma_z']

z       = zeros(len(r))
rho     = rho[:,nz/2]		# valeur dans le plan
phi     = phi[:,nz/2]		# valeur dans le plan
sigma_z = sigma_z[:,nz/2]



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

pt.plot(r,sigma_z,'b')
pt.semilogx()
#pt.semilogy()
pt.xlabel('Radius')
pt.ylabel('Sigma')




####################
# velocity curves
####################

fig = pt.figure()

pt.subplot(1,1,1)

pt.plot(r,stats['vc'],'k')
pt.plot(r,stats['vm'],'y')
pt.plot(r,stats['sr'],'r')
pt.plot(r,stats['sp'],'g')
pt.plot(r,stats['sz'],'b')


pt.xlabel('Radius')
pt.ylabel('Velocity')
pt.title('Rotation curve and velocity dispertions')
pt.legend(('vc','vm','sr','sp','sz'))


####################
# freq.
####################

fig = pt.figure()

pt.subplot(1,1,1)

pt.plot(r,stats['kappa'],'r')
pt.plot(r,stats['omega'],'g')
pt.plot(r,stats['nu'],'b')

pt.xlabel('Radius')
pt.ylabel('Frequencies')
pt.title('Frequences')
pt.legend(('kappa','omega','nu'))

pt.show()

