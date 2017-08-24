#!/usr/bin/env python

'''
 @package   pNbody
 @file      generate_cylindrical_model_miyamoto.py
 @brief     Generate a snapshot with a Miyamoto distribution
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''
from pNbody import *
from pNbody import ic
from pNbody import libgrid
from pNbody import libutil
from pNbody import libmiyamoto




# model parameters
n    	    		= 1e5	        	# number of points
nf   			= 8			# particle number mutiplicative number (used to reduce noise)
M    	    		= 1.0	        	# total mass
G    	   		= 1.0	        	# gravitational constant
hR   	    		= 3.	        	# radial scale length
hz   	    		= 0.3	        	# horizontal scale length
a    	    		= hR-hz	        	# miyamoto parameter a
b    	    		= hz	        	# miyamoto parameter b
Rmax 	    		= 10*hR	        	# maximal radius
Zmax 	    		= 10*hz	        	# maximal z
eps  	    		= 0.05	        	# gravitational softening
AdaptativeSoftenning 	= False			# use an adaptative softenning based on grid cells 
ErrTolTheta 		= 0.5			# gravitational opening criterion
name        		= 'miyamoto.dat'		# output snap file
stats_name  		= 'stats_miyamoto.dmp'	# output stat file


# grid parameters
rmin = 0.		# minimal grid radius
rmax =  Rmax*1.05	# maximal grid radius
zmin = -Zmax*1.05	# minimal grid z
zmax =  Zmax*1.05	# maximal grid z
nr   = 64		# number of bins in r
nt   = 2		# number of bins in t
nz   = 64+1 		# number of bins in z
                        # for an even value of nz, the potential is computed at z=0 
			# for an odd  value of nz, the density   is computed at z=0

# define transfert functions
rc = 1.
g  = lambda r:log(r/rc+1)
gm = lambda r:rc*(exp(r)-1)

# set methods used to compute velocity dispersions
mode_sigma_z = {"name":"jeans","param":None}
mode_sigma_r = {"name":"epicyclic_approximation","param":1.}	
mode_sigma_p = {"name":"epicyclic_approximation","param":None}
params = [mode_sigma_z,mode_sigma_r,mode_sigma_p]


# create the model
nb = ic.miyamoto_nagai(int(n*nf),a,b,Rmax,Zmax,irand=1,name=name,ftype='gadget')
# set all particles to type 2
nb.set_tpe(2)

# open the model
#nb = Nbody(name,ftype='gadget')


# compute velocities
nb,phi,stats = nb.Get_Velocities_From_Cylindrical_Grid(select='disk',disk=('gas','bulge','disk'),eps=eps,nR=nr,nz=nz,nt=nt,Rmax=rmax,zmin=zmin,zmax=zmax,params=params,Phi=None,g=g,gm=gm,ErrTolTheta=ErrTolTheta,AdaptativeSoftenning=AdaptativeSoftenning)

# reduc
if nf>1:
  nb = nb.reduc(nf,mass=True)
  
# write final model
nb.write()


# save output and parameters
stats['n']    = n
stats['M']    = M
stats['G']    = G
stats['hR']   = hR
stats['hz']   = hz
stats['a']    = a
stats['b']    = b
stats['Rmax'] = Rmax
stats['Zmax'] = Zmax
stats['eps']  = eps
stats['nz']   = nz
stats['nr']   = nr
stats['rmin'] = rmin
stats['rmax'] = rmax
stats['zmin'] = zmin
stats['zmax'] = zmax

io.write_dmp(stats_name,stats)



##################
# info
##################

r = stats['R']
z = stats['z']

dr = r[1]-r[0]
dz = z[nz/2+1]-z[nz/2]

print "Delta R :",dr,"=",dr/eps,"eps"
print "Delta z :",dz,"=",dz/eps,"eps"



