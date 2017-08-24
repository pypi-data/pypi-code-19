#!/usr/bin/env python
'''
 @package   pNbody
 @file      generate_spherical_model_g2c.py
 @brief     Generate a snapshot with a G2C profile
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

import Ptools as pt
from numpy import *

from pNbody import ic
from pNbody import profiles
from pNbody import libutil

from scipy import optimize

import sys

# parameters for the profile
n 		= 2**17
rs              = 20.
a		= 0.
b		= 3.
rmax		= 200.
M		= 1.


# parameters for the profile generation
Neps_des	= 10.	# number of des. points in eps
ng 		= 256	# number of division to generate the model
rc		= 0.1	# default rc (if automatic rc fails) length scale of the grid



# random params
seed		= 1



# param for the plot
dR		= 0.1
nr		= int(rmax/dR)

pr_fct      = profiles.generic2c_profile
mr_fct      = profiles.generic2c_mr
ic_fct      = ic.generic2c
args	   = (rs,a,b)


# compute grid parameters
Rs,rc,eps,Neps,g,gm = ic.ComputeGridParameters(n,args,rmax,M,pr_fct,mr_fct,Neps_des,rc,ng)


# create the model
ic_args = (n,)+args+(rmax,None,Rs,seed,'snap.dat','gadget')



nb = ic.generic2c(n,rs,a,b,rmax,dR,Rs,seed,"g2c.dat",ftype='gadget')
nb.write()



# check

nbs = nb.selectc(nb.rxyz()<Rs[1])
print "eps =",Rs[1]
print "des part. in eps",Neps
print "eff part. in eps",nbs.nbody
print "rc",rc


#sys.exit()




###########################
# 
# plot density and Mr
#
###########################

# central density
rho0 =  M/apply(mr_fct,(rmax,)+args)


# compute the profile
r    = arange(dR,rmax,dR)
args = args + (rho0,)


##########################
# density
##########################
pt.subplot(2,1,1)


Rho = apply(pr_fct,(r,)+args)



r_nb,Rho_nb = nb.mdens(nb=nr,rm=rmax)

pt.plot(r,Rho,'-r')
pt.plot(r_nb,Rho_nb,'-b')
pt.semilogx()
pt.semilogy()

pt.xlabel('Radius')
pt.ylabel('Density')

##########################
# mr
##########################
pt.subplot(2,1,2)


Mr = apply(mr_fct,(r,)+args)

r_nb,Mr_nb = nb.Mr_Spherical(nr=nr,rmin=0,rmax=rmax)

pt.plot(r,Mr,'-r')
pt.plot(r_nb,Mr_nb,'-b')

pt.xlabel('Radius')
pt.ylabel('M(r)')

pt.show()


