
import string
import types
import os
import numpy as np

from copy import deepcopy

import pNbody
from pNbody import mpi, thermodyn, mapping, myNumeric
from pNbody import ctes, libutil, FLOAT, nbodymodule
from pNbody import coolinglib, geometry, treelib, libgrid, libdisk

class _NbodyDefault:
  #################################
  #
  # coordinate transformation
  #
  #################################

  #################################
  # positions
  #################################

  def x(self,center=None):
    """
    Return a 1xn float array containing x coordinate
    """
    if center is not None:
      return self.pos[:,0]-center[0]
    else:
      return self.pos[:,0]

  def y(self,center=None):
    """
    Return a 1xn float array containing y coordinate
    """
    if center is not None:
      return self.pos[:,1]-center[1]
    else:
      return self.pos[:,1]

  def z(self,center=None):
    """
    Return a 1xn float array containing z coordinate
    """
    if center is not None:
      return self.pos[:,2]-center[2]
    else:
      return self.pos[:,2]

  def rxyz(self,center=None):
    """
    Return a 1xn float array that corresponds to
    the distance from the center of each particle.
    """
    if center is not None:
      r = np.sqrt( (self.pos[:,0]-center[0])**2 + (self.pos[:,1]-center[1])**2 + (self.pos[:,2]-center[2])**2 )
    else:
      r = np.sqrt( self.pos[:,0]**2 + self.pos[:,1]**2 + self.pos[:,2]**2 )
    return r

  def phi_xyz(self):
    """
    Return a 1xn float array that corresponds to
    the azimuth in spherical coordinate of each particle.
    """
    r   = self.rxyz()
    rxy = self.rxy()
    xp  = self.pos[:,0]*r/rxy           # x projection in the plane
    yp  = self.pos[:,1]*r/rxy           # y projection in the plane
    p   = np.arctan2(yp,xp)
    return p

  def theta_xyz(self):
    """
    Return a 1xn float array that corresponds to
    the elevation angle in spherical coordinate of each particle.
    """
    r   = self.rxyz()
    t   = np.arcsin(self.pos[:,2]/r)
    return t

  def rxy(self):
    """
    Return a 1xn float array that corresponds to
    the projected distance from the center of each particle.
    """
    r = np.sqrt( self.pos[:,0]**2 + self.pos[:,1]**2)
    return r


  def phi_xy(self):
    """
    Return a 1xn float array that corresponds to
    the azimuth in cylindrical coordinate of each particle.
    """
    p   = np.arctan2(self.pos[:,1],self.pos[:,0])
    return p


  r = rxyz
  R = rxy

  ######################
  # spherical coord
  ######################


  def cart2sph(self,pos=None):
    """
    Transform carthesian coodinates x,y,z into spherical
    coordinates r,p,t
    Return a 3xn float array.
    """
    if pos is not None:
      x = pos[:,0]
      y = pos[:,1]
      z = pos[:,2]
    else:
      x = self.pos[:,0]
      y = self.pos[:,1]
      z = self.pos[:,2]

    r   = self.rxyz()
    rxy = self.rxy()
    #xp  = x*r/rxy           # x projection in the plane
    #yp  = y*r/rxy           # y projection in the plane
    #p   = np.arctan2(yp,xp)
    #t   = np.arcsin(z/r)
    p   = np.arctan2(y,x)
    t   = np.arctan2(rxy,z)

    return np.transpose(np.array([r,p,t])).astype(np.float32)

  def sph2cart(self,pos=None):
    """
    Transform spherical coordinates r,p,t into carthesian
    coodinates x,y,z
    Return a 3xn float array.
    """
    if pos is not None:
      r = pos[:,0]
      p = pos[:,1]
      t = pos[:,2]
    else:
      r = self.pos[:,0]
      p = self.pos[:,1]
      t = self.pos[:,2]

    x = r*np.sin(t)*np.cos(p)
    y = r*np.sin(t)*np.sin(p)
    z = r*np.cos(t)
    return np.transpose(np.array([x,y,z])).astype(np.float32)







  #################################
  # velocities
  #################################

  def vx(self):
    """
    Return a 1xn float array containing x velocity
    """
    return self.vel[:,0]

  def vy(self):
    """
    Return a 1xn float array containing y velocity
    """
    return self.vel[:,1]

  def vz(self):
    """
    Return a 1xn float array containing z velocity
    """
    return self.vel[:,2]


  def vn(self):
    """
    Return a 1xn float array that corresponds to
    the norm of velocities
    """
    return np.sqrt(self.vel[:,0]*self.vel[:,0] + self.vel[:,1]*self.vel[:,1] + self.vel[:,2]*self.vel[:,2])


  def vrxyz(self):
    """
    Return a 1xn float array that corresponds to
    the radial velocity in spherical system
    """
    r   = self.rxyz()
    return (self.pos[:,0]*self.vel[:,0] + self.pos[:,1]*self.vel[:,1] + self.pos[:,2]*self.vel[:,2])/r

  def Vr(self):
    """
    Return the radial velocies of particles
    The output is an 3xn float array.
    """
    xr = np.sqrt(self.pos[:,0]**2+self.pos[:,1]**2)
    vr = (self.pos[:,0]*self.vel[:,0] + self.pos[:,1]*self.vel[:,1]) / xr
    return vr


  def Vt(self):
    """
    Return the tangential velocies of particles
    The output is an 3xn float array.
    """
    xr = np.sqrt(self.pos[:,0]**2+self.pos[:,1]**2)
    vt = (self.pos[:,0]*self.vel[:,1] - self.pos[:,1]*self.vel[:,0]) / xr
    return vt

  def Vz(self):
    """
    Return a 1xn float array containing z velocity
    """
    return self.vel[:,2]


  ######################
  # cylindrical coord
  ######################

  def vel_cyl2cart(self,pos=None,vel=None):
    """
    Transform velocities in cylindrical coordinates vr,vt,vz into carthesian
    coodinates vx,vy,vz.
    Pos is the position of particles in cart. coord.
    Vel is the velocity in cylindrical coord.
    Return a 3xn float array.
    """
    return libutil.vel_cyl2cart(self.pos,self.vel)


  def vel_cart2cyl(self):
    """
    Transform velocities in carthesian coordinates vx,vy,vz into cylindrical
    coodinates vr,vz,vz.
    Pos is the position of particles in cart. coord.
    Vel is the velocity in cart. coord.
    Return a 3xn float array.
    """
    return libutil.vel_cart2cyl(self.pos,self.vel)


  #################################
  #
  # physical values
  #
  #################################

  def get_ns(self):
    """
    Return in an array the number of particles of each node.
    """
    ns = mpi.mpi_allgather(self.nbody)
    return ns


  def get_mass_tot(self):
    """
    Return the total mass of system.
    """
    mass_tot = mpi.mpi_sum(self.mass)
    return mass_tot

  def size(self):
    """
    Estimate the model size, using the inertial momentum
    """
    return max(self.minert())



  def cm(self):
    """
    Return the mass center of the model.
    The output is an 3x1 float array.
    """

    mtot = mpi.mpi_sum(self.mass.astype(FLOAT))
    cmx = mpi.mpi_sum(self.pos[:,0].astype(np.float64)*self.mass.astype(FLOAT)) / mtot
    cmy = mpi.mpi_sum(self.pos[:,1].astype(np.float64)*self.mass.astype(FLOAT)) / mtot
    cmz = mpi.mpi_sum(self.pos[:,2].astype(np.float64)*self.mass.astype(FLOAT)) / mtot

    return np.array([cmx,cmy,cmz])


  def get_histocenter(self,rbox=50,nb=500):
    """
    Return the position of the higher density region
    in x,y,z (not good)
    found by the function "histocenter".

    rbox	: size of the box
    nb		: number of bins in each dimension

    """

    rm = rbox/2.
    bins = np.arange(-rm,rm,float(2*rm)/float(nb))

    # histograms in x,y,z (cut the tail)
    hx = mpi.mpi_histogram(self.pos[:,0],bins)[:-1]
    hy = mpi.mpi_histogram(self.pos[:,1],bins)[:-1]
    hz = mpi.mpi_histogram(self.pos[:,2],bins)[:-1]


    # max in each dim
    dx = bins[np.argmax(hx)]
    dy = bins[np.argmax(hy)]
    dz = bins[np.argmax(hz)]

    return np.array([dx,dy,dz])


  def get_histocenter2(self,rbox=50,nb=64):
    """
    Return the position of the higher density region
    in x,y,z (not good)
    found by the function "histocenter".

    rbox	: size of the box
    nb		: number of bins in each dimension

    """

    # transformation -rbox->0, 0->nb/2, rbox->nb
    # y = (x+rbox)/(2*rbox)*nb

    pos = ( self.pos + [rbox,rbox,rbox] )/(2*rbox)	# 0 to 1
    pos = pos*[nb,nb,nb]				# 0 to nb

    pos = pos.astype(np.float32)
    mass = self.mass.astype(np.float32)

    mat = mapping.mkmap3d(pos/nb,mass,mass,(nb,nb,nb))

    # find max
    m = np.ravel(mat)
    arg = np.argmax(m)

    i = np.indices((nb,nb,nb))		# not that good
    ix = np.ravel(i[0])			# not that good
    iy = np.ravel(i[1])			# not that good
    iz = np.ravel(i[2])			# not that good
    ix = ix[arg]
    iy = iy[arg]
    iz = iz[arg]


    # transformation inverse
    # x = 2*rbox*(y/nb)-rbox

    dx = 2*rbox*(float(ix)/nb)-rbox
    dy = 2*rbox*(float(iy)/nb)-rbox
    dz = 2*rbox*(float(iz)/nb)-rbox


    return np.array([dx,dy,dz])


  def cv(self):
    """
    Return the center of the velocities of the model.
    The output is an 3x1 float array.
    """

    cmx = mpi.mpi_sum(self.vel[:,0]*self.mass) / self.mass_tot
    cmy = mpi.mpi_sum(self.vel[:,1]*self.mass) / self.mass_tot
    cmz = mpi.mpi_sum(self.vel[:,2]*self.mass) / self.mass_tot

    return np.array([cmx,cmy,cmz])


  def minert(self):
    """
    Return the diagonal of the intertial momentum.
    """
    mx = mpi.mpi_sum(self.pos[:,0]**2 *self.mass) / self.mass_tot
    my = mpi.mpi_sum(self.pos[:,1]**2 *self.mass) / self.mass_tot
    mz = mpi.mpi_sum(self.pos[:,2]**2 *self.mass) / self.mass_tot

    mx = np.sqrt(mx)
    my = np.sqrt(my)
    mz = np.sqrt(mz)

    return np.array([mx,my,mz])

  def inertial_tensor(self):
    """
    Return the inertial tensor.
    """
    Ixx = mpi.mpi_sum(self.mass * (self.y()**2 + self.z()**2))
    Iyy = mpi.mpi_sum(self.mass * (self.x()**2 + self.z()**2))
    Izz = mpi.mpi_sum(self.mass * (self.x()**2 + self.y()**2))


    Ixy = -mpi.mpi_sum(self.mass * self.x() * self.y())
    Ixz = -mpi.mpi_sum(self.mass * self.x() * self.z())
    Iyz = -mpi.mpi_sum(self.mass * self.y() * self.z())

    I = np.array( [[Ixx,Ixy,Ixz],[Ixy,Iyy,Iyz],[Ixz,Iyz,Izz]]  )

    return I





  def x_sigma(self):
    """
    Return the norm of the position dispersions.
    """

    x  = (self.pos - self.cm())
    x2 = x[:,0]**2 + x[:,1]**2 + x[:,2]**2
    x_s2 = mpi.mpi_sum( x2 *self.mass )/self.mass_tot
    x_s  = np.sqrt(x_s2)

    return x_s

  def v_sigma(self):
    """
    Return the norm of the velocity dispersions.
    """

    v  = (self.vel - self.cv())
    v2 = v[:,0]**2 + v[:,1]**2 + v[:,2]**2
    v_s2 = mpi.mpi_sum( v2 *self.mass )/self.mass_tot
    v_s  = np.sqrt(v_s2)

    return v_s


  def dx_mean(self):
    """
    Return the average distance between particles.
    """

    # 1) estimate the size of the system
    D = self.x_sigma()

    # 2) estimate the # of particules per unit volume
    n = self.nbody_tot/D

    # 3) estimate the average distance between particules
    l = 1./n**(1./3.)

    return l


  def dv_mean(self):
    """
    Return the average relative speed between particles.
    """

    # 1) estimate the size of the system
    D = self.v_sigma()

    # 2) estimate the # of particules per unit volume
    n = self.nbody_tot/D

    # 3) estimate the average distance between particules
    l = 1./n**(1./3.)

    return l



  def Ekin(self):
    """
    Return the total kinetic energy
    """
    E = 0.5 * mpi.mpi_sum (self.mass *  (self.vel[:,0]**2 + self.vel[:,1]**2 + self.vel[:,2]**2) )
    return E

  def ekin(self):
    """
    Return the total specific kinetic energy
    """
    #E = 0.5 * mpi.mpi_sum (             (self.vel[:,0]**2 + self.vel[:,1]**2 + self.vel[:,2]**2) )
    E = self.Ekin()/self.mass_tot
    return E

  def Epot(self,eps):
    """
    Return the total potential energy using the softening lenght eps.

    eps : softening

    WARNING : THIS FUNCTION DO NOT WORK IN MPI MODE
    """
    E = nbodymodule.epot(self.pos,self.mass,eps)
    return E

  def epot(self,eps):
    """
    Return the total specific potential energy using the softening lenght eps.

    eps : softening

    WARNING : THIS FUNCTION DO NOT WORK IN MPI MODE
    """
    e = nbodymodule.epot(self.pos,self.mass,eps)/self.mass_tot
    return e

  def L(self):
    """
    Return the angular momentum in x,y,z of all particles.
    The output is an 3xn float array.
    """
    l = nbodymodule.amxyz(self.pos,self.vel,self.mass)
    return l

  def l(self):
    """
    Return the specific angular momentum in x,y,z of all particles.
    The output is an 3xn float array.
    """
    l = nbodymodule.samxyz(self.pos,self.vel,self.mass)
    return l

  def Ltot(self):
    """
    Return the total angular momentum.
    The output is an 3x1 float array.
    """
    l = mpi.mpi_allreduce (nbodymodule.am(self.pos,self.vel,self.mass))
    #l = mpi.mpi_sum(self.L())
    return l

  def ltot(self):
    """
    Return the specific total angular momentum.
    The output is an 3x1 float array.
    """
    l = mpi.mpi_allreduce (nbodymodule.am(self.pos,self.vel,self.mass))/self.mass_tot
    #l = self.Ltot()/self.mass_tot
    return l

  def Pot(self,x,eps):
    """
    Return the potential at a given position, using the softening lenght eps.

    x	: position (array vector)
    eps : softening
    """

    if type(x) == np.ndarray:
      p = np.zeros(len(x),np.float32)
      for i in range(len(x)):
        p[i] = mpi.mpi_allreduce ( nbodymodule.potential(self.pos,self.mass,np.array(x[i],np.float32),eps) )
    else:
      p = mpi.mpi_allreduce ( nbodymodule.potential(self.pos,self.mass,np.array(x,np.float32),eps) )

    return p


  def TreePot(self,pos,eps,Tree=None):
    """
    Return the potential at a given position, using the softening lenght eps
    and using a tree.

    pos	: position (array vector)
    eps : softening
    Tree: gravitational tree if already computed

    WARNING : this function do not work in parallel

    """

    if Tree is None:
      self.Tree = Tree = self.getTree()


    pot = Tree.Potential(pos,eps)
    return pot



  def Accel(self,x,eps):
    """
    Return the acceleration at a given position, using the softening lenght eps.

    x	: position (array vector)
    eps : softening
    """



    if type(x) == np.ndarray:
      ax = np.zeros(len(x),np.float32)
      ay = np.zeros(len(x),np.float32)
      az = np.zeros(len(x),np.float32)
      for i in range(len(x)):
        ax[i],ay[i],az[i] = nbodymodule.acceleration(self.pos,self.mass,np.array(x[i],np.float32),eps)

      a = np.transpose(np.array([ax,ay,az],np.float32))

    else:
      ax,ay,az = nbodymodule.acceleration(self.pos,self.mass,np.array(x,np.float32),eps)

      ax = mpi.mpi_allreduce ( ax )
      ay = mpi.mpi_allreduce ( ay )
      az = mpi.mpi_allreduce ( az )

      a = np.array([ax,ay,az],np.float32)

    return a


  def TreeAccel(self,pos,eps,Tree=None):
    """
    Return the acceleration at a given position, using the softening lenght eps
    and using a tree.

    pos	: position (array vector)
    eps : softening
    Tree: gravitational tree if already computed

    WARNING : this function do not work in parallel

    """

    if Tree is None:
      self.Tree = Tree = self.getTree()


    acc = Tree.Acceleration(pos,eps)
    return acc


  def tork(self,acc):
    """
    Return the total tork on the system due to the force
    acting on each particle (acc).
    The output is an 3xn float array.

    acc  : 3xn float array
    """

    trk = mpi.mpi_allreduce ( nbodymodule.am(self.pos,np.array(acc,np.float32),self.mass) )

    return trk


  def dens(self,r=None,nb=25,rm=50):
    """
    Return the number density at radius r (supposing a spherical density distribution).
    If r is not specified, it is computed with nb and rm.
    The output is an n x 1 float array.

    !!! This routine do not use masses !!!

    r   : radius
    nb  : number of bins (size of the output)
    rm  : maximal radius
    """

    if r is not None:
      r = np.array(r,float)
    else:
      rmax = rm
      dr = rm/float(nb)
      r = np.arange(0.,rm,dr)

    xr = np.sqrt(self.pos[:,0]**2 +  self.pos[:,1]**2 + self.pos[:,2]**2)
    dens,r = np.histogram(xr,r)

    r1 = r[:-1]
    r2 = r[1:]
    dv = (4./3.)*np.pi*(r2**3-r1**3)

    dens = dens/dv          # surface density

    # take the mean
    r = (r1+r2)/2

    return r,mpi.mpi_allreduce(dens)

  def mdens(self,r=None,nb=25,rm=50):
    """
    Return the density at radius r (supposing a spherical density distribution).
    If r is not specified, it is computed with nb and rm.
    The output is an n x 1 float array.

    r   : radius
    nb  : number of bins (size of the output)
    rm  : maximal radius
    """

    if r is not None:
      r = np.array(r,float)
    else:
      rmax = rm
      dr = rm/float(nb)
      r = np.arange(0.,rm,dr)

    xr = np.sqrt(self.pos[:,0]**2 +  self.pos[:,1]**2 + self.pos[:,2]**2)
    dens = myNumeric.whistogram(xr.astype(float),self.mass.astype(float),r.astype(float))

    r1 = r[:-1]
    r2 = r[1:]
    dv = (4./3.)*np.pi*(r2**3-r1**3)
    dens = dens[:-1]/dv     # surface density

    # take the mean
    r = (r1+r2)/2

    return r,mpi.mpi_allreduce(dens)

  def mr(self,r=None,nb=25,rm=50):
    """
    Return the mass inside radius r (supposing a spherical density distribution).
    If r is not specified, it is computed with nb and rm.
    The output is an n x 1 float array.

    r   : radius
    nb  : number of bins (size of the output)
    rm  : maximal radius
    """

    if r is not None:
      r = np.array(r,float)
    else:
      rmax = rm
      dr = rm/float(nb)
      r = np.arange(0.,rm,dr)

    xr = self.rxyz()
    mr = myNumeric.whistogram(xr.astype(float),self.mass.astype(float),r.astype(float))
    mr = np.add.accumulate(mr)

    return r,mpi.mpi_allreduce(mr)

  def Mr_Spherical(self,nr=25,rmin=0,rmax=50):
    """
    Return the mass inside radius r (supposing a spherical density distribution).
    The output is 2 n x 1 float arrays.

    nr    : number of bins (size of the output)
    rmin  : minimal radius (this must be zero, instead it is wrong...)
    rmax  : maximal radius
    """

    rmin = float(rmin)
    rmax = float(rmax)

    shape = (nr,)
    val = np.ones(self.pos.shape).astype(np.float32)
    mass = self.mass.astype(np.float32)
    r	= self.rxyz()
    r   = (r-rmin)/(rmax-rmin)
    r	= r.astype(np.float32)

    # compute the map
    mr = mapping.mkmap1d(r,mass,val,shape).astype(float)

    # compute the radii
    rs = np.arange(0.,rmax,(rmax-rmin)/nr)

    # sum
    mr = np.add.accumulate(mr)

    return rs,mpi.mpi_allreduce(mr)


  def sdens(self,r=None,nb=25,rm=50):
    """
    Return the surface density at radius r.
    If r is not specified, it is computed with nb and rm.
    The output is an nx1 float array.

    !!! This routine do not uses masses !!!

    r   : radius
    nb  : number of bins (size of the output)
    rm  : maximal radius
    """

    if r is not None:
      r = np.array(r,float)
    else:
      rmax = rm
      dr = rm/float(nb)
      r = np.arange(0.,rm,dr)

    xr = np.sqrt(self.pos[:,0]**2 +  self.pos[:,1]**2)
    sdens,r = np.histogram(xr,r)

    r1 = r[:-1]
    r2 = r[1:]
    ds = np.pi*(r2**2-r1**2)
    sdens = sdens/ds        # surface density

    # take the mean
    r = (r1+r2)/2.

    return r,mpi.mpi_allreduce(sdens)

  def msdens(self,r=None,nb=25,rm=50):
    """
    Return the mass surface density at radius r.
    If r is not specified, it is computed with nb and rm.
    The output is an nx1 float array.

    r   : radius
    nb  : number of bins (size of the output)
    rm  : maximal radius
    """

    if r is not None:
      r = np.array(r,float)
    else:
      rmax = rm
      dr = rm/float(nb)
      r = np.arange(0.,rm,dr)

    xr = np.sqrt(self.pos[:,0]**2 +  self.pos[:,1]**2)
    sdens = myNumeric.whistogram(xr.astype(float),self.mass.astype(float),r.astype(float))

    r1 = r[:-1]
    r2 = r[1:]
    ds = np.pi*(r2**2-r1**2)
    sdens = sdens[:-1]/ds           # surface density

    # take the mean
    r = (r1+r2)/2.

    return r,mpi.mpi_allreduce(sdens)

  def sigma_z(self,r=None,nb=25,rm=50):
    """
    Return the vertical dispertion in z at radius r.
    If r is not specified, it is computed with nb and rm.
    The output is an nx1 float array.

    r   : radius
    nb  : number of bins (size of the output)
    rm  : maximal radius
    """

    if r is not None:
      r = np.array(r,float)
    else:
      rmax = rm
      dr = rm/float(nb)
      r = np.arange(0.,rm,dr)

    r,h = self.Histo(r,mode='sz')

    return r,h


  def sigma_vz(self,r=None,nb=25,rm=50):
    """
    Return the vertical dispertion in z at radius r.
    If r is not specified, it is computed with nb and rm.
    The output is an nx1 float array.

    r   : radius
    nb  : number of bins (size of the output)
    rm  : maximal radius
    """

    if r is not None:
      r = np.array(r,float)
    else:
      rmax = rm
      dr = rm/float(nb)
      r = np.arange(0.,rm,dr)

    r,h = self.Histo(r,mode='svz')

    return r,h




  def zprof(self,z=None,r=2.5,dr=0.5,nb=25,zm=5.):
    """
    Return the z-profile in a vector for a given radius

    !!! This routine works only if particles have equal masses !!!

    z   : bins in z (optional)
    r   : radius of the cut
    dr  : width in r of the cut
    nb  : number of bins (size of the output)
    zm  : maximal height
    """

    if z is not None:
      pass
    else:
      zmax = zm
      dz = 2.*zm/float(nb)
      z = np.arange(-zm,zm,dz)

    # select
    r1 = r-dr/2.
    r2 = r+dr/2.
    ann = self.selectc((self.rxy()>r1)*((self.rxy()<r2)))

    prof,z = np.histogram(ann.pos[:,2],z)

    z1 = z[:-1]
    z2 = z[1:]
    ds = z2-z1
    ds1 = np.pi*(r2**2-r1**2)

    prof = prof/(ds*ds1)
    z  =  z[:-1]

    return z,mpi.mpi_allreduce(prof)


  def sigma(self,r=None,nb=25.,rm=50.):
    """
    Return the 3 velocity dispersion (in cylindrical coordinates) and the mean azimuthal velocity curve.
    If r is not specified, it is computed with nb and rm.

    The output is a list (r,sr,st,sz,mt) of 5 $n\times 1$ float arrays,
    where r is the radius, sr the radial velocity dispersion, st, the azimuthal velocity dispersion,
    sz, the vertical velocity dispersion and mt, the mean azimuthal velocity curve.


    !!! This routine works only if particles have equal masses !!!

    r   : radius where to compute the values
    nb  : number of bins (size of the output)
    rm  : maximal radius

    return : r,sr,st,sz,mt
    """


    if r is not None:
      r1 = r[:-1]
      r2 = r[1:]
      r = (r1+r2)/2.0
    else:
      rmax = rm
      dr = rm/float(nb)

      r1 = np.arange(0,rmax,dr)
      r2 = np.arange(dr,rmax+dr,dr)
      r = (r1+r2)/2.

    sr = []
    sz = []
    st = []
    mt = []

    for i in range(len(r1)):

      #print i,len(r1)

      ann = self.selectc((self.rxy()>r1[i])*((self.rxy()<r2[i])))

      x = ann.pos[:,0]
      y = ann.pos[:,1]

      vx = ann.vel[:,0]
      vy = ann.vel[:,1]
      vz = ann.vel[:,2]

      xr = np.sqrt(x**2+y**2)
      vr = (x*vx + y*vy) / xr
      vt = (x*vy - y*vx) / xr

      # stand dev.
      if len(vr) > 1:
        sr.append(vr.std())
        st.append(vt.std())
        sz.append(vz.std())
        mt.append(vt.mean())
      else:
        sr.append(0.)
        st.append(0.)
        sz.append(0.)
        mt.append(0.)

    sr = np.array(sr,float)
    st = np.array(st,float)
    sz = np.array(sz,float)
    mt = np.array(mt,float)


    return r,sr,st,sz,mt




  def histovel(self,nb=100,vmin=None,vmax=None,mode='n'):
    """
    Return or plot the histrogram of the norm of velocities or of the radial velocities.

    The output is a list (r,h) of 2 nx1 float arrays,
    where r is the radius and h the values of the histogram.

    nb   : number of bins (size of the output)
    vmax : maximum velocity
    vmin : minimum velocity
    mode : 'n' (norme of the velocities)
           'r' (radial velocities)

    """

    if mode == 'r':
      v  = (self.pos[:,0]*self.vel[:,0] + self.pos[:,1]*self.vel[:,1]) / np.sqrt(self.pos[:,0]**2+self.pos[:,1]**2)
    elif mode == 'n':
      v = np.sqrt(self.vel[:,0]**2 + self.vel[:,1]**2 + self.vel[:,2]**2)


    if vmax is None : vmax = mpi.mpi_max(v)
    if vmin is None : vmin = mpi.mpi_min(v)

    bins = np.arange(vmin,vmax,(vmax-vmin)/float(nb))
    h = mpi.mpi_histogram(v,bins)

    return h,bins


  def zmodes(self,nr=32,nm=16,rm=32):
    """
    Compute the vertical modes of a model

    nm = 16   : number of modes
    nr = 32   : number of radius
    rm = 50   : max radius

    return

    r  : the radius used
    m  : the modes computed
    m1 : the matrix of the amplitude
    m2 : the matrix of the phases

    """

    ps = np.arange(-np.pi,np.pi+np.pi/(2.*nm),2*np.pi/(2.*nm))+np.pi	# phases
    R = np.arange(0,nr+1,1)*float(rm)/nr			# radius
    Rs = np.array([],float)


    r = self.rxy()

    m1 = np.array([],float)
    m2 = np.array([],float)

    # loop over all radius

    for i in range(len(R)-1):

      c = (r>=R[i])*(r<=R[i+1])
      an = self.selectc(c)

      if sum(c.astype(int))<=1:
        #print "less than 1 particle in the coupe",R[i]
        amp = np.zeros(len(ps)/2).astype(float)
        m1 = np.concatenate((m1,amp))
        m2 = np.concatenate((m2,amp))
        continue

      x = an.pos[:,0]
      y = an.pos[:,1]
      z = an.pos[:,2]
      t = np.arctan2(y,x)+np.pi

      zm = []
      ok = 0
      for j in range(len(ps)-1):
        c = (t>=ps[j])*(t<ps[j+1])

        if sum(c.astype(int))<=1:
          break

        zm.append(np.compress(c,z).mean())

      else:
        ok = 1

      if not ok:
        #print "less than 1 particle in the sub coupe",R[i]
        amp = np.zeros(len(ps)/2).astype(float)
        m1 = np.concatenate((m1,amp))
        m2 = np.concatenate((m2,amp))
        continue

      ps = ps.astype(float)
      zm = np.array(zm,float)

      t = t.astype(float)
      z = z.astype(float)

      # fourier decomposition
      f, amp, phi = pNbody.fourier.fourier(ps,zm)
      m1 = np.concatenate((m1,amp))
      m2 = np.concatenate((m2,phi))
      Rs = np.concatenate((Rs,np.array([(R[i]+R[i+1])/2.])))

    m = f*2*np.pi

    m1 = np.reshape(m1,(nr,nm))
    m2 = np.reshape(m2,(nr,nm))

    m1 = np.fliplr(m1)
    m2 = np.fliplr(m2)

    return Rs,m,m1,m2




  def dmodes(self,nr=32,nm=16,rm=32):
    """
    Compute the density modes of a model

    nm = 16   : number of modes
    nr = 32   : number of radius
    rm = 50   : max radius

    return

    r  : the radius used
    m  : the modes computed
    m1 : the matrix of the amplitude
    m2 : the matrix of the phases

    """

    ps = np.arange(-np.pi,np.pi+np.pi/(2.*nm),2*np.pi/(2.*nm))+np.pi	# phases
    R = np.arange(0,nr+1,1)*float(rm)/nr			# radius
    Rs = np.array([],float)


    r = self.rxy()


    m1 = np.array([],float)
    m2 = np.array([],float)

    # loop over all radius

    for i in range(len(R)-1):

      c = (r>=R[i])*(r<=R[i+1])
      an = self.selectc(c)

      if sum(c.astype(int))<=1:
        #print "less than 1 particle in the coupe",R[i]
        amp = np.zeros(len(ps)/2).astype(float)
        m1 = np.concatenate((m1,amp))
        m2 = np.concatenate((m2,amp))
        continue

      x = an.pos[:,0]
      y = an.pos[:,1]
      z = an.pos[:,2]
      t = np.arctan2(y,x)+np.pi

      dm = []
      ok = 0
      for j in range(len(ps)-1):
        c = (t>=ps[j])*(t<ps[j+1])

        if sum(c.astype(int))<=1:
          break

        dm.append(sum(c.astype(int)))

      else:
        ok = 1

      if not ok:
        #print "less than 1 particle in the sub coupe",R[i]
        amp = np.zeros(len(ps)/2).astype(float)
        m1 = np.concatenate((m1,amp))
        m2 = np.concatenate((m2,amp))
        Rs = np.concatenate((Rs,np.array([(R[i]+R[i+1])/2.])))
        continue

      ps = ps.astype(float)
      dm = np.array(dm,float)

      t = t.astype(float)
      z = z.astype(float)


      # fourier decomposition
      f, amp, phi = pNbody.fourier.fourier(ps,dm)
      phi = -phi
      m1 = np.concatenate((m1,amp))
      m2 = np.concatenate((m2,phi))
      Rs = np.concatenate((Rs,np.array([(R[i]+R[i+1])/2.])))

      '''
      #an.rotate(np.pi,axis='y')
      #an.show(view='xy',size=(20,20))

      print (R[i]+R[i+1])/2.,phi[2]+2*np.pi
      g = SM.plot()
      g.erase()
      g.limits(0,360,dm)
      g.box()
      g.connect(ps*180/np.pi,dm)

      fdm = amp[2]*np.cos(ps*2-phi[2])
      #fdm = amp[0]*np.cos(ps*0+phi[0])
      #for j in range(1,16):
      #  fdm = fdm + amp[j]*np.cos(ps*j+phi[j])

      g.ctype('red')
      g.connect(ps*180/np.pi,fdm)
      g.ctype('black')

      g.show()
      '''


    m = f*2*np.pi

    m1 = np.reshape(m1,(nr,nm))
    m2 = np.reshape(m2,(nr,nm))

    m1 = np.fliplr(m1)
    m2 = np.fliplr(m2)

    return Rs,m,m1,m2

  def getRadiusInCylindricalGrid(self,z,Rmax,nr=32,nt=32):
    '''
    Compute the radius in cells of a cylindrical grid
    '''

    irs = np.arange(nr)
    its = np.arange(nt)

    Radi = np.zeros((nt,nr),float)
    Rs   = irs*Rmax/float(nr)
    ts   = its*2*np.pi/float(nt)


    # use to compute values at the center of the cell
    dr = Rs[1]-Rs[0]
    dt = ts[1]-ts[0]

    for ir in irs:
      for it in its:


       R = ir*Rmax/float(nr) + dr/2.
       #t = it*2*np.pi/float(nt) + dt/2.

       Radi[it,ir]= R

    return Radi


  def getAccelerationInCylindricalGrid(self,eps,z,Rmax,nr=32,nt=32,UseTree=False):
    '''
    Compute the Acceleration in cells of a cylindrical grid
    '''

    irs = np.arange(nr)
    its = np.arange(nt)

    Accx = np.zeros((nt,nr),float)
    Accy = np.zeros((nt,nr),float)
    Accz = np.zeros((nt,nr),float)
    Rs   = irs*Rmax/float(nr)
    ts   = its*2*np.pi/float(nt)


    # use to compute values at the center of the cell
    dr = Rs[1]-Rs[0]
    dt = ts[1]-ts[0]

    # build the tree
    if UseTree:
      if self.Tree is None:
        self.Tree = self.getTree()

    for ir in irs:
      for it in its:


       R = ir*Rmax/float(nr) + dr/2.
       t = it*2*np.pi/float(nt) + dt/2.

       x = R*np.cos(t)
       y = R*np.sin(t)
       z = 0.0

       if UseTree:
         a = self.TreeAccel(np.array([[x,y,z]],np.float32),eps,Tree=None)

         Accx[it,ir]= a[0][0]
         Accy[it,ir]= a[0][1]
         Accz[it,ir]= a[0][2]
       else:
         a = self.Accel([x,y,z],eps)
         Accx[it,ir]= a[0]
         Accy[it,ir]= a[1]
         Accz[it,ir]= a[2]



    return Accx,Accy,Accz


  def getPotentialInCylindricalGrid(self,eps,z,Rmax,nr=32,nt=32,UseTree=False):
    '''
    Compute the potential in cells of a cylindrical grid
    '''

    irs = np.arange(nr)
    its = np.arange(nt)

    Phis = np.zeros((nt,nr),float)
    Rs   = irs*Rmax/float(nr)
    ts   = its*2*np.pi/float(nt)

    # build the tree
    if UseTree:
      if self.Tree is None:
        self.Tree = self.getTree()


    # use to compute values at the center of the cell
    dr = Rs[1]-Rs[0]
    dt = ts[1]-ts[0]

    for ir in irs:
      for it in its:


       R = ir*Rmax/float(nr) + dr/2.
       t = it*2*np.pi/float(nt) + dt/2.

       x = R*np.cos(t)
       y = R*np.sin(t)
       z = 0.0

       if UseTree:
         P = self.TreePot(np.array([[x,y,z]],np.float32),eps,Tree=None)
         Phis[it,ir]= P[0]
       else:
         Phis[it,ir]= self.Pot([x,y,z],eps)

    return Phis


  def getSurfaceDensityInCylindricalGrid(self,Rmax,nr=32,nt=32):
    '''
    Compute the surface density in cells of a cylindrical grid
    '''

    # r and t between 1 and 2
    r = self.rxy()/Rmax
    t = (self.phi_xy()+np.pi)/(2*np.pi)

    pos = np.transpose(np.array([t,r,r],np.float32))
    shape = (nt,nr)
    Sdens = libutil.GetMassMap(pos,self.mass,shape)

    # divide by the suface of a cell
    Rs = np.arange(nr+1)*Rmax/float(nr)
    R1 = Rs[:-1]
    R2 = Rs[1:]
    S = np.pi*(R2**2-R1**2)/float(nt)

    return Sdens/S

  def getNumberParticlesInCylindricalGrid(self,Rmax,nr=32,nt=32):
    '''
    Compute the number of particles in cells of a cylindrical grid
    '''

    # r and t between 1 and 2
    r = self.rxy()/Rmax
    t = (self.phi_xy()+np.pi)/(2*np.pi)

    pos = np.transpose(np.array([t,r,r],np.float32))
    shape = (nt,nr)
    Num = libutil.GetMassMap(pos,np.ones(len(pos)).astype(np.float32),shape)

    return Num


  def getRadialVelocityDispersionInCylindricalGrid(self,Rmax,nr=32,nt=32):
    '''
    Compute the radial velocity dispersion in cells of a cylindrical grid
    '''

    # r and t between 1 and 2
    r = self.rxy()/Rmax
    t = (self.phi_xy()+np.pi)/(2*np.pi)

    pos = np.transpose(np.array([t,r,r],np.float32))
    shape = (nt,nr)
    Sigmar = libutil.GetSigmaValMap(pos,self.mass,self.Vr(),shape)

    return Sigmar





  #################################
  #
  # geometrical operations
  #
  #################################

  def cmcenter(self):
    """
    Move the N-body object in order
    to center the mass center at the origin.
    """
    self.pos  = (self.pos - self.cm()).astype(np.float32)

  def cvcenter(self):
    """
    Center the center of velocities at the origin.
    """
    self.vel  = (self.vel - self.cv()).astype(np.float32)

  def histocenter(self,rbox=50,nb=500):
    """
    Move the N-body object in order to center the higher
    density region found near the mass center.
    The higher density region is determined whith density histograms.

    rbox	: box dimension, where to compute the histograms
    nb		: number of bins for the histograms

    """
    self.pos  = (self.pos - self.get_histocenter(rbox=rbox,nb=nb)).astype(np.float32)

  def histocenter2(self,rbox=50,nb=64):
    """
    Move the N-body object in order to center the higher
    density region found near the mass center.
    The higher density region is determined whith density histograms.

    rbox	: box dimension, where to compute the histograms
    nb		: number of bins for the histograms

    """
    self.pos  = (self.pos - self.get_histocenter2(rbox=rbox,nb=nb)).astype(np.float32)


  def hdcenter(self):
    """
    Move the N-body object in order to center the higher
    density region found.
    """

    if self.has_array('rho'):
      idx = mpi.mpi_argmax(self.rho)
      self.pos  = (self.pos - mpi.mpi_getval(self.pos,idx)).astype(np.float32)



  def translate(self,dx,mode='p'):
    """
    Translate the positions or the velocities of the object.

    dx    : shift (array vector)
    mode  : 'p' : translate positions
            'v' : translate velocities
    """
    if mode=='p':
      self.pos  = (self.pos + dx).astype(np.float32)
    elif mode=='v':
      self.vel  = (self.vel + dx).astype(np.float32)


  def rebox(self,boxsize=None,mode=None,axis='xyz'):
    """
    Translate the positions of the object in order that all particles
    being contained in a box of size boxsize.

    boxsize : size of the box
              if boxsize is not defined, we try first to see if self.boxsize
              is defined.

    mode    : type of reboxing
              None    : -> [0,boxsize]
              centred : -> [-boxsize/2,boxsize/2]
              [x,y,z] :
    """


    if boxsize is None:

      if self.has_var('boxsize'):
        boxsize = self.boxsize

    if boxsize is not None:

      if mode is None:

        if string.find(axis,'x')!=-1:
          self.pos[:,0] = np.where((self.pos[:,0]<0.0    ),self.pos[:,0]+boxsize,self.pos[:,0])
        if string.find(axis,'y')!=-1:
          self.pos[:,1] = np.where((self.pos[:,1]<0.0    ),self.pos[:,1]+boxsize,self.pos[:,1])
        if string.find(axis,'z')!=-1:
          self.pos[:,2] = np.where((self.pos[:,2]<0.0    ),self.pos[:,2]+boxsize,self.pos[:,2])

        if string.find(axis,'x')!=-1:
          self.pos[:,0] = np.where((self.pos[:,0]>boxsize),self.pos[:,0]-boxsize,self.pos[:,0])
        if string.find(axis,'y')!=-1:
          self.pos[:,1] = np.where((self.pos[:,1]>boxsize),self.pos[:,1]-boxsize,self.pos[:,1])
        if string.find(axis,'z')!=-1:
          self.pos[:,2] = np.where((self.pos[:,2]>boxsize),self.pos[:,2]-boxsize,self.pos[:,2])

      elif mode=='centred':

        if string.find(axis,'x')!=-1:
          self.pos[:,0] = np.where((self.pos[:,0]<=-boxsize/2.),self.pos[:,0]+boxsize,self.pos[:,0])
        if string.find(axis,'y')!=-1:
          self.pos[:,1] = np.where((self.pos[:,1]<=-boxsize/2.),self.pos[:,1]+boxsize,self.pos[:,1])
        if string.find(axis,'z')!=-1:
          self.pos[:,2] = np.where((self.pos[:,2]<=-boxsize/2.),self.pos[:,2]+boxsize,self.pos[:,2])

        if string.find(axis,'x')!=-1:
          self.pos[:,0] = np.where((self.pos[:,0]>  boxsize/2.),self.pos[:,0]-boxsize,self.pos[:,0])
        if string.find(axis,'y')!=-1:
          self.pos[:,1] = np.where((self.pos[:,1]>  boxsize/2.),self.pos[:,1]-boxsize,self.pos[:,1])
        if string.find(axis,'z')!=-1:
          self.pos[:,2] = np.where((self.pos[:,2]>  boxsize/2.),self.pos[:,2]-boxsize,self.pos[:,2])

      elif (type(mode)==np.ndarray) or (type(mode)==types.ListType):

        if string.find(axis,'x')!=-1:
          self.pos[:,0] = np.where((self.pos[:,0]<=mode[0]-boxsize/2.),self.pos[:,0]+boxsize,self.pos[:,0])
        if string.find(axis,'y')!=-1:
          self.pos[:,1] = np.where((self.pos[:,1]<=mode[1]-boxsize/2.),self.pos[:,1]+boxsize,self.pos[:,1])
        if string.find(axis,'z')!=-1:
          self.pos[:,2] = np.where((self.pos[:,2]<=mode[2]-boxsize/2.),self.pos[:,2]+boxsize,self.pos[:,2])

        if string.find(axis,'x')!=-1:
          self.pos[:,0] = np.where((self.pos[:,0]> mode[0]+boxsize/2.),self.pos[:,0]-boxsize,self.pos[:,0])
        if string.find(axis,'y')!=-1:
          self.pos[:,1] = np.where((self.pos[:,1]> mode[1]+boxsize/2.),self.pos[:,1]-boxsize,self.pos[:,1])
        if string.find(axis,'z')!=-1:
          self.pos[:,2] = np.where((self.pos[:,2]> mode[2]+boxsize/2.),self.pos[:,2]-boxsize,self.pos[:,2])





  def rotate_old(self,angle=0,mode='a',axis='x'):
    """
    Rotate the positions and/or the velocities of the object around a specific axis.

    angle : rotation angle in radian
    axis  : 'x'     : around x
            'y'     : around y
            'z'     : around z
          : [x,y,z] : around this axis
    mode  : 'p' : rotate only position
            'v' : rotate only velocities
            'a' : rotate both (default)
    """

    if type(axis) == type('a'):			# rotate around x,y or z

      if   axis =='x':
        if mode=='p' or mode=='a':
          self.pos=nbodymodule.rotx(angle,self.pos)
        if mode=='v' or mode=='a':
          self.vel=nbodymodule.rotx(angle,self.vel)

      elif axis =='y':
        if mode=='p' or mode=='a':
          self.pos=nbodymodule.roty(angle,self.pos)
        if mode=='v' or mode=='a':
          self.vel=nbodymodule.roty(angle,self.vel)

      elif axis =='z':
        if mode=='p' or mode=='a':
          self.pos=nbodymodule.rotz(angle,self.pos)
        if mode=='v' or mode=='a':
          self.vel=nbodymodule.rotz(angle,self.vel)

    else:					# rotate around a given axis

      # construction of the rotation matrix

      nxy = np.sqrt(axis[0]**2+axis[1]**2)

      theta_x = angle
      theta_z = 2.*np.pi - np.arctan2(axis[1],axis[0])
      theta_y = np.arctan2(axis[2],nxy)

      if mode=='p' or mode=='a':
        # rot in z
        self.pos=nbodymodule.rotz(theta_z,self.pos)
        # rot in y
        self.pos=nbodymodule.roty(theta_y,self.pos)
        # rot in x
        self.pos=nbodymodule.rotx(theta_x,self.pos)
        # rot in -y
        self.pos=nbodymodule.roty(-theta_y,self.pos)
        # rot in -z
        self.pos=nbodymodule.rotz(-theta_z,self.pos)

      if mode=='v' or mode=='a':
        # rot in z
        self.vel=nbodymodule.rotz(theta_z,self.vel)
        # rot in y
        self.vel=nbodymodule.roty(theta_y,self.vel)
        # rot in x
        self.vel=nbodymodule.rotx(theta_x,self.vel)
        # rot in -y
        self.vel=nbodymodule.roty(-theta_y,self.vel)
        # rot in -z
        self.vel=nbodymodule.rotz(-theta_z,self.vel)


  def rotate(self,angle=0,axis=[1,0,0],point=[0,0,0],mode='a'):
    """
    Rotate the positions and/or the velocities of the object around a specific axis
    defined by a vector and an point.

    angle : rotation angle in radian
    axis  : direction of the axis
    point : center of the rotation

    mode  : 'p' : rotate only position
            'v' : rotate only velocities
            'a' : rotate both (default)

    """

    if   axis=='x':
      axis = np.array([1,0,0],float)
    elif axis=='y':
      axis = np.array([0,1,0],float)
    elif axis=='z':
      axis = np.array([0,0,1],float)


    x = self.pos
    v = self.vel

    # center point
    x = x-point

    # construction of the rotation matrix
    norm = np.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
    if norm == 0:
      return x
    sn = np.sin(-angle/2.)

    e0 = np.cos(-angle/2.)
    e1 = axis[0]*sn/norm
    e2 = axis[1]*sn/norm
    e3 = axis[2]*sn/norm

    a = np.zeros((3,3),float)
    a[0,0] = e0**2 + e1**2 - e2**2 - e3**2
    a[1,0] = 2.*(e1*e2 + e0*e3)
    a[2,0] = 2.*(e1*e3 - e0*e2)
    a[0,1] = 2.*(e1*e2 - e0*e3)
    a[1,1] = e0**2 - e1**2 + e2**2 - e3**2
    a[2,1] = 2.*(e2*e3 + e0*e1)
    a[0,2] = 2.*(e1*e3 + e0*e2)
    a[1,2] = 2.*(e2*e3 - e0*e1)
    a[2,2] = e0**2 - e1**2 - e2**2 + e3**2
    a = a.astype(float)

    # multiply x and v
    if mode=='p':
      x = np.dot(x,a)
    elif mode=='v':
      v = np.dot(v,a)
    else:
      x = np.dot(x,a)
      v = np.dot(v,a)

    # decenter point
    x =  x+point

    self.pos = x.astype(np.float32)
    self.vel = v.astype(np.float32)


  def rotateR(self,R,mode='a'):
    """
    Rotate the model using the matrix R

    mode : 'p' : only position
           'v' : only velocities
           'a' : both (default)
    """

    # multiply x and v
    if mode=='p':
      self.pos = np.dot(self.pos,R)
    elif mode=='v':
      self.vel = np.dot(self.vel,R)
    else:
      self.pos = np.dot(self.pos,R)
      self.vel = np.dot(self.vel,R)



  def get_rotation_matrix_to_align_with_main_axis(self):
    """
    Get the rotation matrix used to rotate the object in order to align
    it's main axis with the axis of its inertial tensor.
    """

    # compute inertial tensor
    I = self.inertial_tensor()

    # find eigen values and vectors
    val,vec = np.linalg.eig(I)
    l1 = val[0]
    l2 = val[1]
    l3 = val[2]
    a1 = vec[:,0]
    a2 = vec[:,1]
    a3 = vec[:,2]


    # find Rm such that Rm*1,0,0 = a1
    #              that Rm*0,1,0 = a2
    #              that Rm*0,0,1 = a3

    Rm = np.transpose(np.array([a1,a2,a3]))

    return Rm




  def align_with_main_axis(self,mode='a'):
    """
    Rotate the object in order to align it's major axis with
    the axis of its inertial tensor.

    mode : 'p' : only position
           'v' : only velocities
           'a' : both (default)
    """

    # find rotation matrix
    R = self.get_rotation_matrix_to_align_with_main_axis()

    # apply it
    self.rotateR(R,mode)




  def align(self,axis,mode='a',sgn='+',fact=None):
    """
    Rotate the object in order to align the axis 'axis' with the z axis.

    axis : [x,y,z]
    mode : 'p' : only position
           'v' : only velocities
           'a' : both (default)
    sgn  : '+' : normal rotation
           '-' : reverse sense of rotation
    fact : int : factor to increase the angle
    """

    n = [axis[1], -axis[0],0.]
    theta =  np.arccos(axis[2]/np.sqrt(axis[0]**2+axis[1]**2+axis[2]**2))

    if sgn =='-': theta = -theta
    if fact is not None: theta = theta*fact
    self.rotate(angle=theta,mode=mode,axis=n)


  def align2(self,axis1=[1,0,0],axis2=[0,0,1],point=[0,0,0]):
    '''
    Rotate the object in order to align the axis 'axis' with the z axis.

    axis1 : [x,y,z]
    axis2 : [x,y,z]
    point : [x,y,z]
    '''

    a1 = np.array(axis1,float)
    a2 = np.array(axis2,float)

    a3 = np.array([0,0,0],float)
    a3[0] = a1[1]*a2[2] - a1[2]*a2[1]
    a3[1] = a1[2]*a2[0] - a1[0]*a2[2]
    a3[2] = a1[0]*a2[1] - a1[1]*a2[0]

    n1 = np.sqrt(a1[0]**2 + a1[1]**2 + a1[2]**2)
    n2 = np.sqrt(a2[0]**2 + a2[1]**2 + a2[2]**2)
    angle = np.arccos(np.inner(a1,a2)/(n1*n2))

    self.rotate(angle=angle,axis=a3,point=point)


  def spin(self,omega=None,L=None,j=None,E=None):
    """
    Spin the object with angular velocity "omega" (rigid rotation).
    Omega is a 1 x 3 array object

    If L (total angular momentum) is explicitely given, compute Omega from L (1 x 3 array object).

    omega : angular speed (array vector)
    L     : desired angular momentum
    j     : desired energy fraction in rotation
    E     : Total energy (without rotation)
    """

    # do nothing
    if L is None and omega is None and j is None:
      pass

    # use j and E (spin around z axis)
    if j is not None:
      if E is None:
        "spin : print you must give E"
      else:
        if (j > 1):
          self.log.write("spin : j must be less than 1")
          sys.exit()

        Erot = j*E/(1-j)

        omega = np.sqrt(2*Erot/mpi.mpi_sum(self.mass*self.rxy()**2) )
        omega = np.array([0,0,omega],np.float32)
        self.vel = nbodymodule.spin(self.pos,self.vel,omega)



    # use omega
    elif L is None and omega is not None:

      omega = np.array(omega,np.float32)
      self.vel = nbodymodule.spin(self.pos,self.vel,omega)

    # use L
    # Pfenniger 93
    elif L is not None:

      L = np.array(L,np.float32)
      aamx = L[0]
      aamy = L[1]
      aamz = L[2]

      x = self.pos[:,0]
      y = self.pos[:,1]
      z = self.pos[:,2]
      vx = self.vel[:,0]
      vy = self.vel[:,1]
      vz = self.vel[:,2]
      m  = self.mass

      Ixy = sum(m*x*y)
      Iyz = sum(m*y*z)
      Izx = sum(m*z*x)
      Ixx = sum(m*x*x)
      Iyy = sum(m*y*y)
      Izz = sum(m*z*z)

      Axx = Iyy+Izz
      Ayy = Izz+Ixx
      Azz = Ixx+Iyy
      Axy = -Ixy
      Ayz = -Iyz
      Azx = -Izx

      D = Axx*Ayy*Azz + 2*Axy*Ayz*Azx - Axx*Ayz**2 - Ayy*Azx**2 - Azz*Axy**2

      DLX = sum(m*(y*vz-z*vy))-aamx
      DLY = sum(m*(z*vx-x*vz))-aamy
      DLZ = sum(m*(x*vy-y*vx))-aamz

      Bxx = Ayy*Azz - Ayz**2
      Byy = Azz*Axx - Azx**2
      Bzz = Axx*Ayy - Axy**2
      Bxy = Azx*Ayz - Axy*Azz
      Byz = Axy*Azx - Ayz*Axx
      Bzx = Ayz*Axy - Azx*Ayy

      omega = np.array([0,0,0],np.float32)
      omega[0] = -(Bxx*DLX + Bxy*DLY + Bzx*DLZ)/D
      omega[1] = -(Bxy*DLX + Byy*DLY + Byz*DLZ)/D
      omega[2] = -(Bzx*DLX + Byz*DLY + Bzz*DLZ)/D

      self.vel = nbodymodule.spin(self.pos,self.vel,omega)


  #################################
  #
  # selection of particles
  #
  #################################

  def selectc(self,c,local=False):
    """
    Return an N-body object that contain only particles where the
    corresponding value in c is not zero.
    c is a nx1 Nbody array.

    c      : the condition vector
    local  : local selection (True) or global selection (False)
    """

    new = pNbody.Nbody(status='new',ftype=self.ftype,local=local)

    # now, copy all var linked to the model
    for name in self.get_list_of_vars():
      setattr(new, name, getattr(self,name))

    # here, we create ptype on the fly (used to create new.npart)
    #self.ptype = array([],int)
    #for i in range(len(self.npart)):
    #  self.ptype = np.concatenate( (self.ptype,np.ones(self.npart[i])*i) )

    # now, copy and compress all array linked to the model
    for name in self.get_list_of_array():
      vec = getattr(self,name)
      setattr(new, name, np.compress(c,vec,axis=0))

    # now, compute new.npart
    #new.npart = array([],int)
    #for i in range(len(self.npart)):
    #  c = (new.tpe==i)
    #  npart_i = sum(c.astype(int))
    #  new.npart = np.concatenate( (new.npart, npart_i ) )

    # check
    #if len(new.pos)!= sum(new.npart):
    #  pass

    # other vars
    new.init()

    return new


  def selecti(self,i,local=False):
    """
    Return an N-body object that contain only particles having
    their index (not id) in i.

    i      : vector containing indexes
    local  : local selection (True) or global selection (False)
    """

    new = pNbody.Nbody(status='new',ftype=self.ftype,local=local)

    # now, copy all var linked to the model
    for name in self.get_list_of_vars():
      setattr(new, name, getattr(self,name))

    # here, we create ptype on the fly (used to create new.npart)
    #self.ptype = array([],int)
    #for i in range(len(self.npart)):
    #  self.ptype = np.concatenate( (self.ptype,np.ones(self.npart[i])*i) )

    # now, copy and compress all array linked to the model
    for name in self.get_list_of_array():
      vec = getattr(self,name)
      setattr(new, name, vec[i])

    # now, compute new.npart
    #new.npart = array([],int)
    #for i in range(len(self.npart)):
    #  c = (new.tpe==i)
    #  npart_i = sum(c.astype(int))
    #  new.npart = np.concatenate( (new.npart, npart_i ) )

    # check
    #if len(new.pos)!= sum(new.npart):
    #  pass

    # other vars
    new.init()

    return new
  

  def sub(self,n1=0,n2=None):
    """
    Return an N-body object that have particles whith indicies in the range [n1:n2].

    n1  : number of the first particule
    n2	: number of the last particule

    Note : the first particle is 0
    """

    if n1 is None:
      n1 = 0
    if n2 is None:
      n2 = self.nbody

    if n2 <= n1:
      n2 = n1+1

    num = np.arange(self.nbody)
    return self.selectc((num>=n1)*(num<=n2))



  def reduc(self,n,mass=False):
    """
    Return an N-body object that contain a fraction 1/n of particles.

    n	: inverse of the fraction of particule to be returned
    """

    c = np.where(np.fmod(np.arange(self.nbody),n).astype(int)==0,1,0)

    nb = self.selectc(c)
    if mass:
      nb.mass = nb.mass * n

    return nb



  def selectp(self,lst=None,file=None,reject=False,local=False,from_num=True):
    """
    Return an N-body object that contain only particles with specific number id.

    The list of id's is given either by lst (nx1 int array) or
    by the name ("file") of a file containing the list of id's.

    lst	: vector list (integer)

    reject : True/False : if True, reject particles in lst (default = False)
    local  : local selection (True) or global selection (False)

    frum_num : if True, use self.num to select particules
               if False, use arange(self.nbody)
    """

    if lst is not None:
      lst = np.array(lst,int)

    if file is not None:
      lst = []
      f = open(file)
      while 1:
        try:
          lst.append(int(string.split(f.readline())[0]))
        except:
          break


      f.close()
      lst = np.array(lst,int)


    # 1) sort the list
    ys = np.sort(lst)

    # 2) sort index in current file
    if from_num:
      xs = np.sort(self.num)
      zs = np.take(np.arange(self.nbody),np.argsort(self.num))	# sort 0,1,2,n following xs (or self.num)
    else:
      xs = np.arange(self.nbody)

    # 3) apply mask on sorted lists (here, getmask need xs and ys to be sorted)
    m = myNumeric.getmask(xs.astype(int),ys.astype(int))
    if reject:
      m = np.logical_not(m)

    # 4) revert mask, following zs inverse transformation
    if from_num:
      c = np.take(m,np.argsort(zs))
    else:
      c = m

    new = self.selectc(c,local=local)
    return new

  def getindex(self,num):
    """
    Return an array of index of a particle from its specific number id.
    The array is empty if no particle corresponds to the specific number id.

    num : Id of the particle
    """

    idx = np.compress((self.num == num),np.arange(self.nbody))
    if len(idx)==1:
      return idx[0]
    else:
      return idx



  #################################
  #
  # add particles
  #
  #################################


  def append(self,solf,do_not_sort=False,do_init_num=True,do_not_change_num=False):
    """
    Add to the current N-body object, particles form the
    N-body object "new".

    solf : Nbody object
    """
    
    if do_not_change_num:
      do_init_num = False
      do_not_sort = True

    if solf.ftype != self.ftype:
      raise "append Error","files have different type"
      return

    if solf.get_list_of_array()  != self.get_list_of_array():
      raise "append Error","files have different arrays"
      return

    # loop over all types
    self_npart = self.npart
    solf_npart = solf.npart

    if len(self_npart) != len(self_npart):
      print "append : files have different mxnpart !"
      sys.exit()

    # compute numadd
    if not do_not_change_num:
      numadd = max(self.num)+1
      solf.num += numadd

    # add array linked to the model
    names = self.get_list_of_array()
    for name in names:

      vec1 = getattr(self,name)
      vec2 = getattr(solf,name)

      '''
      vec  = array([],np.float32)

      if vec1.ndim == 1:
        vec.shape = (0,)
      else:
        vec.shape = (0,3)


      # here, we guarantee the order of particles according to npart
      for i in np.arange(len(self_npart)):

        e11 = sum((np.arange(len(self_npart)) < i) * self_npart,0)
        e21 = sum((np.arange(len(solf_npart)) < i) * solf_npart,0)

        vec = np.concatenate((vec,vec1[e11:e11+self_npart[i]],vec2[e21:e21+solf_npart[i]]))

      '''

      vec = np.concatenate((vec1,vec2))
      setattr(self, name, vec)

    # remove numadd
    #solf.num -= numadd

    # here, we sort the particles, according to tpe
    if do_not_sort:
      pass
    else:
      sequence = self.tpe.argsort()

      for name in names:
        vec = getattr(self,name)
        vec = np.take(vec,sequence,axis=0)
        setattr(self, name, vec)


    self.nbody = self.nbody + solf.nbody

    if do_init_num:
      self.npart = self.get_npart()		# needed by self.get_num()
      self.npart_tot = self.get_npart_tot()	# needed by self.get_num()
      self.num = self.get_num()

    self.init()



  def __add__(self,solf,do_not_sort=False):

    # first copy self
    new = deepcopy(self)
    # now, add solf
    new.append(solf,do_not_sort)
    return new

  #################################
  #
  # take particles
  #
  #################################

  def take(self,vec=None):
    '''
    extract particles according to the vector vec

    vec : vector (default=self.num)
    '''

    new = pNbody.Nbody(status='new',ftype=self.ftype)

    if vec is None:
      vec = self.num


    sequence = vec

    # now, copy all var linked to the model
    for name in self.get_list_of_vars():
      setattr(new, name, getattr(self,name))


    # add array linked to the model
    for name in self.get_list_of_array():
      setattr(new, name, np.take(getattr(self,name),sequence,axis=0))

    #new.num = new.get_num()
    new.init()
    return new

  #################################
  #
  # sort particles
  #
  #################################

  def sort(self,vec=None):
    '''
    sort particles according to the vector vec

    vec : vector on which to sort (default=self.num)
    '''

    new = pNbody.Nbody(status='new',ftype=self.ftype)

    if vec is None:
      vec = self.num


    sequence = np.argsort(vec)

    # now, copy all var linked to the model
    for name in self.get_list_of_vars():
      setattr(new, name, getattr(self,name))


    # add array linked to the model
    for name in self.get_list_of_array():
      setattr(new, name, np.take(getattr(self,name),sequence,axis=0))

    #new.num = new.get_num()
    new.init()
    return new


  def sort_type(self):
    '''
    Contrary to sort, this fonction sort particles
    respecting their type.
    '''

    new = pNbody.Nbody(status='new',ftype=self.ftype)


    # now, copy all var linked to the model
    for name in self.get_list_of_vars():
      setattr(new, name, getattr(self,name))


    # add array linked to the model
    for name in self.get_list_of_array():

      #vec  = np.take(getattr(self,name),sequence,axis=0)
      vec  = np.array([],np.float32)
      vec1 = getattr(self,name)


      if vec1.ndim == 1:
        vec.shape = (0,)
      else:
        vec.shape = (0,3)


      # loop over all types
      npart = self.npart

      for i in np.arange(len(npart)):

        e11 = sum((np.arange(len(npart)) < i) * npart)

        sequence = np.argsort(self.num[e11:e11+npart[i]])

        vec = np.concatenate((vec,np.take(vec1[e11:e11+npart[i]],sequence,axis=0)))



      setattr(new, name, vec)


    new.num = new.get_num()
    new.init()


    return new



  #################################
  #
  # Tree and SPH functions
  #
  #################################

  def InitSphParameters(self,DesNumNgb=33,MaxNumNgbDeviation=3):

    self.DesNumNgb = DesNumNgb
    self.MaxNumNgbDeviation = MaxNumNgbDeviation
    self.Density = None
    self.Hsml = None

    if not self.has_var('Tree'):
      self.Tree = None


  def setTreeParameters(self,Tree,DesNumNgb,MaxNumNgbDeviation):

    if Tree is None:
      self.Tree = Tree = self.getTree()

    if DesNumNgb is None:
      DesNumNgb = self.DesNumNgb
    else:
      self.DesNumNgb = DesNumNgb

    if MaxNumNgbDeviation is None:
      MaxNumNgbDeviation = self.MaxNumNgbDeviation
    else:
      self.MaxNumNgbDeviation =  MaxNumNgbDeviation

    return  Tree,DesNumNgb,MaxNumNgbDeviation



  def getTree(self,force_computation=False,ErrTolTheta=0.8):
    '''
    Return a Tree object
    '''

    if self.Tree is not None and force_computation==False:
      return self.Tree
    else:

      print "create the tree : ErrTolTheta=",ErrTolTheta

      # decide if we use tree or ptree
      npart = np.array(self.npart)

      if mpi.mpi_NTask()>1:
        print "%d : use ptree"%(mpi.mpi_ThisTask())
        from pNbody import ptreelib
        self.Tree = ptreelib.Tree(npart=npart,pos=self.pos,vel=self.vel,mass=self.mass,num=self.num,tpe=self.tpe)
      else:
        from pNbody import treelib
        self.Tree = treelib.Tree(npart=npart,pos=self.pos,vel=self.vel,mass=self.mass,ErrTolTheta=ErrTolTheta)

      return self.Tree



  def get_rsp_approximation(self,DesNumNgb=None,MaxNumNgbDeviation=None,Tree=None):
    '''
    Return an aproximation of rsp, based on the tree.
    '''

    Tree,DesNumNgb,MaxNumNgbDeviation = self.setTreeParameters(Tree,DesNumNgb,MaxNumNgbDeviation)
    return Tree.InitHsml(DesNumNgb,MaxNumNgbDeviation)



  def ComputeSph(self,DesNumNgb=None,MaxNumNgbDeviation=None,Tree=None):
    '''
    Compute self.Density and self.Hsml using sph approximation
    '''

    Tree,DesNumNgb,MaxNumNgbDeviation = self.setTreeParameters(Tree,DesNumNgb,MaxNumNgbDeviation)

    if self.Hsml is None:
      if not self.has_array('rsp'):
        self.Hsml = self.get_rsp_approximation(DesNumNgb,MaxNumNgbDeviation,Tree)
      else:
        self.Hsml=self.rsp

    self.Density,self.Hsml = Tree.Density(self.pos,self.Hsml,DesNumNgb,MaxNumNgbDeviation)



  def ComputeDensityAndHsml(self,pos=None,Hsml=None,DesNumNgb=None,MaxNumNgbDeviation=None,Tree=None):
    '''
    Compute Density and Hsml (for a specific place)
    '''

    Tree,DesNumNgb,MaxNumNgbDeviation = self.setTreeParameters(Tree,DesNumNgb,MaxNumNgbDeviation)

    if pos is None:
      pos = self.pos

    if Hsml is None:
      Hsml = np.ones(len(pos)).astype(np.float32)

    Density,Hsml = Tree.Density(pos,Hsml,DesNumNgb,MaxNumNgbDeviation)

    return Density,Hsml



  def SphEvaluate(self,val,pos=None,vel=None,hsml=None,DesNumNgb=None,MaxNumNgbDeviation=None,Tree=None):
    '''
    Return an sph evaluation of the variable var
    '''

    Tree,DesNumNgb,MaxNumNgbDeviation = self.setTreeParameters(Tree,DesNumNgb,MaxNumNgbDeviation)

    if pos is None:
      pos = self.pos

    if vel is None:
      vel = self.vel

    if hsml is None:
      if self.Hsml is None:
        if not self.has_array('rsp'):
          self.Hsml = self.get_rsp_approximation(DesNumNgb,MaxNumNgbDeviation,Tree)
        else:
          self.Hsml=self.rsp
      hsml = self.Hsml


    if self.Density is None:
      if not self.has_array('rho'):
        self.Density = self.SphDensity(DesNumNgb,MaxNumNgbDeviation,Tree)
      else:
        self.Density=self.rho

    if type(val) == np.ndarray:
      val = Tree.SphEvaluate(pos,hsml,self.Density,val,DesNumNgb,MaxNumNgbDeviation)
    else:
      if   val =='div':
        val = Tree.SphEvaluateDiv(pos,vel,hsml,self.Density,DesNumNgb,MaxNumNgbDeviation)
      elif val =='rot':
        val = Tree.SphEvaluateRot(pos,vel,hsml,self.Density,DesNumNgb,MaxNumNgbDeviation)
      elif val =='ngb':
        val = Tree.SphEvaluateNgb(pos,hsml,DesNumNgb,MaxNumNgbDeviation)

    return val


  #################################
  #
  # sph functions
  #
  #################################

  def weighted_numngb(self,num):
    '''
    num = particle where to compute weighted_numngb
    see Springel 05
    '''

    def wk1(hinv3,u):
      KERNEL_COEFF_1=2.546479089470
      KERNEL_COEFF_2=15.278874536822
      wk = hinv3 * (KERNEL_COEFF_1 + KERNEL_COEFF_2 * (u - 1) * u * u)
      return wk

    def wk2(hinv3,u):
      KERNEL_COEFF_5=5.092958178941
      wk = hinv3 * KERNEL_COEFF_5 * (1.0 - u) * (1.0 - u) * (1.0 - u)
      return wk

    def getwk(r,h):
      # we do not exclude the particle itself
      u = r/h
      hinv3 = 1./h**3
      wk = np.where((u<0.5),wk1(hinv3,u),wk2(hinv3,u))
      wk = np.where((r<h),wk,0)
      return wk

    i = self.getindex(num)
    h = self.rsp[i]
    r = np.sqrt( (self.pos[:,0]-self.pos[i,0])**2 + (self.pos[:,1]-self.pos[i,1])**2 + (self.pos[:,2]-self.pos[i,2])**2 )

    # compute wk for these particle
    wk = getwk(r,h)

    NORM_COEFF=4.188790204786	# 4/3.*np.pi
    return NORM_COEFF *sum(wk)*h**3


  def real_numngb(self,num):
    '''
    number of particles wor wich r<h
    '''
    i = self.getindex(num)
    h = self.rsp[i]
    r = np.sqrt( (self.pos[:,0]-self.pos[i,0])**2 + (self.pos[:,1]-self.pos[i,1])**2 + (self.pos[:,2]-self.pos[i,2])**2 )

    n = sum(np.where((r<h),1,0))
    return n


  def usual_numngb(self,num):
    '''
    usual way to compute the number of neighbors
    '''
    i = self.getindex(num)
    h = self.rsp[i]
    r = np.sqrt( (self.pos[:,0]-self.pos[i,0])**2 + (self.pos[:,1]-self.pos[i,1])**2 + (self.pos[:,2]-self.pos[i,2])**2 )

    c = (r<h)
    M1 = sum(c*self.mass)/sum(c.astype(int))	# mean mass
    M2 = 4/3.*np.pi*h**3 * self.rho[i]		# total mass
    n = M2/M1
    return n




  #################################
  #
  # redistribution of particles
  #
  #################################


  def redistribute(self):
    """

    This function redistribute particles amoung all nodes in order to
    have a similar number of particles per nodes

    """


    if mpi.NTask>1:


      list_of_array = self.get_list_of_array()

      # loop over all particles type
      npart = self.npart
      new_npart = npart

      for i in range(len(npart)):

        #if i==0:

          nparts = mpi.mpi_allgather(npart[i])
          nparts = np.array(nparts)

          if mpi.mpi_IsMaster():
            ex_table = mpi.mpi_GetExchangeTable(nparts)
            ex_table = mpi.mpi_bcast(ex_table,0)

          else:
            ex_table = None
            ex_table = mpi.mpi_bcast(ex_table,0)



          # send particles
          for toTask in range(mpi.NTask):
            if ex_table[mpi.ThisTask,toTask] > 0:
              n_elt  = ex_table[mpi.ThisTask,toTask]
              #print "%d send %d to %d"%(mpi.ThisTask,n_elt,toTask)

              # first_elt = first elt of the current block
              first_elt = sum((np.arange(len(new_npart)) < i) * new_npart)
              # update npart
              new_npart[i] = new_npart[i] - n_elt


              # loop over all vect erd,mass,num,pos,rho,rsp,u,vel
              for name in list_of_array:

                  vec = getattr(self,name)
                  sub_vec = vec[first_elt:first_elt+n_elt]

                  if len(sub_vec) != n_elt:
                    print "redistribute error :"
                    print "node %d should send len=%d got len=%d"%(mpi.ThisTask,n_elt,len(sub_vec))
                    sys.exit()

                  mpi.mpi_send(name,toTask)
                  mpi.mpi_send(sub_vec,toTask)

                  #self.pos = np.concatenate( (self.pos[:first_elt],self.pos[first_elt+n_elt:]) )
                  setattr(self, name, np.concatenate( (vec[:first_elt],vec[first_elt+n_elt:]) ) )



          # recieve particles
          for fromTask in range(mpi.NTask):
            if ex_table[fromTask,mpi.ThisTask] > 0:
              n_elt = ex_table[fromTask,mpi.ThisTask]
              #print "%d get %d from %d"%(mpi.ThisTask,n_elt,fromTask)

              # first_elt = first elt of the current block
              first_elt = sum((np.arange(len(new_npart)) < i) * new_npart)
              # update npart
              new_npart[i] = new_npart[i] + n_elt

              # loop over all vect
              for name in list_of_array:

                  # first, check name
                  send_name =  mpi.mpi_recv(fromTask)
                  if send_name != name:
                    raise "Task %d FromTask %d, %s != %s"%(mpi.mpi_ThisTask(),fromTask,send_name,name)

                  vec = getattr(self,name)
                  sub_vec = mpi.mpi_recv(fromTask)
                  if len(sub_vec) != n_elt:
                    print "redistribute error :"
                    print "node %d should recive len=%d got len=%d"%(mpi.ThisTask,n_elt,len(sub_vec))
                    sys.exit()

                  #self.pos = np.concatenate( (vec[:first_elt],sub_vec,vec[first_elt:]) )
                  setattr(self, name, np.concatenate( (vec[:first_elt],sub_vec,vec[first_elt:]) ) )



          self.init()


  def ExchangeParticles(self):
    '''
    Exchange particles betwee procs, using peano-hilbert decomposition computed in ptree
    '''
    if self.Tree is None:
      self.Tree = self.getTree()

    # get num and procs from the Tree
    num,procs = self.Tree.GetExchanges()

    # compute the transition table T
    H,bins =  np.histogram(procs,np.arange(mpi.mpi_NTask()))
    T = mpi.mpi_AllgatherAndConcatArray(H)
    T.shape = (mpi.mpi_NTask(),mpi.mpi_NTask())


    # loop over all numpy vectors

    list_of_array = self.get_list_of_array()
    # loop over all vect
    for name in list_of_array:
      if name != "num":
        setattr(self, name, mpi.mpi_ExchangeFromTable(T,procs,num,getattr(self,name),copy(self.num)) )

    # do num at the end
    self.num = mpi.mpi_ExchangeFromTable(T,procs,num,self.num,copy(self.num))


    self.init()


  def SendAllToAll(self):
    '''
    Send all particles to all nodes
    at the end of the day, all nodes have the same nbody object
    '''

    nbs = []
    for i in xrange(mpi.NTask-1):

      prev = (mpi.ThisTask-i-1)%mpi.NTask
      next = (mpi.ThisTask+i+1)%mpi.NTask

      nbs.append(mpi.mpi_sendrecv(self,dest=next,source=prev))

    for nbi in nbs:
      self = self + nbi

    return self


  #################################
  #
  # specific parallel functions
  #
  #################################

  def gather_pos(self):
    '''
    Gather in a unique array all positions of all nodes.
    '''
    return self.gather_vec(self.pos)

  def gather_vel(self):
    '''
    Gather in a unique array all velocites of all nodes.
    '''
    return self.gather_vec(self.vel)

  def gather_mass(self):
    '''
    Gather in a unique array all mass of all nodes.
    '''
    return self.gather_vec(self.mass)

  def gather_num(self):
    '''
    Gather in a unique array all num of all nodes.
    '''
    return self.gather_vec(self.num)


  def gather_vec(self,vec):
    '''
    Gather in a unique array all vectors vec of all nodes.
    '''

    # here, we assume that we have a vector npart
    # giving the number of particles per type

    vec_all = np.array([],vec.dtype)
    if vec.ndim==1:
      vec_all.shape = (0,)
    else:
      vec_all.shape = (0,vec.shape[1])

    i1 = 0

    npart = self.npart
    for i in range(len(npart)):

      i2 = i1 + npart[i]

      if (i1!=i2):
        vec_all = np.concatenate((vec_all,mpi.mpi_AllgatherAndConcatArray(vec[i1:i2])))

      i1 = i1 + npart[i]

    return vec_all




  #################################
  #
  # graphical operations
  #
  #################################


  def display(self,*arg,**kw):
    '''
    Display the model
    '''

    if kw.has_key('palette'):
      palette = kw['palette']
    else:
      palette = None

    if kw.has_key('save'):
      save = kw['save']
    else:
      save = None

    if kw.has_key('marker'):
      marker = kw['marker']
    else:
      marker = None

    params = libutil.extract_parameters(arg,kw,self.defaultparameters)
    mat,matint,mn_opts,mx_opts,cd_opts = self.Map(params)

    if mpi.mpi_IsMaster():
      if save is not None:
        if os.path.splitext(save)[1] == ".fits":
          io.WriteFits(np.transpose(mat).astype(np.float32),save, None)
          return


    if palette is not None:
      libutil.mplot(matint,palette=palette,save=save,marker=marker)
    else:
      libutil.mplot(matint,save=save,marker=marker)


  def show(self,*arg,**kw):
    '''
    Display the model
    this is an alias to display
    '''
    self.display(*arg,**kw)


  def Map(self,*arg,**kw):
    '''
    Return 2 final images (float and int)
    '''

    params = libutil.extract_parameters(arg,kw,self.defaultparameters)


    mn_opts = []
    mx_opts = []
    cd_opts = []

    if self.nbody==0 and mpi.mpi_NTask()==1:
      mat = np.zeros(params['shape'],np.float32)
      matint = mat.astype(int)
      mn_opts.append(params['mn'])
      mx_opts.append(params['mx'])
      cd_opts.append(params['cd'])
      return mat,matint,mn_opts,mx_opts,cd_opts


    # compute map
    mat = self.CombiMap(params)


    # set ranges
    matint,mn_opt,mx_opt,cd_opt = libutil.set_ranges(mat,scale=params['scale'],cd=params['cd'],mn=params['mn'],mx=params['mx'])
    mn_opts.append(mn_opt)
    mx_opts.append(mx_opt)
    cd_opts.append(cd_opt)

    # add contour
    if params['l_color'] != 0:
      matint = contours(mat,matint,params['l_n'],params['l_min'],params['l_max'],params['l_kx'],params['l_ky'],params['l_color'],params['l_crush'])

    # add box and ticks
    if params['b_weight'] != 0:
      matint = add_box(matint,shape=params['shape'],size=params['size'],center=None,box_opts=(params['b_weight'],params['b_xopts'],params['b_yopts'],params['b_color']))


    return mat,matint,mn_opts,mx_opts,cd_opts



  def CombiMap(self,*arg,**kw):
    '''
    Return an image in form of a matrix (nx x ny float array).
    Contrary to ComputeMap, CombiMap compose different output of ComputeMap.

    pos  : position of particles (moment 0)

    sr   : dispertion in r    (with respect to xp)
    svr  : dispertion in vr

    vxyr : mean velocity in the plane
    svxyr: dispertion in vxy

    vtr  : mean tangential velocity in the plane
    svtr : dispertion in vt

    szr : ratio sigma z/sigma r

    '''

    params = libutil.extract_parameters(arg,kw,self.defaultparameters)
    mode = params['mode']


    #if mode == 'pos':
    #  mat = self.ComputeMap(params)

    if mode == 'm':
      mat = self.ComputeMap(params)

    elif mode == 'sr':
      mat = self.ComputeSigmaMap(params,mode1='r',mode2='r2')

    elif mode == 'svr':
      mat = self.ComputeSigmaMap(params,mode1='vr',mode2='vr2')

    elif mode == 'svx':
      mat = self.ComputeSigmaMap(params,mode1='vx',mode2='vx2')

    elif mode == 'svy':
      mat = self.ComputeSigmaMap(params,mode1='vy',mode2='vy2')

    elif mode == 'svxyr':
      mat = self.ComputeSigmaMap(params,mode1='vxyr',mode2='vxyr2')


    elif mode == 'svtr':
      mat = self.ComputeSigmaMap(params,mode1='vtr',mode2='vtr2')


    elif mode == 'szr':				# could be simplified

      m0 = self.ComputeMap(params,mode='m')
      m1 = self.ComputeMap(params,mode='vr')
      m2 = self.ComputeMap(params,mode='vr2')

      m1 = np.where(m0==0,0,m1)
      m2 = np.where(m0==0,0,m2)
      m0 = np.where(m0==0,1,m0)
      mat = m2/m0 - (m1/m0)**2
      mat_sz = np.sqrt(np.clip(mat,0,1e10))

      m0 = self.ComputeMap(params,mode='m')
      m1 = self.ComputeMap(params,mode='vxyr')
      m2 = self.ComputeMap(params,mode='vxyr2')

      m1 = np.where(m0==0,0,m1)
      m2 = np.where(m0==0,0,m2)
      m0 = np.where(m0==0,1,m0)
      mat = m2/m0 - (m1/m0)**2
      mat_sr = np.sqrt(np.clip(mat,0,1e10))

      mat_sz = np.where(mat_sr==0,0,mat_sz)
      mat_sr = np.where(mat_sr==0,1,mat_sr)
      mat = mat_sz/mat_sr


    elif mode == 'lum':
      mat = self.ComputeMap(params,mode='lum')


    else:
      mat = self.ComputeMeanMap(params,mode1=mode)

    return mat


  def ComputeMeanMap(self,*arg,**kw):
    """
    Compute the mean map of an observable.
    """
    params = libutil.extract_parameters(arg,kw,self.defaultparameters)

    if kw.has_key('mode1'):
      mode1 = kw['mode1']
    else:
      raise "ComputeMeanMap :","you must give parameter mode1"

    m0 = self.ComputeMap(params,mode='0')
    m1 = self.ComputeMap(params,mode=mode1)

    m1 = np.where(m0==0,0,m1)
    m0 = np.where(m0==0,1,m0)
    mat = m1/m0
    return mat


  def ComputeSigmaMap(self,*arg,**kw):
    """
    Compute the sigma map of an observable.
    """
    params = libutil.extract_parameters(arg,kw,self.defaultparameters)

    if kw.has_key('mode1'):
      mode1 = kw['mode1']
    else:
      raise "ComputeMeanMap","you must give parameter mode1"

    if kw.has_key('mode2'):
      mode2 = kw['mode2']
    else:
      raise "ComputeMeanMap","you must give parameter mode2"

    m0 = self.ComputeMap(params,mode='0')
    m1 = self.ComputeMap(params,mode=mode1)
    m2 = self.ComputeMap(params,mode=mode2)
    m1 = np.where(m0==0,0,m1)
    m2 = np.where(m0==0,0,m2)
    m0 = np.where(m0==0,1,m0)
    mat = m2/m0 - (m1/m0)**2
    mat = np.sqrt(np.clip(mat,0,1e10))
    return mat


  def ComputeMap(self,*arg,**kw):
    '''
    Return an image in form of a matrix (nx x ny float array)

    obs         : position of observer
    x0          : eye position
    xp          : focal position
    alpha       : angle of the head
    view        : 'xy' 'xz' 'yz'

    eye         : 'right' 'left'
    dist_eye    : distance between eyes

    mode	: mode of map
    space       : pos or vel

    persp       : 'on' 'off'
    clip        : (near,far)
    size        : (maxx,maxy)

    cut         : 'yes' 'no'

    frsp	: factor for rsp
    shape       : shape of the map

    '''


    params = libutil.extract_parameters(arg,kw,self.defaultparameters)
    obs         = params['obs']
    x0          = params['x0']
    xp          = params['xp']
    alpha       = params['alpha']
    mode        = params['mode']
    view        = params['view']
    r_obs       = params['r_obs']
    eye         = params['eye']
    dist_eye    = params['dist_eye']
    foc         = params['foc']
    space       = params['space']
    persp       = params['persp']
    clip        = params['clip']
    size        = params['size']
    shape       = params['shape']
    cut         = params['cut']
    frsp        = params['frsp']
    filter_name = params['filter_name']
    filter_opts = params['filter_opts']

    # 0)
    if libutil.getvaltype(mode)=='normal':
      val = libutil.getval(self,mode=mode,obs=obs)

    # 1) get observer position
    if obs is None:
      obs = geometry.get_obs(x0=x0,xp=xp,alpha=alpha,view=view,r_obs=r_obs)

    # 2) expose the model	# !!! as in self.expose we use Nbody() this must be called by each Task
    nb,obs = self.expose(obs,eye,dist_eye,foc=foc,space=space)

    if self.nbody > 0:

      # 3) compute val
      if libutil.getvaltype(mode)=='in projection':
        val = libutil.getval(nb,mode=mode,obs=obs)

      # 4) projection transformation
      if persp == 'on':
        zp = - nb.pos[:,2]                        # save dist obs-point
        pos = geometry.frustum(nb.pos,clip,size)
      else:
        pos = geometry.ortho(nb.pos,clip,size)

      # 5) keep only particles in 1:1:1

      if not self.has_array('rsp'):               # bad !!!
        self.rsp = None

      if cut=='yes':
        if self.rsp is not None:
          if params['rendering']=='map':
            pos,(mass,rsp,val,zp) = geometry.boxcut(pos,[self.mass,self.rsp,val,zp])
          else:
            pos,(mass,rsp,val,zp) = geometry.boxcut_segments(pos,[self.mass,self.rsp,val,zp])
        else:
          if params['rendering']=='map':
            pos,(mass,val,zp) = geometry.boxcut(pos,[self.mass,val,zp])
          else:
            pos,(mass,val,zp) = geometry.boxcut_segments(pos,[self.mass,val,zp])
          rsp = None
      else:
        mass = self.mass
        rsp  = self.rsp

      if len(pos)!=0:

        # 6) scale rsp and scale mass
        if frsp!= 0:
          if (rsp is None) or (sum(rsp)==0):
            rsp = np.ones(len(pos),np.float32)

          if persp == 'on':

            fact = 1/(zp+clip[0])

            # rsp is distance dependant...
            rsp = rsp * fact
            rsp = rsp.astype(np.float32)

            # mass is distance dependant...
            mass = mass*fact**2
            mass = mass.astype(np.float32)


          rsp = rsp*frsp                           # multiply with the factor
          self.log.write( "rsp : min = %10.5f max = %10.5f mean = %10.5f"%(min(rsp),max(rsp),rsp.mean()) )
          rsp = np.clip(rsp,0,100)
          self.log.write( "rsp : min = %10.5f max = %10.5f mean = %10.5f"%(min(rsp),max(rsp),rsp.mean()) )

          rsp = rsp.astype(np.float32)
        else:
          rsp = None

        # 7) viewport transformation : (x,y) -> ((0,1),(0,1))
        pos = geometry.viewport(pos,shape=None)
        pos = pos.astype(np.float32)

        # 8) render : map or lines
        if params['rendering']=='map':
          if rsp is not None:
            # default one
            mat =  mapping.mkmap2dsph(pos,mass,val,rsp,shape)

            # new with kernel in 2d
            #mat =  mkmap2dksph(pos,mass,val,rsp,shape)

            # kernel in 3d
            #mat =  mapping.mkmap3dksph(pos,mass,val,rsp,(shape[0],shape[1],shape[0]))
            #mat = sum(mat,axis=2)

            #mat =  mapping.mkmap3dsph(pos,mass,val,rsp,(shape[0],shape[1],shape[0]))
            #mat = sum(mat,axis=2)

            #print "--->",sum(np.ravel(mat))

          else:
            mat =  mapping.mkmap2d(pos,mass,val,shape)
        elif params['rendering']=='mapcubic':
          if rsp is not None:
            mat =  mapping.mkmap2dncub(pos,mass,val,rsp,shape)
          else:
            raise "rsp need to be defined"

        elif params['rendering']=='polygon':
          pos = pos * np.array([params['shape'][0],params['shape'][1] ,0])
          mat = np.zeros(params['shape'],np.float32)
          mat = draw_polygon(mat,pos[:,0],pos[:,1],1)

        elif params['rendering']=='lines':
          pos = pos * np.array([params['shape'][0],params['shape'][1] ,0])
          mat = np.zeros(params['shape'],np.float32)
          mat = draw_lines(mat,pos[:,0],pos[:,1],1)

        elif params['rendering']=='segments':
          pos = pos * np.array([params['shape'][0],params['shape'][1] ,0])
          mat = np.zeros(params['shape'],np.float32)
          mat = draw_segments(mat,pos[:,0],pos[:,1],1,zp)

        elif params['rendering']=='points':
          pos = pos * np.array([params['shape'][0],params['shape'][1] ,0])
          mat = np.zeros(params['shape'],np.float32)
          mat = draw_points(mat,pos[:,0],pos[:,1],1)


        elif params['rendering']=='polygon2':
          pos = pos * np.array([params['shape'][0],params['shape'][1] ,0])
          mat = np.zeros(params['shape'],np.float32)
          mat = draw_polygonN(mat,pos[:,0],pos[:,1],1,2)

        elif params['rendering']=='polygon4':
          pos = pos * np.array([params['shape'][0],params['shape'][1] ,0])
          mat = np.zeros(params['shape'],np.float32)
          mat = draw_polygonN(mat,pos[:,0],pos[:,1],1,4)

        elif params['rendering']=='polygon10':
          pos = pos * np.array([params['shape'][0],params['shape'][1] ,0])
          mat = np.zeros(params['shape'],np.float32)
          mat = draw_polygonN(mat,pos[:,0],pos[:,1],1,10)

        elif params['rendering'][:8]=='polygon#':
          n = int(params['rendering'][8:])
          pos = pos * np.array([params['shape'][0],params['shape'][1] ,0])
          mat = np.zeros(params['shape'],np.float32)
          mat = draw_polygonN(mat,pos[:,0],pos[:,1],1,n)


        else: # compute a map
          if rsp is not None:
            mat =  mapping.mkmap2dsph(pos,mass,val,rsp,shape)
          else:
            mat =  mapping.mkmap2d(pos,mass,val,shape)



      # there is no particles (after 5)
      else:
        mat = np.zeros(params['shape'],np.float32)


    # there is no particles
    else:
      mat = np.zeros(params['shape'],np.float32)

    # 9) sum mat over all proc
    #mat = mpi.mpi_allreduce(mat)				# could be more efficient if only the master get the final mat
    mat = mpi.mpi_allreduce(mat)

    # 10) filter matrix
    if mpi.mpi_IsMaster():
      if params['filter_name'] is not None:
        mat = libutil.apply_filter(mat,name=filter_name,opt=filter_opts)

    return mat





  def ComputeObjectMap(self,*arg,**kw):
    '''

    * * * IN DEVELOPPEMENT : allow to draw an object like a box, a grid... * * *


    Return an image in form of a matrix (nx x ny float array)

    obs         : position of observer
    x0          : eye position
    xp          : focal position
    alpha       : angle of the head
    view        : 'xy' 'xz' 'yz'

    eye         : 'right' 'left'
    dist_eye    : distance between eyes

    mode	: mode of map
    space       : pos or vel

    persp       : 'on' 'off'
    clip        : (near,far)
    size        : (maxx,maxy)

    cut         : 'yes' 'no'

    frsp	: factor for rsp
    shape       : shape of the map

    '''



    # here, nb must represent a geometric object

    # ob

    # expose : -> must use ob instead of self
    #		--> we can give explicitely pos and vel

    # ensuite, le nb est le bon






    params = libutil.extract_parameters(arg,kw,self.defaultparameters)
    obs         = params['obs']
    x0          = params['x0']
    xp          = params['xp']
    alpha       = params['alpha']
    mode        = params['mode']
    view        = params['view']
    r_obs       = params['r_obs']
    eye         = params['eye']
    dist_eye    = params['dist_eye']
    foc         = params['foc']
    space       = params['space']
    persp       = params['persp']
    clip        = params['clip']
    size        = params['size']
    shape       = params['shape']
    cut         = params['cut']
    frsp        = params['frsp']
    filter_name = params['filter_name']
    filter_opts = params['filter_opts']

    # 0)
    if libutil.getvaltype(mode)=='normal':
      val = libutil.getval(self,mode=mode,obs=obs)

    # 1) get observer position
    if obs is None:
      obs = geometry.get_obs(x0=x0,xp=xp,alpha=alpha,view=view,r_obs=r_obs)

    # 2) expose the model	# !!! as in self.expose we use Nbody() this must be called by each Task
    nb,obs = self.expose(obs,eye,dist_eye,foc=foc,space=space)

    if self.nbody > 0:

      # 3) compute val
      if libutil.getvaltype(mode)=='in projection':
        val = libutil.getval(nb,mode=mode,obs=obs)

      # 4) projection transformation
      if persp == 'on':
        zp = - nb.pos[:,2]                        # save dist obs-point
        pos = geometry.frustum(nb.pos,clip,size)
      else:
        pos = geometry.ortho(nb.pos,clip,size)

      # 5) keep only particles in 1:1:1

      if not self.has_array('rsp'):               # bad !!!
        self.rsp = None

      if cut=='yes':
        if self.rsp is not None:
          pos,(mass,rsp,val,zp) = geometry.boxcut(pos,[self.mass,self.rsp,val,zp])
        else:
          pos,(mass,val,zp) = geometry.boxcut(pos,[self.mass,val,zp])
          rsp = None
      else:
        mass = self.mass
        rsp  = self.rsp

      if len(pos)!=0:

        # 6) scale rsp and scale mass
        if frsp!= 0:
          if (rsp is None) or (sum(rsp)==0):
            rsp = np.ones(len(pos),np.float32)

          if persp == 'on':

            fact = 1/((zp-clip[0])+ 2*clip[0])

            # rsp is distance dependant...
            rsp = rsp * fact
            rsp = rsp.astype(np.float32)

            # mass is distance dependant...
            mass = mass*fact**2
            mass = mass.astype(np.float32)


          rsp = rsp*frsp                           # multiply with the factor
          self.log.write( "rsp : min = %10.5f max = %10.5f mean = %10.5f"%(min(rsp),max(rsp),rsp.mean()) )
          rsp = np.clip(rsp,0,100)
          self.log.write( "rsp : min = %10.5f max = %10.5f mean = %10.5f"%(min(rsp),max(rsp),rsp.mean()) )

          rsp = rsp.astype(np.float32)
        else:
          rsp = None


        # 7) viewport transformation : (x,y) -> ((0,1),(0,1))
        pos = geometry.viewport(pos,shape=None)
        pos = pos.astype(np.float32)


        # 8) get the map
        #if rsp is not None:
        #  mat =  mkmap2dsph(pos,mass,val,rsp,shape)
        #else:
        #  mat =  mkmap2d(pos,mass,val,shape)
        #
        # empty matrix
        mat = np.zeros(params['shape'],np.float32)
        #for po in pos:
        #  i = int(po[0]*params['shape'][0])
        #  j = int(po[1]*params['shape'][1])
        #  mat[i,j]=255

        pos = pos * [ params['shape'][0],params['shape'][1],1 ]

        x0 = pos[0][0]
        y0 = pos[0][1]
        x1 = pos[1][0]
        y1 = pos[1][1]
        mat = libutil.draw_line(mat,x0,x1,y0,y1,255)
        #mat = libutil.draw_cube(mat,pos,255)



      # there is no particles (after 5)
      else:
        mat = np.zeros(params['shape'],np.float32)


    # there is no particles
    else:
      mat = np.zeros(params['shape'],np.float32)

    # 9) sum mat over all proc
    mat = mpi.mpi_allreduce(mat)		# may be inefficient, better use reduce ?

    # 10) filter matrix
    if mpi.mpi_IsMaster():
      if params['filter_name'] is not None:
        mat = apply_filter(mat,name=filter_name,opt=filter_opts)

    return mat























  def expose(self,obs,eye=None,dist_eye=None,foc=None,space='pos',pos=None,vel=None):
    """
    Rotate and translate the object in order to be seen as if the
    observer was in x0, looking at a point in xp.

    obs         : observer matrix
    eye		: 'right' or 'left'
    dist_eye    : distance between eyes (separation = angle)
    space       : pos or vel
    foc         : focal

    """

    # create a minimal copy of self
    if pos is not None and vel is not None:
      obj = pNbody.Nbody(status='new',p_name='none',pos=pos,vel=vel,mass=None,ftype='gadget')
    else:
      obj = pNbody.Nbody(status='new',p_name='none',pos=self.pos,vel=self.vel,mass=None,ftype='gadget')

    if space=='vel':
      obj.pos = self.vel

    # first : put x0 at the origin
    obj.translate(- obs[0])
    obs = obs - obs[0]

    # second : anti-align e1 with z
    obj.align2(         axis1=obs[1],axis2=[0,0,-1])
    obs = geometry.align(obs,axis1=obs[1],axis2=[0,0,-1])

    # third : align e3 with y
    obj.align2(         axis1=obs[3],axis2=[0,1,0])
    obs = geometry.align(obs,axis1=obs[3],axis2=[0,1,0])


    # fourth if eye is defined
    if  eye=='right':

      if foc is None or foc==0:	# simple translation (wee look at infini)
        obj.translate([-dist_eye,0,0])  # not /2 for compatibility with glups

      else:
        Robs = foc
        phi = -np.arctan(dist_eye/foc)
        obj.rotate(         angle=-phi,axis=[0,1,0],point=[0,0,-Robs])


    elif eye=='left':

      if foc is None or foc==0:	# simple translation (wee look at infini)
        obj.translate([+dist_eye,0,0])  # not /2 for compatibility with glups

      else:
        Robs = foc
        phi = -np.arctan(dist_eye/foc)
        obj.rotate(         angle=+phi,axis=[0,1,0],point=[0,0,-Robs])

    return obj,obs




  '''

  def getvxy(self,shape=(256,256),size=(30.,30.),center=(0.,0.,0.),view='xz',vn=8.,vmax=0.1,color=1):

    self.log.write( "the result may be incertain (in development)" )

    # choice of the view
    if   view=='xz':
      view=1
    elif view=='xy':
      view=2
    elif view=='yz':
      view=3
    elif view!='xz'and view!='xy'and view!='yz':
      view=1


    dx =   mapone(self.pos,self.mass,self.vel[:,0],shape,size,center,view)   * vn/vmax
    dy = - mapone(self.pos,self.mass,self.vel[:,2],shape,size,center,view)   * vn/vmax

    # mask
    mask = fromfunction(lambda x,y: (np.fmod(x,vn) + np.fmod(y,vn))==0 ,shape)

    # points de depart
    x0 = np.indices(shape)[0] + int(vn/2.)
    y0 = np.indices(shape)[1] + int(vn/2.)

    # points d'arrivee
    x1 = x0 + dx.astype(int)
    y1 = y0 + dy.astype(int)

    # truncation
    x1 = np.clip(x1,0,shape[0])
    y1 = np.clip(y1,0,shape[1])

    # compress
    mask = mask*(x1!=x0)*(y1!=y0)
    mask = np.ravel(mask)
    x0 = compress(mask,np.ravel(x0))
    x1 = compress(mask,np.ravel(x1))
    y0 = compress(mask,np.ravel(y0))
    y1 = compress(mask,np.ravel(y1))

    # trace lines
    mat = np.zeros(shape,np.float32)
    color = array(color,int8)[0]
    for i in range(len(x0)):
      create_line(mat,x0[i],y0[i],x1[i],y1[i],color)
      create_line(mat,x0[i],y0[i],x0[i]+1,y0[i]+1,color)
      create_line(mat,x0[i],y0[i],x0[i]+1,y0[i]  ,color)
      create_line(mat,x0[i],y0[i],x0[i]  ,y0[i]+1,color)

    return mat.astype(int8)

  '''


  #################################
  #
  # 1d histograms routines
  #
  #################################


  ###########################
  def Histo(self,bins,mode='m',space='R'):
  ###########################

    histo = self.CombiHisto(bins,mode=mode,space=space)

    # take the mean
    bins1 = bins[:-1]
    bins2 = bins[1:]
    bins = (bins1+bins2)/2.

    return bins,mpi.mpi_allreduce(histo)


  ###########################
  def CombiHisto(self,bins,mode='m',space='R'):
  ###########################

    if mode == 'm':
      histo = self.ComputeHisto(bins,mode='0',space=space)

    elif mode == 'sz':
      histo = self.ComputeSigmaHisto(bins,mode1='z',mode2='z2',space=space)

    elif mode == 'svz':
      histo = self.ComputeSigmaHisto(bins,mode1='vz',mode2='vz2',space=space)

    elif mode == 'svt':
      histo = self.ComputeSigmaHisto(bins,mode1='vt',mode2='vt2',space=space)

    elif mode == 'svr':
      histo = self.ComputeSigmaHisto(bins,mode1='vr',mode2='vr2',space=space)


    elif mode == 'vt':
      histo = self.ComputeMeanHisto(bins,mode1='vt',space=space)

    elif mode == 'vr':
      histo = self.ComputeMeanHisto(bins,mode1='vr',space=space)

    elif mode == 'vz':
      histo = self.ComputeMeanHisto(bins,mode1='vz',space=space)



    else:
      print "unknown mode %s"%(mode)

    return histo



  #################################
  def ComputeMeanHisto(self,bins,mode1,space):
  #################################
    """
    Compute the mean map of an observable.
    """

    h0 = self.ComputeHisto(bins,mode='0',space=space)
    h1 = self.ComputeHisto(bins,mode=mode1,space=space)
    h1 = np.where(h0==0,0,h1)
    h0 = np.where(h0==0,1,h0)
    h = h1/h0
    return h


  #################################
  def ComputeSigmaHisto(self,bins,mode1,mode2,space):
  #################################
    """
    Compute the histogram of an observable.
    """

    h0 = self.ComputeHisto(bins,mode='0',space=space)
    h1 = self.ComputeHisto(bins,mode=mode1,space=space)
    h2 = self.ComputeHisto(bins,mode=mode2,space=space)
    h1 = np.where(h0==0,0,h1)
    h2 = np.where(h0==0,0,h2)
    h0 = np.where(h0==0,1,h0)
    h = h2/h0 - (h1/h0)**2
    h = np.sqrt(np.clip(h,0,1e10))
    return h

  #################################
  def ComputeHisto(self,bins,mode,space):
  #################################
    '''
    Compute and histogram
    '''

    # set space
    if   space == 'R':
      x = self.rxy()
    elif space == 'r':
      x = self.rxyz()



    # set mode
    if   mode == 'm' or mode=='0':
      v = self.mass

    elif mode == 'z':
      v = self.mass*self.z()

    elif mode == 'z2':
      v = self.mass*self.z()**2

    elif mode == 'vz':
      v = self.mass*self.vz()

    elif mode == 'vz2':
      v = self.mass*self.vz()**2

    elif mode == 'vt':
      v = self.mass*self.Vt()

    elif mode == 'vt2':
      v = self.mass*self.Vt()**2

    elif mode == 'vr':
      v = self.mass*self.Vr()

    elif mode == 'vr2':
      v = self.mass*self.Vr()**2

    else:
      print "unknown mode %s"%(mode)


    histo = myNumeric.whistogram(x.astype(float),v.astype(float),bins.astype(float))
    return histo


  ############################################
  #
  # Routines to get velocities from positions
  #
  ############################################



  def Get_Velocities_From_Virial_Approximation(self,select=None,vf=1.,eps=0.1,UseTree=True,Tree=None,ErrTolTheta=0.5):
    '''
    This routine does not work ! Do not use it, or check !
    '''


    if select is not None:
      nb_sph = self.select(select)
    else:
      nb_sph = self


    # build the Tree for nb
    self.getTree(force_computation=True,ErrTolTheta=ErrTolTheta)

    # compute potential
    pot = 0.5*self.TreePot(nb_sph.pos,eps)
    # virial approximation to get the velocities
    sigmasp = np.sqrt(-pot/3*vf)

    # compute accel
    acc = self.TreeAccel(nb_sph.pos,eps)
    pot =   (acc[:,0]*nb_sph.pos[:,0] + acc[:,1]*nb_sph.pos[:,1] + acc[:,2]*nb_sph.pos[:,2])
    # virial approximation to get the velocities
    sigmas = np.sqrt(-pot/3*vf)

    # avoid negative values
    sigmas = np.where( (pot>0),sigmasp, sigmas )



    # generate velocities
    vx = sigmas*np.random.standard_normal([nb_sph.nbody])
    vy = sigmas*np.random.standard_normal([nb_sph.nbody])
    vz = sigmas*np.random.standard_normal([nb_sph.nbody])
    nb_sph.vel = np.transpose(array([vx,vy,vz])).astype(np.float32)

    return nb_sph


  def Get_Velocities_From_AdaptativeSpherical_Grid(self,select=None,eps=0.1,n=1000,UseTree=True,Tree=None,phi=None,ErrTolTheta=0.5):
    '''
     Computes velocities using the jeans equation in spherical coordinates.
     An adaptative grid is set automatically.
    '''

    if select is not None:
      nb_sph = self.select(select)
    else:
      nb_sph = self


    # create the adaptiative grid and compute rho
    r = nb_sph.rxyz()
    a = r.argsort()

    x = np.take(nb_sph.pos[:,0],a)
    y = np.take(nb_sph.pos[:,1],a)
    z = np.take(nb_sph.pos[:,2],a)
    mass = np.take(nb_sph.mass,a)
    r = np.sqrt( x**2 + y**2 + z**2 )

    n_bins     = int((nb_sph.nbody+1)/n + 1)

    rs    = []
    rsmin = []
    rsmax = []
    rhos  = []
    ns    = []


    for i in xrange(n_bins):

      jmin = i*n
      jmax = i*n + n

      jmin = min(jmin,nb_sph.nbody-1)
      jmax = min(jmax,nb_sph.nbody-1)

      if jmin!=jmax:
        rr = r[jmin:jmax]
        mm = mass[jmin:jmax]

        rmean = rr.mean()
        rmin  = rr.min()
        rmax  = rr.max()

        rs.append(rmean)
        rsmin.append(rmin)
        rsmax.append(rmax)

        # density
        rho =  sum(mm)/(4/3.*np.pi*(rmax**3-rmin**3))

        rhos.append(rho)

        # number

        ns.append(len(rr))


    r = np.array(rs)
    rsmin = np.array(rsmin)
    rsmax = np.array(rsmax)
    rho = np.array(rhos)
    dr = rsmax-rsmin

    nn = np.array(ns)


    # build the Tree for nb
    self.getTree(force_computation=True,ErrTolTheta=ErrTolTheta)

    # compute potential
    x = r
    y = np.zeros(len(r))
    z = np.zeros(len(r))
    pos = np.transpose(np.array([x,y,z])).astype(np.float32)
    phi = self.TreePot(pos,eps)


    # compute sigma
    sigma = libdisk.get_1d_Sigma_From_Rho_Phi(rho=rho,phi=phi,r=r,dr=dr)

    # generate velocities for all particles
    sigmas = lininterp1d(nb_sph.rxyz().astype(np.float32),r.astype(np.float32),sigma.astype(np.float32))

    vx = sigmas*np.random.standard_normal([nb_sph.nbody])
    vy = sigmas*np.random.standard_normal([nb_sph.nbody])
    vz = sigmas*np.random.standard_normal([nb_sph.nbody])
    nb_sph.vel = np.transpose(np.array([vx,vy,vz])).astype(np.float32)

    # here we should limit the speed according to max speed
    phis = lininterp1d(nb_sph.rxyz().astype(np.float32),r.astype(np.float32),phi.astype(np.float32))



    vm = 0.95*np.sqrt(-2*phis)
    vn = nb_sph.vn()
    vf = np.where(vn>vm,vm/vn,1)
    vf.shape = (len(vf),1)
    nb_sph.vel = nb_sph.vel * vf

    # other info
    phi
    dphi  = libgrid.get_First_Derivative(phi,r)
    vcirc = libdisk.Vcirc(r,dphi)


    stats = {}
    stats['r']     = r
    stats['nn']    = nn
    stats['phi']   = phi
    stats['rho']   = rho
    stats['sigma'] = sigma
    stats['vc']    = vcirc

    return nb_sph,phi,stats



  def Get_Velocities_From_Spherical_Grid(self,select=None,eps=0.1,nr=128,rmax=100.0,UseTree=True,Tree=None,phi=None,ErrTolTheta=0.5,g=None,gm=None,NoDispertion=False,omega=None):
    '''
    Computes velocities using the jeans equation in spherical coordinates.
    '''

    if select is not None:
      nb_sph = self.select(select)
    else:
      nb_sph = self


    # build the Tree for nb
    self.getTree(force_computation=True,ErrTolTheta=ErrTolTheta)


    # create the grid
    G = libgrid.Spherical_1d_Grid(rmin=0,rmax=rmax,nr=nr,g=g,gm=gm)


    if phi is None:
      phi = G.get_PotentialMap(self,eps=eps,UseTree=UseTree)

    r	= G.get_r()
    rho = G.get_DensityMap(nb_sph)
    nn  = G.get_NumberMap(nb_sph)

    # dr
    dr  = G.get_r(offr=1)-G.get_r(offr=0)

    # compute sigma
    sigma = libdisk.get_1d_Sigma_From_Rho_Phi(rho=rho,phi=phi,r=r,dr=dr)


    # correct sigma in case of rotation (we assume the rotation around z)
    if omega is not None:
      print "add rotation"

      e_jeans = 0.5*sigma*sigma
      e_rot   = 0.5*r**2 * omega**2

      e = e_jeans - e_rot


      if (e<0).any():
        print "at some radius the kinetic specifig energy is less than zero\nYou should decrease omega."
      e = np.where(e<0,0,e)

      sigma = np.sqrt(2*e)



    # generate velocities for all particles
    sigmas = G.get_Interpolation(nb_sph.pos,sigma)

    if NoDispertion:
      vx = sigmas*np.ones(nb_sph.nbody)
      vy = sigmas*np.ones(nb_sph.nbody)
      vz = sigmas*np.ones(nb_sph.nbody)
    else:
      vx = sigmas*np.random.standard_normal([nb_sph.nbody])
      vy = sigmas*np.random.standard_normal([nb_sph.nbody])
      vz = sigmas*np.random.standard_normal([nb_sph.nbody])

    nb_sph.vel = np.transpose(np.array([vx,vy,vz])).astype(np.float32)


    # do not spin
    # add rotation
    #if omega is not None:
    #  nb_sph.spin(omega=array([0,0,omega]))



    # here we should limit the speed according to max speed
    phis = G.get_Interpolation(nb_sph.pos,phi)
    vm = 0.95*np.sqrt(-2*phis)
    vn = nb_sph.vn()
    vf = np.where(vn>vm,vm/vn,1)
    vf.shape = (len(vf),1)
    nb_sph.vel = nb_sph.vel * vf

    # other info
    phi
    dphi  = libgrid.get_First_Derivative(phi,r)
    vcirc = libdisk.Vcirc(r,dphi)


    stats = {}
    stats['r']     = r
    stats['nn']    = nn
    stats['phi']   = phi
    stats['rho']   = rho
    stats['sigma'] = sigma
    stats['vc']    = vcirc

    return nb_sph,phi,stats



  def Get_Velocities_From_Cylindrical_Grid(self,select='disk',disk=('gas','disk'),eps=0.1,nR=32,nz=32,nt=2,Rmax=100,zmin=-10,zmax=10,params=[None,None,None],UseTree=True,Tree=None,Phi=None,ErrTolTheta=0.5,AdaptativeSoftenning=False,g=None,gm=None,NoDispertion=False):
    '''
    Computes velocities using the jeans equation in cylindrical coordinates.
    '''

    mode_sigma_z = params[0]
    mode_sigma_r = params[1]
    mode_sigma_p = params[2]

    if params[0] is None:
      mode_sigma_z = {"name":"jeans","param":None}
    if params[1] is None:
      mode_sigma_r = {"name":"toomre","param":1.0}
    if params[2] is None:
      mode_sigma_p = {"name":"epicyclic_approximation","param":None}

    nb_cyl = self.select(select)		# current component
    nb_dis = self.select(disk)			# disk component, for Q computation


    # build the Tree for nb
    self.getTree(force_computation=True,ErrTolTheta=ErrTolTheta)

    # create the grid
    G = libgrid.Cylindrical_2drz_Grid(rmin=0,rmax=Rmax,nr=nR,zmin=zmin,zmax=zmax,nz=nz,g=g,gm=gm)

    R,z   = G.get_rz()

    ####################################
    # compute Phi in a 2d rz grid
    ####################################
    # here, we could use Acc instead
    Phi = G.get_PotentialMap(self,eps=eps,UseTree=UseTree,AdaptativeSoftenning=AdaptativeSoftenning)
    Phi = libgrid.get_Symetrisation_Along_Axis(Phi,axis=1)
    #Accx,Accy,Accz  = libgrid.get_AccelerationMap_On_Cylindrical_2dv_Grid(self,nR,nz,Rmax,zmin,zmax,eps=eps)
    #Ar = np.sqrt(Accx**2+Accy**2)

    ####################################
    # compute Phi (z=0) in a 2d rt grid
    ####################################
    Grt = libgrid.Cylindrical_2drt_Grid(rmin=0,rmax=Rmax,nr=nR,nt=nt,z=0,g=g,gm=gm)
    Accx,Accy,Accz = Grt.get_AccelerationMap(self,eps=eps,UseTree=UseTree,AdaptativeSoftenning=AdaptativeSoftenning)
    Ar = np.sqrt(Accx**2+Accy**2)
    Ar = np.sum(Ar,axis=1)/nt
    Rp,tp = Grt.get_rt()

    Phi0  = Phi[:,nz/2]			# not used
    dPhi0  = Ar
    d2Phi0 = libgrid.get_First_Derivative(dPhi0,R)


    # density
    rho = G.get_DensityMap(nb_cyl,offz=-0.5)
    rho = libgrid.get_Symetrisation_Along_Axis(rho,axis=1)

    # number per bin
    nn = G.get_NumberMap(nb_cyl,offz=-0.5)

    Sden  = G.get_SurfaceDensityMap(nb_cyl,offz=-0.5)
    Sdend = G.get_SurfaceDensityMap(nb_dis,offz=-0.5)


    # compute frequencies (in the plane)
    kappa = libdisk.Kappa(R,dPhi0,d2Phi0)
    omega = libdisk.Omega(R,dPhi0)
    vcirc = libdisk.Vcirc(R,dPhi0)
    nu    = libdisk.Nu(z,Phi)


    # compute sigma_z
    if   mode_sigma_z['name']=='jeans':
      R1,z1   = G.get_rz(offz=0)
      R2,z2   = G.get_rz(offz=1)
      dz = z2-z1
      sigma_z  = libdisk.get_2d_Sigma_From_Rho_Phi(rho=rho,Phi=Phi,z=z,dz=dz)
      sigma_z2 = sigma_z**2

    elif mode_sigma_z['name']=='surface density':
      """sigma_z2 = pi*G*Sden*Hz"""
      print "mode sigma z : 'surface density', not implemented yet"
      sys.exit()

    # compute sigma_r
    if   mode_sigma_r['name']=='epicyclic_approximation':
      beta2 =  mode_sigma_r['param']
      f =  np.where( kappa**2>0 , (1./beta2) * (nu**2/kappa**2) , 1.0  )
      f.shape = (nR,1)
      sigma_r2 = sigma_z2 * f

    elif mode_sigma_r['name']=='isothropic':
      sigma_r2 = sigma_z2

    elif mode_sigma_r['name']=='toomre':
      Q = mode_sigma_r['param']
      Gg = 1.0
      sr = np.where(kappa>0,Q*3.36*Gg*Sdend/kappa,sigma_z[:,nz/2])
      sr.shape = (nR,1)


      sigma_r2 = np.ones((nR,nz)) * sr
      sigma_r2 = sigma_r2**2

    elif mode_sigma_r['name']=='constant':

      sr = mode_sigma_r['param']

      sigma_r2 = np.ones((nR,nz)) * sr
      sigma_r2 = sigma_r2**2

    # compute sigma_p
    if   mode_sigma_p['name']=='epicyclic_approximation':
      f = np.where( omega**2>0 , (1/4.0) * (kappa**2/omega**2) , 1.0  )
      f.shape = (nR,1)
      sigma_p2 = sigma_r2 * f

    elif mode_sigma_p['name']=='isothropic':
      sigma_p2 = sigma_z2

    notok = True
    count = 0
    while notok:

      count = count + 1
      print "compute vm"

      # compute vm
      sr2 = sigma_r2[:,nz/2]                  # should not be only in the plane
      sp2 = sigma_p2[:,nz/2]                  # should not be only in the plane
      vc  = vcirc                             # should not be only in the plane


      T1 = vc**2
      T2 = + sr2 - sp2
      T3 = np.where(Sden>0,R/Sden,0)* libgrid.get_First_Derivative(Sden*sr2,R)
      vm2 = T1 + T2 + T3

      # if vm2 < 0
      c = (vm2<0)
      if sum(c)>0:
        print "Get_Velocities_From_Cylindrical_Grid : vm2 < 0 for %d elements"%(sum(c))

        '''
        vm2 = where(c,0,vm2)
        dsr2 = where(c,(T1+T2+T3)/2.,0)     # energie qu'il faut retirer a sr
        dsp2 = where(c,(T1+T2+T3)/2.,0)     # energie qu'il faut retirer a sp
        # take energy from sigma_r and sigma_p
        sigma_r2 = np.transpose(np.transpose(sigma_r2) + dsr2)
        sigma_p2 = np.transpose(np.transpose(sigma_p2) + dsp2)
        '''

        E = sr2 + sp2 + vm2
        if sum(E<0) != 0:

          print "-----------------------------------------------------"
          for i in range(len(R)):
            print R[i],vc[i]**2,sr2[i],sp2[i],vm2[i],sigma_z[i,nz/2]**2
          print "-----------------------------------------------------"
          print "Get_Velocities_From_Cylindrical_Grid : we are in trouble here..."
          raise "E<0"

        vm2 = np.where(c,E/3.,vm2)
        sr2 = np.where(c,E/3.,sr2)
        sp2 = np.where(c,E/3.,sp2)

        sigma_r2 = np.transpose(np.ones((nz,nR)) * sr2)
        sigma_p2 = np.transpose(np.ones((nz,nR)) * sp2)


        if count > 0:
          notok = False
      else:
        notok = False


      # old implementation
      #vm2  = where(c,T1,vm2)
      #dsr2 = where(c,-(T2+T3)/2.,0)
      #dsp2 = where(c,-(T2+T3)/2.,0)




    # check again
    c = (vm2<0).astype(int)
    nvm = np.sum(c)
    if np.sum(nvm)>0:
      print "WARNING : %d cells still have vm<0 !!!"%(nvm)
      print "Vc^2 < 0 !!!"
      vm2  = np.where(c,0,vm2)

    vm = np.where(vm2>0,np.sqrt(vm2),0)

    # generate velocities for all particles
    sigma_r2s = G.get_Interpolation(nb_cyl.pos,sigma_r2)
    sigma_p2s = G.get_Interpolation(nb_cyl.pos,sigma_p2)
    sigma_z2s = G.get_Interpolation(nb_cyl.pos,sigma_z2)
    sigma_rs  = np.where(sigma_r2s>0,np.sqrt(sigma_r2s),0)
    sigma_ps  = np.where(sigma_p2s>0,np.sqrt(sigma_p2s),0)
    sigma_zs  = np.where(sigma_z2s>0,np.sqrt(sigma_z2s),0)
    vcircs    = G.get_r_Interpolation(nb_cyl.pos,vcirc)
    vms       = G.get_r_Interpolation(nb_cyl.pos,vm)

    if NoDispertion:
      vr = sigma_rs
      vp = sigma_ps*0 + vms
      vz = sigma_zs
    else:
      vr = sigma_rs*np.random.standard_normal([nb_cyl.nbody])
      vp = sigma_ps*np.random.standard_normal([nb_cyl.nbody]) + vms
      vz = sigma_zs*np.random.standard_normal([nb_cyl.nbody])

    vel = np.transpose(np.array([vr,vp,vz])).astype(np.float32)
    nb_cyl.vel = libutil.vel_cyl2cart(nb_cyl.pos,vel)

    # here we should limit the speed according to max speed
    phis = G.get_Interpolation(nb_cyl.pos,Phi)
    vmax = 0.95*np.sqrt(-2*phis)
    vn = nb_cyl.vn()
    vf = np.where(vn>vmax,vmax/vn,1)
    vf.shape = (len(vf),1)
    nb_cyl.vel = nb_cyl.vel * vf

    # some output
    sr =  sigma_r = np.sqrt(sigma_r2[:,nz/2])
    sp =  sigma_p = np.sqrt(sigma_p2[:,nz/2])
    sz =  sigma_z = np.sqrt(sigma_z2[:,nz/2])
    Q  = np.where((Sden>0),sr*kappa/(3.36*Sdend),0)


    stats = {}
    stats['R']      = R
    stats['z']      = z
    stats['vc']     = vc
    stats['vm']     = vm
    stats['sr']     = sr
    stats['sp']     = sp
    stats['sz']     = sz
    stats['kappa']  = kappa
    stats['omega']  = omega
    stats['nu']     = nu
    stats['Sden']   = Sden
    stats['Sdend']  = Sdend
    stats['Q']      = Q
    #stats['Ar']     = Ar

    stats['rho']    = rho
    stats['phi']    = Phi
    stats['nn']     = nn
    stats['sigma_z']= np.sqrt(sigma_z2)
    stats['Phi0']   = Phi0
    stats['dPhi0']  = dPhi0
    stats['d2Phi0'] = d2Phi0

    return nb_cyl,Phi,stats


  ############################################
  #
  # evolution routines
  #
  ############################################

  def IntegrateUsingRK(self,tstart=0,dt=1,dt0=1e-5,epsx=1.e-13,epsv=1.e-13):
    """
    Integrate the equation of  motion using RK78 integrator.


    tstart   : initial time
    dt       : interval time
    dt0      : inital dt
    epsx     : position precision
    epsv     : velocity precision

    tmin,tmax,dt,dtout,epsx,epsv,filename

    """

    tend   = tstart + dt

    self.pos,self.vel,self.atime,self.dt = pNbody.nbdrklib.IntegrateOverDt(self.pos.astype(float),self.vel.astype(float),self.mass.astype(float),tstart,tend,dt,epsx,epsv)
    self.pos = self.pos.astype(np.float32)
    self.vel = self.vel.astype(np.float32)

  #################################
  #
  # Thermodynamic functions
  #
  #################################

  def U(self):
    '''
    Return the gas specific energy of the model.
    The output is an nx1 float array.
    '''
    return self.u



  def MeanWeight(self):
    '''
    Return the mean weight of a model, taking into account
    heating by UV source.
    The output is an nx1 float array.
    '''

    xi         = self.unitsparameters.get('xi')
    Redshift = 1./self.atime - 1.


    UnitDensity_in_cgs = self.localsystem_of_units.get_UnitDensity_in_cgs()
    UnitEnergy_in_cgs  = self.localsystem_of_units.get_UnitEnergy_in_cgs()
    UnitMass_in_g      = self.localsystem_of_units.get_UnitMass_in_g()
    HubbleParam        = self.hubbleparam

    # 0) convert into cgs
    Density = self.rho.astype(float) *UnitDensity_in_cgs * (HubbleParam*HubbleParam) / self.atime**3
    Egyspec = self.u.astype(float)   *UnitEnergy_in_cgs/UnitMass_in_g

    # 1) compute mu
    MeanWeight,Lambda = coolinglib.cooling(Egyspec,Density,xi,Redshift)

    return MeanWeight.astype(np.float32)

  def A(self):
    '''
    Return the gas entropy of the model.
    The output is an nx1 float array.
    '''
    gamma      = self.unitsparameters.get('gamma')
    xi         = self.unitsparameters.get('xi')
    ionisation = self.unitsparameters.get('ionisation')
    mu         = thermodyn.MeanWeight(xi,ionisation)
    mh         = ctes.PROTONMASS.into(self.localsystem_of_units)
    k          = ctes.BOLTZMANN.into(self.localsystem_of_units)
    thermopars = {"k":k,"mh":mh,"mu":mu,"gamma":gamma}


    A = np.where((self.u>0),thermodyn.Aru(self.Rho(),self.u,thermopars),0)
    return A


  def P(self):
    '''
    Return the gas pressure of the model.
    The output is an nx1 float array.
    '''
    gamma      = self.unitsparameters.get('gamma')
    xi         = self.unitsparameters.get('xi')
    ionisation = self.unitsparameters.get('ionisation')
    mu         = thermodyn.MeanWeight(xi,ionisation)
    mh         = ctes.PROTONMASS.into(self.localsystem_of_units)
    k          = ctes.BOLTZMANN.into(self.localsystem_of_units)
    thermopars = {"k":k,"mh":mh,"mu":mu,"gamma":gamma}

    P = np.where((self.u>0),thermodyn.Pru(self.Rho(),self.u,thermopars),0)
    return P


  def Ne(self):
    '''
    Return the electron density of the model.
    The output is an nx1 float array.
    '''

    xi         = self.unitsparameters.get('xi')
    ionisation = self.unitsparameters.get('ionisation')
    mh         = ctes.PROTONMASS.into(self.localsystem_of_units)

    thermopars = {"mh":mh,"Xi":xi,"ionisation":ionisation}
    ne = thermodyn.ElectronDensity(self.Rho(),thermopars)

    return ne

  def S(self):
    '''
    Return the `entropy` of the model, defined as
    S = T * Ne^(1-gamma)
    The output is an nx1 float array.
    '''

    gamma         = self.unitsparameters.get('gamma')

    s = self.T()*self.Ne()**(1.-gamma)

    return s


  def Lum(self):
    '''
    Return the luminosty of the model, defined as
    Lum = m*u/Tcool = m*Lambda/rho

    The output is an nx1 float array.
    '''

    Lum = self.mass*self.u/self.Tcool()

    return Lum

