#!/usr/bin/env python

from pNbody import *
from pNbody import ic
from pNbody import libgrid
from pNbody import libutil
from pNbody import libdisk






#################################################################
# model parameters
#################################################################

Ntot 	= 2**19			# total number of particles
nf   	= 1			# particle number mutiplicative number (used to reduce noise)
eps 	= 0.25			# softening

# mass ratio between components
fm_gas   = 1.
fm_disk  = 5.
fm_bulge = 5.
fm_halo  = 20.

# disk
M_disk   = 40.
Hr_disk  = 4.
Hz_disk  = 0.3
fr_disk  = 10.
fz_disk  = 10.

# halo
M_halo   = 300.
Hr_halo  = 30.
fr_halo  = 3.0

# bulge
M_bulge  = 16.0
Hr_bulge = 1.4
fr_bulge = 5.0

# gas
M_gas    = 8.
Hz_gas   = 0.3
Hr_gas  = 4.0
Rf       = 40.
Hr_gas   = Hr_gas - Hz_gas
rmax_gas = 3*Hr_halo
zmax_gas = 3*Hz_gas



#################################################################
# parameters for the velocities
#################################################################

ErrTolTheta = 0.5
AdaptativeSoftenning = False



###################################
# spherical components
###################################


# grid parameters halo
stats_name_halo = "stats_halo.dmp"
grmin_halo 	= 0				# grid minimal radius
grmax_halo 	= Hr_halo*fr_halo*1.05		# grid maximal radius
nr_halo 	= 64				# number of radial bins
eps_halo	= eps
# transfert function
rc_halo 	= Hr_halo
g_halo  	= lambda r:log(r/rc_halo+1.)
gm_halo 	= lambda r:rc_halo*(exp(r)-1.)


# grid parameters bulge
stats_name_bulge = "stats_bulge.dmp"
grmin_bulge 	= 0				# grid minimal radius
grmax_bulge 	= Hr_bulge*fr_bulge*1.05	# grid maximal radius
nr_bulge 	= 64				# number of radial bins
eps_bulge	= eps
# transfert function
rc_bulge 	= Hr_halo
g_bulge  	= lambda r:log(r/rc_bulge+1.)
gm_bulge 	= lambda r:rc_bulge*(exp(r)-1.)



###################################
# cylindrical components
###################################


# grid parameters disk
stats_name_disk = "stats_disk.dmp"
grmin_disk 	= 0.			# minimal grid radius
grmax_disk 	=  Hr_disk*fr_disk	# maximal grid radius
gzmin_disk 	= -Hz_disk*fz_disk	# minimal grid z
gzmax_disk 	=  Hz_disk*fz_disk	# maximal grid z
nr_disk   	= 32			# number of bins in r
nt_disk   	= 2			# number of bins in t
nz_disk   	= 64+1 			# number of bins in z
                        		# for an even value of nz, the potential is computed at z=0 
					# for an odd  value of nz, the density   is computed at z=0
eps_disk	= eps
rc_disk 	= 3.0
g_disk  	= lambda r:log(r/rc_disk+1.)
gm_disk 	= lambda r:rc_disk*(exp(r)-1.)

mode_sigma_z = {"name":"jeans","param":None}
mode_sigma_r = {"name":"toomre","param":1.0}		
mode_sigma_p = {"name":"epicyclic_approximation","param":None}
params_disk = [mode_sigma_z,mode_sigma_r,mode_sigma_p]


# grid parameters gas
stats_name_gas = "stats_gas.dmp"
grmin_gas 	= 0.			# minimal grid radius
grmax_gas 	=  rmax_gas*1.05	# maximal grid radius
gzmin_gas 	= -zmax_gas*1.05	# minimal grid z
gzmax_gas 	=  zmax_gas*1.05	# maximal grid z
nr_gas   	= 32			# number of bins in r
nt_gas   	= 2			# number of bins in t
nz_gas   	= 64+1 			# number of bins in z
                        		# for an even value of nz, the potential is computed at z=0 
					# for an odd  value of nz, the density   is computed at z=0
eps_gas		= eps
rc_gas 		= 3.0
g_gas  		= lambda r:log(r/rc_gas+1.)
gm_gas 		= lambda r:rc_gas*(exp(r)-1.)

mode_sigma_z = {"name":"jeans","param":None}
mode_sigma_r = {"name":"constant","param":0.1}		
mode_sigma_p = {"name":"epicyclic_approximation","param":None}
params_gas = [mode_sigma_z,mode_sigma_r,mode_sigma_p]









#################################################################
# compute mass for each components
#################################################################


# ref mas of particles
m = ( M_disk/fm_disk + M_halo/fm_halo + M_bulge/fm_bulge + M_gas/fm_gas )/float(Ntot)


# distributes number of particles
N_gas   = int( M_gas  /(m*fm_gas) )
N_disk  = int( M_disk /(m*fm_disk) )
N_bulge = int( M_bulge/(m*fm_bulge) )
N_halo  = int( M_halo/(m*fm_halo) )
 
print "N_gas   = %d"%N_gas  
print "N_disk  = %d"%N_disk 
print "N_bulge = %d"%N_bulge
print "N_halo  = %d"%N_halo 
print "----------------------------"
print "N_tot   = %d"%(N_gas+N_disk+N_bulge+N_halo) 
print "----------------------------"



if nf > 1:

  N_gas    = int(nf*N_gas)  
  N_disk   = int(nf*N_disk) 
  N_bulge  = int(nf*N_bulge)
  N_halo   = int(nf*N_halo)
  
    



#################################################################
# generate models
#################################################################


#####################
# exponnential disk
#####################

nb_disk = None
if M_disk != 0.0:
  print "generating disk..."
  nb_disk = ic.expd(N_disk,Hr_disk,Hz_disk,fr_disk*Hr_disk,fz_disk*Hz_disk,irand=0,ftype='gadget')
  nb_disk.set_tpe(2)
  nb_disk.mass = (M_disk/N_disk) * ones(nb_disk.nbody).astype(float32)
  nb_disk.rename('disk.dat')
  nb_disk.write()


#####################
# halo
#####################

nb_halo = None
if M_halo != 0.0:
  print "generating halo..."
  nb_halo = ic.plummer(N_halo,1,1,1,Hr_halo,fr_halo*Hr_halo,vel='no',ftype='gadget')
  nb_halo.set_tpe(1)
  nb_halo.mass = (M_halo/N_halo) * ones(nb_halo.nbody).astype(float32)
  nb_halo.rename('halo.dat')
  nb_halo.write()

#####################
# bulge
#####################

nb_bulge = None
if M_bulge != 0.0:
  print "generating bulge..."
  nb_bulge = ic.plummer(N_bulge,1,1,1,Hr_bulge,fr_bulge*Hr_bulge,vel='no',ftype='gadget')
  nb_bulge.set_tpe(3)
  nb_bulge.mass = (M_bulge/N_bulge) * ones(nb_bulge.nbody).astype(float32)
  nb_bulge.rename('bulge.dat')
  nb_bulge.write()

#####################
# gas disk
#####################

nb_gas = None
if M_gas != 0.0:
  print "generating gas..."
  nb_gas =  ic.miyamoto_nagai(N_gas,Hr_gas,Hz_gas,rmax_gas,zmax_gas,irand=-2,ftype='gadget')
  nb_gas.set_tpe(0)  
  nb_gas.mass = (M_gas/N_gas) * ones(nb_gas.nbody).astype(float32)
  nb_gas.rename('gas.dat')
  nb_gas.write()



###############################################################
# merge all components
###############################################################

#nb = Nbody(ftype='gadget')
nb = None

if nb_disk != None:
  if nb ==None:
    nb = nb_disk
  else:
    nb = nb + nb_disk
  

if nb_halo != None:
  if nb ==None:
    nb = nb_halo
  else:
    nb = nb + nb_halo

if nb_bulge != None:
  if nb ==None:
    nb = nb_bulge
  else:
    nb = nb + nb_bulge

if nb_gas != None:
  if nb ==None:
    nb = nb_gas
  else:
    nb = nb + nb_gas


nb.rename('snapnf.dat')
nb.write()



   

   
###############################################################
# compute velocities
###############################################################


if nb_disk != None:
  print "------------------------"
  print "disk velocities..."
  print "------------------------"
  nb_disk,phi,stats_disk = nb.Get_Velocities_From_Cylindrical_Grid(select='disk',disk=('disk','gas'),eps=eps_disk,nR=nr_disk,nz=nz_disk,nt=nt_disk,Rmax=grmax_disk,zmin=gzmin_disk,zmax=gzmax_disk,params=params_disk,Phi=None,g=g_disk,gm=gm_disk,ErrTolTheta=ErrTolTheta,AdaptativeSoftenning=AdaptativeSoftenning)
  io.write_dmp(stats_name_disk,stats_disk)

  r = stats_disk['R']
  z = stats_disk['z']
  dr = r[1]-r[0]
  dz = z[nz_disk/2+1]-z[nz_disk/2]
  print "disk : Delta R :",dr,"=",dr/eps_disk,"eps"
  print "disk : Delta z :",dz,"=",dz/eps_disk,"eps"

  # reduc
  if nf>1:
    nb_disk = nb_disk.reduc(nf,mass=True)


if nb_gas != None:
  print "------------------------"
  print "gas velocities..."
  print "------------------------"
  nb_gas,phi,stats_gas = nb.Get_Velocities_From_Cylindrical_Grid(select='gas',disk=('disk','gas'),eps=eps_gas,nR=nr_gas,nz=nz_gas,nt=nt_gas,Rmax=grmax_gas,zmin=gzmin_gas,zmax=gzmax_gas,params=params_gas,Phi=None,g=g_gas,gm=gm_gas,ErrTolTheta=ErrTolTheta,AdaptativeSoftenning=AdaptativeSoftenning)
  io.write_dmp(stats_name_gas,stats_gas)

  r = stats_gas['R']
  z = stats_gas['z']
  dr = r[1]-r[0]
  dz = z[nz_gas/2+1]-z[nz_gas/2]
  print "gas   : Delta R :",dr,"=",dr/eps_gas,"eps"
  print "gas   : Delta z :",dz,"=",dz/eps_gas,"eps"

  # reduc
  if nf>1:
    nb_gas = nb_gas.reduc(nf,mass=True)
  
  
if nb_bulge != None:
  print "------------------------"
  print "bulge velocities..."
  print "------------------------"
  nb_bulge,phi,stats_bulge = nb.Get_Velocities_From_Spherical_Grid(select='bulge',eps=eps_bulge,nr=nr_bulge,rmax=grmax_bulge,phi=None,g=g_bulge,gm=gm_bulge,UseTree=True,ErrTolTheta=ErrTolTheta)
  io.write_dmp(stats_name_bulge,stats_bulge)

  r = stats_bulge['r']
  dr = r[1]-r[0]
  print "bulge : Delta r :",dr,'=',dr/eps_bulge,"eps"

  # reduc
  if nf>1:
    nb_bulge = nb_bulge.reduc(nf,mass=True)
   
    
if nb_halo != None:
  print "------------------------"
  print "halo velocities..."
  print "------------------------"
  nb_halo,phi,stats_halo = nb.Get_Velocities_From_Spherical_Grid(select='halo',eps=eps_halo,nr=nr_halo,rmax=grmax_halo,phi=None,g=g_halo,gm=gm_halo,UseTree=True,ErrTolTheta=ErrTolTheta)
  io.write_dmp(stats_name_halo,stats_halo)

  r = stats_halo['r']
  dr = r[1]-r[0]
  print "halo : Delta r :",dr,'=',dr/eps_halo,"eps"

  # reduc
  if nf>1:
    nb_halo = nb_halo.reduc(nf,mass=True)


###############################################################
# recompose models and save it
###############################################################
 

#nb = Nbody(ftype='gadget')
nb = None

if nb_disk != None:
  if nb ==None:
    nb = nb_disk
  else:
    nb = nb + nb_disk
  

if nb_halo != None:
  if nb ==None:
    nb = nb_halo
  else:
    nb = nb + nb_halo

if nb_bulge != None:
  if nb ==None:
    nb = nb_bulge
  else:
    nb = nb + nb_bulge

if nb_gas != None:
  if nb ==None:
    nb = nb_gas
  else:
    nb = nb + nb_gas  
  



nb.rename('snap.dat')
nb.write()








