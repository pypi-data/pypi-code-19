#!/usr/bin/env python

'''
 @package   pNbody
 @file      generate_spherical_model_plummer.py
 @brief     Generate a snapshot with a plummer distribution
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''
from pNbody import *
from pNbody import ic
from pNbody import libgrid
from pNbody import libutil


# model parameters
n  		= 1e6				# number of particles
a 		= 0.1				# radial scale length
rmax 		= 2.				# maximal radius
G 		= 1.0				# gravitational constant
M 		= 1.0				# total mass
eps 		= 3e-3				# gravitational softening
ErrTolTheta 	= 0.5				# gravitational opening criterion
name 		= 'plummer.dat' 		# output snap file
stats_name 	= 'stats_plummer.dmp'		# output stat file

# grid parameters
grmin = 0		# grid minimal radius
grmax = rmax*1.05	# grid maximal radius
nr = 128		# number of radial bins
# transfert function
rc = a
g  = lambda r:log(r/rc+1)
gm = lambda r:rc*(exp(r)-1)

# create the model
nb = ic.plummer(n,1,1,1,eps=a,rmax=rmax,M=M,vel='no',name=name,ftype='gadget')
# set all particles to type 1
nb.set_tpe(1)



# compute velocities
nb,phi,stats = nb.Get_Velocities_From_Spherical_Grid(eps=eps,nr=nr,rmax=grmax,phi=None,g=g,gm=gm,UseTree=True,ErrTolTheta=ErrTolTheta)
# write final model
nb.write()


# save output and parameters
stats['n']   = n
stats['G']   = G
stats['M']   = M
stats['a']   = a
stats['eps'] = eps
stats['rmin'] = grmin
stats['rmax'] = grmax
stats['nr']   = nr
io.write_dmp(stats_name,stats)


##################
# info
##################

r = stats['r']
dr = r[1]-r[0]
print "Delta r :",dr,'=',dr/eps,"eps"
