''' 
 @package   pNbody
 @file      ic.py
 @brief     init file
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

# -*- coding: iso-8859-1 -*-
from pNbody import *
from numpy import *
import iclib

import profiles
import sys

try:
  from scipy.integrate import quadrature
  from scipy import special
  from scipy import optimize
  is_scipy = True
except ImportError:
  is_scipy = False 




'''
# isotropic velocities
random2 = random.random([n])
random3 = random.random([n]) 
p = 2*pi*random2
costh = 1.-2.*random3			    
sinth = sqrt(1.-costh**2)
vx = v*sinth*cos(p)	     
vy = v*sinth*sin(p)				      
vz = v*costh 

# radial velocities
x = nb.pos[:,0] 
y = nb.pos[:,1]  
z = nb.pos[:,2] 
vx = v*x/r
vy = v*y/r
vz = v*z/r	    



Somes notes on the teneration of initial conditions:

Spherical case
--------------

1) if M(r) is known analitically :
  
  1.1) if it is invertible analitically
       --> for a given x between 0 and 1, find r from M(r)
  
  1.2) if it si not invertible anatitically
  
       
       1.2.1) use a Monte-Carlo approach
              (warning : may take time if the model is cuspy)
            
       1.2.2) invert M(r) numerically and create a vector of r and Mr
              then, use generic_Mr
	      
       1.2.3) for a given x between 0 and 1, find r from M(r),
              by inverting M(r). May take time.	      







'''



def get_local_n(n):
  '''
  This function set the global number of particle each
  node must hand.
  '''

  # set the number of particules per procs
  n0 = n
  npercpu = n/mpi.mpi_NTask()
  
  if mpi.mpi_IsMaster():
    npercpu = npercpu + (n-npercpu*mpi.mpi_NTask())
  
  n = npercpu
   
  ntot = mpi.mpi_allreduce(n) 
  
  if ntot!=n0:
    print "ntot=%d while n0=%d"%(ntot,n0) 
    sys.exit()
  
  return n,ntot




def ComputeGridParameters(n,args,rmax,M,pr_fct,mr_fct,Neps_des,rc,ng):
  '''
  
  This function computes dR, the appropriate grid used to approximate Mr.
  
  The grid is set in order to have "Neps_des" particles
  in the first division of the grid. Then, the radius of the grid
  follows an exponnential distribution up to rmax.
  
  1) from the density distribution, the total mass and the number of particles,
     using a newton algorithm, it computes eps, the radius that will contains "Neps_des" particles
  
 
  2) once eps is set, we determine rc (the grid scale length) from eps and ng, in order to 
     have a grid with the a first cell equal to eps.
  
  
     if the computation of rc fails, we use the default value of rc
  
  
  The function takes the following arguments
  
  n 		: number of particles
  M		: total mass
  rmax          : max radius
  args		: list of args for the profile
  pr_fct	: profile function
  mr_fct	: mass-radius function
  
  Neps_des	: desired number of point in the first beam
  rc		: default size of the first beam
  ng		: number of grid divisions
  
  
  it returns :
  
  
  Rs		: grid points
  eps		: radius containing about  Neps_des particles
  Neps		: number of particles in eps
  '''

  if not is_scipy:
    raise "module scipy needed for function ComputeModelParameters !"

  
  ###########################
  # some considerations
  ###########################

  # central density
  rho0 =  M/apply(mr_fct,(rmax,)+args)

  # mass of particles
  m = M/float(n)

  args = args + (rho0,)
  rs = args[0]

  ###########################################################################################################################
  # find eps in order to have Neps_des particles in eps
  def RfromN(r,args,m,N):
    return apply(mr_fct,(r,)+args)/m - N


  try:
    eps = optimize.newton(RfromN, x0=rs, args = (args,m,Neps_des), fprime = None, tol = 1e-10, maxiter = 500)  
  except:
    print "fail to get eps from newton, trying bisection."  
    try:
      eps = optimize.bisection(RfromN, a=1e-10, b=rs, args = (args,m,Neps_des), xtol = 1e-5, maxiter = 500)
      print "ok"
    except:
      print "fail to get eps from bisection."
      print "quit"
      sys.exit()  
  
  ###########################################################################################################################


  ###########################################################################################################################
  # compute the number of particles that will fall in eps
  Meps = apply(mr_fct,(eps,)+args)
  Neps = Meps/m
  ###########################################################################################################################


  ###########################################################################################################################
  # parameters for the adaptative grid

  # find eps in order to have Neps_des particles in eps
  def GetRc(rc,n,rmax,eps):
    return (exp((1./(ng-1))/rc)-1)/(exp(1./rc)-1) * rmax - eps


  try:
    #rc = optimize.newton(GetRc, x0=0.1, args = (n,rmax,eps), fprime = None, tol = 1e-20, maxiter = 500)  
    rc = optimize.bisection(GetRc, a=1e-4, b=rmax, args = (n,rmax,eps), xtol = 1e-3, maxiter = 500)
  except:
    print "fail to get rc, using rc=%g."%rc

  gm = lambda i:(exp((i/float(ng-1))/rc)-1)/(exp(1./rc)-1) * rmax
  g  = lambda r: float(ng-1)*rc*log(r/rmax*(exp(1./rc)-1.)+1.)
  Rs = gm(arange(ng))

  
  
  
  return Rs,rc,eps,Neps,g,gm








def ComputeGridParameters2(eps,nmax,args,rmax,M,pr_fct,mr_fct,Neps_des,rc,ng):
  '''
  
  This function computes dR, the appropriate grid used to approximate Mr.
  
  The number of particle of the model is set in order to have "Neps_des" particles
  in the first division of the grid. Then, the radius of the grid
  follows an exponnential distribution up to rmax.
  
  1) n is set from the total mass and Neps_des
   
  2) once n is set, we determine rc (the grid scale length) from eps and ng, in order to 
     have a grid with the a first cell equal to eps.
  
  
     if the computation of rc fails, we use the default value of rc
  
  
  The function takes the following arguments
  
  eps 		: the desired grid resolution
  nmax		: max number of particles
  M		: total mass
  rmax          : max radius
  args		: list of args for the profile
  pr_fct	: profile function
  mr_fct	: mass-radius function
  
  Neps_des	: desired number of point in the first beam
  rc		: default size of the first beam
  ng		: number of grid divisions
  
  
  it returns :
  
  n		: number of particles
  Rs		: grid points
  rc		: parameter of the scaling fct
  g		: scaling fct
  gm		: inverse of scaling fct
  '''

  if not is_scipy:
    raise "module scipy needed for function ComputeModelParameters !"

  
  ###########################
  # some considerations
  ###########################

  # central density
  rho0 =  M/apply(mr_fct,(rmax,)+args)

  args = args + (rho0,)
  rs = args[0]

  # number of particles  
  n = int(Neps_des*M/apply(mr_fct,(eps,)+args))


  
  # if n> nmax, find eps containing Neps_des particles
  if n>nmax:
    
    n = nmax
    
        # mass of particles
    m = M/float(n)

  
    ###########################################################################################################################
    # find eps in order to have Neps_des particles in eps
    def RfromN(r,args,m,N):
      return apply(mr_fct,(r,)+args)/m - N
  
  
    try:
      eps = optimize.newton(RfromN, x0=rs, args = (args,m,Neps_des), fprime = None, tol = 1e-10, maxiter = 500)  
    except:
      print "fail to get eps from newton, trying bisection."  
      try:
    	eps = optimize.bisection(RfromN, a=1e-10, b=rs, args = (args,m,Neps_des), xtol = 1e-5, maxiter = 500)
    	print "ok"
      except:
    	print "fail to get eps from bisection."
    	print "quit"
    	sys.exit()  
  
    ###########################################################################################################################
  
  
    ###########################################################################################################################
    # compute the number of particles that will fall in eps
    Meps = apply(mr_fct,(eps,)+args)
    Neps = Meps/m
    ###########################################################################################################################
  
  


  # mass of particles
  m = M/float(n)








  ###########################################################################################################################
  # parameters for the adaptative grid

  # find eps in order to have Neps_des particles in eps
  def GetRc(rc,ng,rmax,eps):
    return (exp((1./(ng-1))/rc)-1)/(exp(1./rc)-1) * rmax - eps


  try:
    #rc = optimize.newton(GetRc, x0=0.1, args = (n,rmax,eps), fprime = None, tol = 1e-20, maxiter = 500)  
    rc = optimize.bisection(GetRc, a=1e-4, b=rmax, args = (ng,rmax,eps), xtol = 1e-3, maxiter = 500)
  except:
    print "fail to get rc, using rc=%g."%rc

  gm = lambda i:(exp((i/float(ng-1))/rc)-1)/(exp(1./rc)-1) * rmax
  g  = lambda r: float(ng-1)*rc*log(r/rmax*(exp(1./rc)-1.)+1.)
  Rs = gm(arange(ng))

  
  
  
  return n,eps,Rs,rc,g,gm












def invert(x,rmin,rmax,fct,args,eps=1e-10):
  '''
  return vector r that corresponds to
  fct(r,args)=x
  This routine uses a simple bissector algorithm
  '''
  n = len(x)
  rrmin = rmin*ones(n)
  rrmax = rmax*ones(n)
  xxmin = fct(rrmin,args) - x
  xxmax = fct(rrmax,args) - x

  if sum((xxmin*xxmax>=0))!=0:
    print "No max between rmin and rmax ! for some points"
    sys.exit()
  
  k = 0  
  
  while max(abs(rrmax-rrmin)) > eps:
    
    print "it = %3d err = %8.1e"%(k,max(abs(rrmax-rrmin)))
    
    k = k +1 
    rr = (rrmax+rrmin)/2.
    
    xx = fct(rr,args)-x  

    rrmax = where(xxmin*xx <= 0,rr,rrmax)
    rrmin = where(xxmin*xx >  0,rr,rrmin)
    xxmin = where(xxmin*xx >  0,xx,xxmin)

  return rr    
  
  

def box(n,a,b,c,irand=1,name='box.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules distributed
  in an homogeneous box of dimension a,b,c, centred at the origin
  radius rmax.
  '''
  
  if type(n) == ndarray:
    rand_vec = n
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 
    # generate random numbers
    rand_vec = random.random([n,3])  
    
  
  pos = rand_vec-[0.5,0.5,0.5]
  pos = pos*array([2*a,2*b,2*c])
  
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb


def homodisk(n,a,b,dz,irand=1,name='homodisk.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules distributed
  in an homogeneous oval of radius a and b, and of thickness dz.
  '''



  if type(n) == ndarray:
    random1 = n[:,0]
    random2 = n[:,1]
    random3 = n[:,2]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:    
  
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 

    random1 = random.random([n])
    random2 = random.random([n])
    random3 = random.random([n]) 


    
  xx = random1**(1./2.)  
  
  theta = 2.* random2*pi  
  
  x = a* xx * cos(theta)
  y = b* xx * sin(theta) 
  z = dz*random3 - dz/2.
  
  pos = transpose(array([x,y,z]))
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb



def disklrrc(n,a,b,dz,irand=1,name='homodisk.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules distributed
  in a disk having a linear rising rotation curve.
  '''



  if type(n) == ndarray:
    random1 = n[:,0]
    random2 = n[:,1]
    random3 = n[:,2]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:    
  
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 

    random1 = random.random([n])
    random2 = random.random([n])
    random3 = random.random([n]) 


    
  xx = random1**(1./3)  
  
  theta = 2.* random2*pi  
  
  x = a* xx * cos(theta)
  y = b* xx * sin(theta) 
  z = dz*random3 - dz/2.
  
  pos = transpose(array([x,y,z]))
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb




def homosphere(n,a,b,c,irand=1,name='homosphere.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules distributed
  in an homogeneous triaxial sphere of axis a,b,c.
  '''

  if type(n) == ndarray:
    random1 = n[:,0]
    random2 = n[:,1]
    random3 = n[:,2]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:    
  
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 

    random1 = random.random([n])
    random2 = random.random([n])
    random3 = random.random([n]) 

      
  xm = (random1)**(1./3.)
  phi = random2*pi*2.		 
  costh = 1.-2.*random3   
      
  	   
  sinth = sqrt(1.-costh**2) 	   
  axm = a*xm*sinth
  bxm = b*xm*sinth	     	   
  x = axm*cos(phi)	     	   
  y = bxm*sin(phi)	     	   
  z = c*xm*costh	     	   

  pos = transpose(array([x,y,z]))
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb


def shell(n,r,irand=1,name='cell.dat',ftype='binary',verbose=False):
  '''
  Shell of radius r
  '''


  if type(n) == ndarray:
    random2 = n[:,0]
    random3 = n[:,1]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot =  get_local_n(n)   
    random2 = random.random(n)
    random3 = random.random(n) 
    

  phi = random2*pi*2.		 
  costh = 1.-2.*random3 	   
    
  sinth = sqrt(1.-costh**2)	   

  x = r*sinth*cos(phi) 	   
  y = r*sinth*sin(phi) 	   
  z = r*costh   


  pos = transpose(array([x,y,z]))
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb





def plummer(n,a,b,c,eps,rmax,M=1.,irand=1,vel='no',name='plummer.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules distributed
  in a triaxial plummer model of axis a,b,c and core radius eps
  and max radius of rmax.  
  
  rho = (1.+(r/eps)**2)**(-5/2)
  
  '''

  if type(n) == ndarray:
    random1 = n[:,0]
    random2 = n[:,1]
    random3 = n[:,2]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:    
  
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 

    random1 = random.random([n])
    random2 = random.random([n])
    random3 = random.random([n]) 



  
  # positions
  rmax = float(rmax)
  eps  = float(eps)
  
  eps = eps/rmax
  xm = 1./(1.+(eps)**2)*random1**(2./3.)    
  xm = eps*sqrt(xm/(1.-xm))	
  phi = 2*pi*random2
  
  costh = 1.-2.*random3			      
  sinth = sqrt(1.-costh**2)
  axm = rmax*a*xm*sinth
  bxm = rmax*b*xm*sinth
  x = axm*cos(phi)	     	   
  y = bxm*sin(phi) 					    
  z = rmax*c*xm*costh        
  
  pos = transpose(array([x,y,z]))
  # velocities
  if vel == 'yes':
    
    R  = sqrt(x**2+y**2)
    rho = (3.*M/(4.*pi*eps**3))*(1+(R**2+z**2)/eps**2)**(-5./2.)
    C2 = z**2+eps**2
    C  = sqrt(C2)
    
    TD = M*C/(R**2+C2)**(3./2.)
    sz = sqrt(eps**2/(8.*pi*C2)/rho) *TD
    
    vx = sz*random.standard_normal([n])
    vy = sz*random.standard_normal([n])
    vz = sz*random.standard_normal([n])
    vel = transpose(array([vx,vy,vz]))
   
  else: 
    vel = ones([n,3])*0.0
  
  # masses
  mass = ones([n])*M/ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb
  
  
def kuzmin(n,eps,dz,irand=1,name='kuzmin.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules distributed
  in a kuzmin (infinitely thin) disk 
  
  rho = eps*M/(2*pi*(R**2+eps**2)**(3/2))
  
  '''

  if type(n) == ndarray:
    random1 = n[:,0]
    random2 = n[:,1]
    random3 = n[:,2]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:    
  
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 

    random1 = random.random([n])
    random2 = random.random([n])
    random3 = random.random([n]) 
      
  rmax = 1
  xx = random1
  xx = sqrt((eps/(1-xx))**2-eps**2)
  theta = 2.* random2*pi  
  
  x = rmax* xx * cos(theta)
  y = rmax* xx * sin(theta) 
  z = dz*random3 - dz/2.
  
  pos = transpose(array([x,y,z]))
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot

  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb





  

def expd(n,Hr,Hz,Rmax,Zmax,irand=1,name='expd.dat',ftype='binary',verbose=False):
  '''
  Exonential disk
  
  rho = 1/(1+(r/rc)**2)
  '''  

  # set random seed
  irand=irand+mpi.mpi_Rank()
  # set the number of particules per procs
  n,ntot =  get_local_n(n) 

  
  pos = iclib.exponential_disk(n,Hr,Hz,Rmax,Zmax,irand)
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb





def miyamoto_nagai(n,a,b,Rmax,Zmax,irand=1,fct=None,fRmax=0,name='miyamoto.dat',ftype='binary',verbose=False):
  '''
  Miyamoto Nagai distribution
  '''

  # set random seed
  irand = irand+mpi.mpi_Rank()   
  # set the number of particules per procs
  n,ntot =  get_local_n(n) 

  
  if fct==None:
    pos = iclib.miyamoto_nagai(n,a,b,Rmax,Zmax,irand)
  else:
    pos = iclib.miyamoto_nagai_f(n,a,b,Rmax,Zmax,irand,fct,fRmax)  
       
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb






def generic_alpha(n,a,e,rmax,irand=1,fct=None,name='generic_alpha.dat',ftype='binary',verbose=False):
  '''
  Generic alpha distribution : rho ~ (r+e)^a
  '''

  # set random seed
  irand = irand+mpi.mpi_Rank()   
  # set the number of particules per procs
  n,ntot =  get_local_n(n) 

  
  pos = iclib.generic_alpha(n,a,e,rmax,irand)
       
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb











def dl2_mr(r,args):
  '''
  Mass in the radius r for the distribution
  
  rho = (1.-eps*(r/rmax)**2)
  '''  
  eps    = args[0]
  rmax = args[1]
  return ((4./3.)*r**3 - (4./5.)*eps*r**5/rmax**2)/(((4./3.) - (4./5.)*eps)*rmax**3)


def dl2(n,a,b,c,eps,rmax,irand=1,name='dl2.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules distributed as
  
  rho = (1.-eps*(r/rmax)**2)
  '''

  if type(n) == ndarray:
    random1 = n[:,0]
    random2 = n[:,1]
    random3 = n[:,2]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:    
  
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 

    random1 = random.random([n])
    random2 = random.random([n])
    random3 = random.random([n]) 
    
      
  x = random1
  xm = invert(x,0,rmax,dl2_mr,[eps,rmax])    
  phi = 2*pi*random2
  
  costh = 1.-2.*random3		      
  sinth = sqrt(1.-costh**2)
  axm = a*xm*sinth
  bxm = b*xm*sinth
  x = axm*cos(phi)	     	   
  y = bxm*sin(phi) 					    
  z = c*xm*costh        
       
  
  pos = transpose(array([x,y,z]))
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb




def isothm_mr(r,args):
  '''
  Mass in the radius r for the distribution
  
  rho = 1/(1+r/rc)**2
  '''  
  rc   = args[0]
  rm   = args[1]
  
  cte = 2*rc**3*log(rc) + rc**3
  
  Mr = r *rc**2 - 2*rc**3*log(rc+r ) - rc**4/(rc+r ) + cte
  Mx = rm*rc**2 - 2*rc**3*log(rc+rm) - rc**4/(rc+rm) + cte
  
  return Mr/Mx


def isothm(n,rc,rmax,irand=1,name='isothm.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules distributed as

  rho = 1/(1+r/rc)**2
  '''

  if type(n) == ndarray:
    random1 = n[:,0]
    random2 = n[:,1]
    random3 = n[:,2]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:    
  
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 

    random1 = random.random([n])
    random2 = random.random([n])
    random3 = random.random([n]) 
      
  x = random1
  xm = invert(x,0,rmax,isothm_mr,[rc,rmax])    
  phi = 2*pi*random2
  
  costh = 1.-2.*random3		      
  sinth = sqrt(1.-costh**2)
  axm = xm*sinth
  bxm = xm*sinth
  x = axm*cos(phi)	     	   
  y = bxm*sin(phi) 					    
  z = xm*costh        
       
  
  pos = transpose(array([x,y,z]))
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb


def pisothm_mr(r,args):
  '''
  Mass in the radius r for the distribution
  
  rho = 1/(1+(r/rc)**2)
  '''  
  rc    = args[0]
  rmn   = args[1]
  rmx   = args[2] 
 
  Mr  = rc**3 *(   r/rc - arctan( r/rc) )
  Mmn = rc**3 *( rmn/rc - arctan(rmn/rc) )
  Mmx = rc**3 *( rmx/rc - arctan(rmx/rc) )

  return (Mr-Mmn)/(Mmx-Mmn)


def pisothm(n,rc,rmax,rmin=0,irand=1,name='pisothm.dat',ftype='binary',verbose=False):
  '''
  Pseudo-isothermal sphere
  Mass in the radius r for the distribution

  rho = 1/(1+(r/rc)**2)
  '''

  if type(n) == ndarray:
    random1 = n[:,0]
    random2 = n[:,1]
    random3 = n[:,2]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:    
  
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 

    random1 = random.random([n])
    random2 = random.random([n])
    random3 = random.random([n]) 


  x = random1
  xm = invert(x,rmin,rmax,pisothm_mr,[rc,rmin,rmax])
  phi = 2*pi*random2

  costh = 1.-2.*random3
  sinth = sqrt(1.-costh**2)
  axm = xm*sinth
  bxm = xm*sinth
  x = axm*cos(phi)
  y = bxm*sin(phi)
  z = xm*costh


  pos = transpose(array([x,y,z]))
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot

  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb

 












def nfw(n,rs,Rmax,dR,Rs=None,irand=1,name='nfw.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules following
  an nfw profile. 
  
  rho = 1/[ (r/rs)(1+r/rs)^2 ]
  
  '''
  

  def Mr(r,rs):
    return 4*pi*rs**3*( log(1.+r/rs) - r/(rs+r) ) 
   
  
  if type(Rs)!=ndarray:
    Rs  = arange(0,Rmax+dR,dR)		  # should use a non linear grid
  
  Mrs = zeros(len(Rs))
  ntot = len(Rs)

  for i in xrange(len(Rs)):
    Mrs[i] =  Mr(Rs[i],rs)
    if verbose:
      print Rs[i],Mrs[i],i,'/',ntot

  # normalisation
  Mrs = Mrs/Mrs[-1]
  Mrs[0] = 0

  
  # now use Mr
  nb = generic_Mr(n,rmax=Rmax,R=Rs,Mr=Mrs,irand=irand,name=name,ftype=ftype,verbose=verbose)


  return nb







  

def hernquist(n,rs,Rmax,dR,Rs=None,irand=1,name='hernquist.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules following
  a hernquist modifed profile. 
  
  rho =  1/( (r/rs) * (1+r/rs)**3 )
  
  '''
  

  def Mr(r,rs):
    return rs**3 * 0.5*(r/rs)**2/(1+r/rs)**2
   
  
  if type(Rs)!=ndarray:
    Rs  = arange(0,Rmax+dR,dR)		  # should use a non linear grid
  
  Mrs = zeros(len(Rs))
  ntot = len(Rs)

  for i in xrange(len(Rs)):
    Mrs[i] =  Mr(Rs[i],rs)
    if verbose:
      print Rs[i],Mrs[i],i,'/',ntot

  # normalisation
  Mrs = Mrs/Mrs[-1]
  Mrs[0] = 0

  
  # now use Mr
  nb = generic_Mr(n,rmax=Rmax,R=Rs,Mr=Mrs,irand=irand,name=name,ftype=ftype,verbose=verbose)


  return nb






  
  
  




def burkert(n,rs,Rmax,dR,Rs=None,irand=1,name='burkert.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules following
  a burkert profile. 
  
  rhob = 1 / ( ( 1 + r/rs  ) * ( 1 + (r/rs)**2  ) )
  
  '''
  

  def Mr(r,rs):
    return 4*pi*rs**3*( 0.25*log((r/rs)**2+1) - 0.5*arctan(r/rs) + 0.5*log((r/rs)+1)   )
   
  
  if type(Rs)!=ndarray:
    Rs  = arange(0,Rmax+dR,dR)		  # should use a non linear grid
  
  Mrs = zeros(len(Rs))
  ntot = len(Rs)

  for i in xrange(len(Rs)):
    Mrs[i] =  Mr(Rs[i],rs)
    if verbose:
      print Rs[i],Mrs[i],i,'/',ntot

  # normalisation
  Mrs = Mrs/Mrs[-1]
  Mrs[0] = 0

  
  # now use Mr
  nb = generic_Mr(n,rmax=Rmax,R=Rs,Mr=Mrs,irand=irand,name=name,ftype=ftype,verbose=verbose)


  return nb











def nfwg(n,rs,gamma,Rmax,dR,Rs=None,irand=1,name='nfwg.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules following
  an nfw modifed profile. 
  
  rho = 1/[ ((r/rs))**(gamma)(1+r/rs)^2 ]**(0.5*(3-gamma))
  
  '''
  
  if not is_scipy:
    raise "module scipy needed for function nfwg !"
  
  

  def Mr(r,rs,gamma):
    aa = 1.5-0.5*gamma
    cc = 2.5-0.5*gamma
    z  =  -r**2/rs**2
    return 2*pi*(r/rs)**-gamma * r**3 * special.hyp2f1(aa,aa,cc,z)/aa

   
  
  if type(Rs)!=ndarray:
    Rs  = arange(0,Rmax+dR,dR)		  # should use a non linear grid
  
  Mrs = zeros(len(Rs))
  ntot = len(Rs)

  for i in xrange(len(Rs)):
    Mrs[i] =  Mr(Rs[i],rs,gamma)
    if verbose:
      print Rs[i],Mrs[i],i,'/',ntot

  # normalisation
  Mrs = Mrs/Mrs[-1]
  Mrs[0] = 0

  
  # now use Mr
  nb = generic_Mr(n,rmax=Rmax,R=Rs,Mr=Mrs,irand=irand,name=name,ftype=ftype,verbose=verbose)


  return nb









def generic2c(n,rs,a,b,Rmax,dR,Rs=None,irand=1,name='nfwg.dat',ftype='binary',verbose=False):
  '''
  Return an Nbody object that contains n particules following
  an nfw modifed profile. 
  
  rho = 1/( (r/rs)**a * (1+r/rs)**(b-a) )
  
  '''
  
  if not is_scipy:
    raise "module scipy needed for function generic2c !"
  


  def Mr(r,rs,a,b):
    a = float(a)
    b = float(b)

    aa = b-a
    bb = -a + 3
    cc = 4 - a
    z  =  -r/rs
  
    return 4*pi*(r/rs)**(-a) * r**3 * special.hyp2f1(aa,bb,cc,z)/bb
  
  
    
  if type(Rs)!=ndarray:
    Rs  = arange(0,Rmax+dR,dR)		  # should use a non linear grid
  
  Mrs = zeros(len(Rs))
  ntot = len(Rs)

  for i in xrange(len(Rs)):
    Mrs[i] =  Mr(Rs[i],rs,a,b)
    if verbose:
      print Rs[i],Mrs[i],i,'/',ntot

  # normalisation
  Mrs = Mrs/Mrs[-1]
  Mrs[0] = 0

  
  # now use Mr
  nb = generic_Mr(n,rmax=Rmax,R=Rs,Mr=Mrs,irand=irand,name=name,ftype=ftype,verbose=verbose)


  return nb










#def generic_MxHyHz(n,xmax,ymax,zmax,x=None,Mx=None,name='box_Mx.dat',ftype='binary',verbose=False):
#  '''
#  Distribute particles in a box. The density in x is defined in order to reproduce M(x) given by Mx.
#  Here, contrary to generic_Mx, the size of the box is defined.
#  '''
#  
#  if type(nx) == ndarray:
#    random1 = nx
#    random2 = ny
#    random3 = nz
#    n = len(n)
#  else:
#    random1 = random.random([nx])
#    random2 = random.random([ny])
#    random3 = random.random([nz])
#        
#  pos = iclib.generic_MxHyHz(n,xmax,ymax,zmax,x.astype(float32),Mx.astype(float32),random1.astype(float32),random2.astype(float32),random3.astype(float32),verbose)
#       
#  vel =  ones([n,3])*0.0
#  mass = ones([n])*1./n
#  
#  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)
#
#  return nb




#################################
# geometric distributions
#################################


def generic_Mx(n,xmax,x=None,Mx=None,irand=1,name='box_Mx.dat',ftype='binary',verbose=False):
  '''
  Distribute particles in a box. The density in x is defined in order to reproduce M(x) given by Mx
  '''

  if type(n) == ndarray:
    random1 = n[:,0]
    random2 = n[:,1]
    random3 = n[:,2]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:    
  
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 

    random1 = random.random([n])
    random2 = random.random([n])
    random3 = random.random([n]) 
    
        
  pos = iclib.generic_Mx(n,xmax,x.astype(float32),Mx.astype(float32),random1.astype(float32),random2.astype(float32),random3.astype(float32),verbose)
       
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb




def generic_Mr(n,rmax,R=None,Mr=None,irand=1,name='sphere_Mr.dat',ftype='binary',verbose=False):
  '''
  Distribute particles in order to reproduce M(R) given by Mr
  '''

  if type(n) == ndarray:
    random1 = n[:,0]
    random2 = n[:,1]
    random3 = n[:,2]
    n = len(n)
    ntot = mpi.mpi_allreduce(n) 
  else:    
  
    # set random seed
    random.seed(irand+mpi.mpi_Rank())	
    # set the number of particules per procs
    n,ntot   = get_local_n(n) 

    random1 = random.random([n])
    random2 = random.random([n])
    random3 = random.random([n]) 
        
  pos = iclib.generic_Mr(n,rmax,R.astype(float32),Mr.astype(float32),random1.astype(float32),random2.astype(float32),random3.astype(float32),verbose)
       
  vel =  ones([n,3])*0.0
  mass = ones([n])*1./ntot
  
  nb = Nbody(status='new',p_name=name,pos=pos,vel=vel,mass=mass,ftype=ftype)

  return nb





#################################
# geometric primitives
#################################




def line(M=1.,name='line.dat',ftype='binary'):

  x = array([-0.5,0.5])
  y = array([0,0])
  z = array([0,0])
  
  n = len(x)
  pos = transpose((x,y,z))
  mass= M*ones(n)
  nb  = Nbody(status='new',pos=pos,mass=mass,p_name=name,ftype=ftype)
  return nb
  

def square(M=1.,name='square.dat',ftype='binary'):

  x = array([-0.5,+0.5,+0.5,-0.5])
  y = array([-0.5,-0.5,+0.5,+0.5])
  z = array([0,0,0,0])

  n = len(x)
  pos = transpose((x,y,z))
  mass= M*ones(n)
  nb  = Nbody(status='new',pos=pos,mass=mass,p_name=name,ftype=ftype)
  return nb



def circle(n=10,M=1.,name='circle.dat',ftype='binary'):

  t = arange(0,2*pi,2*pi/n)

  x = cos(t)
  y = sin(t)
  z = zeros(n)

  n = len(x)
  pos = transpose((x,y,z))
  mass= M*ones(n)
  nb  = Nbody(status='new',pos=pos,mass=mass,p_name=name,ftype=ftype)
  return nb


def grid(n=10,m=10,M=1.,name='grid.dat',ftype='binary'):

  dx = 1/float(n)
  dy = 1/float(m)
    
  xx = arange(0,1+dx,dx)
  yy = arange(0,1+dy,dy)
  
  x = zeros(4*n*m)
  y = zeros(4*n*m)
  z = zeros(4*n*m)
  
  k = 0    
  for i in xrange(n):
    for j in xrange(m):
      x[k+0] = xx[i+0] - 0.5
      y[k+0] = yy[j+0] - 0.5
      
      x[k+1] = xx[i+1] - 0.5
      y[k+1] = yy[j+0] - 0.5
      
      x[k+2] = xx[i+1] - 0.5
      y[k+2] = yy[j+1] - 0.5
      
      x[k+3] = xx[i+0] - 0.5
      y[k+3] = yy[j+1] - 0.5
      k = k + 4


  n = len(x)
  pos = transpose((x,y,z))
  mass= M*ones(n)
  nb  = Nbody(status='new',pos=pos,mass=mass,p_name=name,ftype=ftype)
  return nb


def cube(M=1.,name='cube.dat',ftype='binary'):
  x = array([0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0, 0,0, 1,1, 1,1, 0,0,])-0.5
  y = array([0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0, 0,0, 0,0, 1,1, 1,1,])-0.5
  z = array([0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1, 0,1, 0,1, 0,1, 0,1,])-0.5

  n = len(x)
  pos = transpose((x,y,z))
  mass= M*ones(n)
  nb  = Nbody(status='new',pos=pos,mass=mass,p_name=name,ftype=ftype)
  return nb

  
def sphere(n=10,m=10,M=1.,name='sphere.dat',ftype='binary'):

  pos = zeros((2*n*m,3),float32)

  ts = arange(0,2*pi,2*pi/n)
  zs =  2*arange(m)/float(m-1) - 1

  k = 0
  
  # parallels
  for i in range(m):
    for j in range(n):
      r = sin(arccos(zs[i]))
      x = r*cos(ts[j])
      y = r*sin(ts[j])
      z = zs[i]
          
      pos[k] = [x,y,z] 
      k = k + 1

  # meridians
  for j in range(n):
    for i in range(m):
      r = sin(arccos(zs[i]))
      x = r*cos(ts[j])
      y = r*sin(ts[j])
      z = zs[i]
          
      pos[k] = [x,y,z] 
      k = k + 1

  nb  = Nbody(status='new',pos=pos,p_name=name,ftype=ftype)
  nb.mass = M*nb.mass
  
  return nb


def arrow(M=1.,name='arrow.dat',ftype='binary'):

  q = (1+sqrt(5)) / 2.	# golden number

  lx = 1/q
  x1 = lx/3.
  x2 = 2*lx/3.
  y1 = 1./q

  x = array([x1,x2,x2,lx,0.5*lx ,0,x1,x1    ])
  y = array([0,0,y1,y1,1,y1,y1,0])
  z = zeros(len(x))

  n = len(x)
  pos = transpose((x,y,z))
  mass= M*ones(n)
  nb  = Nbody(status='new',pos=pos,mass=mass,p_name=name,ftype=ftype)
  
  nb.translate([-lx/2, -1 , 0])
  nb.rotate(axis='z',angle=pi)
  
  return nb











