''' 
 @package   pNbody
 @file      libdisk.py
 @brief     init file
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

from pNbody import *
from numpy import *

def get_Integral(v,dr,ia,ib):
  '''
  Integrate the vector v, between ia and ib, using trapezes.
  
  
  v  : values of cells (must be 1 dimensional)
  dr : corresponding physical size of cells
  ia : lower  real indice			WARNING : the indicies must now be integer !!!
  ib : higher real indice			WARNING : the indicies must now be integer !!!
  '''
  
  ia = max(0,ia)
  ib = min(len(v),ib)
      
  
  if ia==ib:
    return 0.0
  
  if ia>ib:
    raise "ia must be < ib"  
  
  
  '''
  # below, the case of non int values for ia and ib
  
  iap = int(ceil(ia))
  ibp = int(floor(ib))
  
  dra = iap-ia
  drb = ib-ibp  
        
  Ia = 0.0
  if dra != 0:
    Ia = v[iap-1] * dra
  
  Ib = 0.0  
  if drb != 0:
    Ib = v[ibp] * drb 
  
  
  I = v[iap:ibp]*dr[iap:ibp]
        
  return sum(I)+Ia+Ib

  '''

  I = 0
  for i in range(ia,ib):
    I = I + dr[i]* ( v[i+1] + 0.5*fabs(v[i+1]-v[i]) ) 
   

  return I






def Diff(f,x,s=None,k=2):
  '''
  First derivative of f(x)
  '''
 
  #if s!=None:
  #  tck = interpolate.fitpack.splrep(x,f,s=s,k=k)
  #  f  = interpolate.fitpack.splev(x,tck)

  
  fp = zeros(len(x),x.dtype)
    
  fp[0 ]  = (f[ 1]-f[ 0])/(x[ 1]-x[ 0]) 
  fp[-1]  = (f[-1]-f[-2])/(x[-1]-x[-2])
  
  
  f1 = f[2:]
  f2 = f[:-2]
  x1 = x[2:]
  x2 = x[:-2]  
  
  fp[1:-1] = (f1-f2)/(x1-x2)
  
  return fp


def Kappa(R,dPhi,d2Phi):
    
  Kappa2 = where((R==0),0.0,d2Phi + dPhi*3/R)
  
  if R[0]==0 and R[1]>0:    
    dPhi  = 0.5*(dPhi[0]+dPhi[1])
    d2Phi = 0.5*(d2Phi[0]+d2Phi[1])
    R     = 0.5*R[1] 
    Kappa2[0] = d2Phi + dPhi*3/R
  
  
  return sqrt(Kappa2)


def Omega(R,dPhi):

  Omega2 = where((R==0),0,dPhi/R)
  return sqrt(Omega2)

def Nu(z,Phi):
  
  nr,nz = Phi.shape
  
  odd = fmod(nz,2)
  
  if odd:
    idx1 = (nz/2)
    idx2 = (nz/2)+1    
  else:
    idx1 = (nz/2)

  
  nu2 = array([],float)
  
  for i in range(nr):
    
    d1 = Diff(Phi[i,:],z)
    d2 = Diff(d1,z)
        
    if odd:
      nu2 = concatenate((nu2, array([0.5*(d2[idx1]+d2[idx2])])))
    else:
      nu2 = concatenate((nu2,array([d2[idx1]])))
    
  return where(nu2>0,sqrt(nu2),0 )   
 

def Nu_Old(z,Phi):
  
  nr,nz = Phi.shape
  
  odd = fmod(nz,2)
  
  if odd:
    idx1 = (nz-1)/2
  else:
    idx1 = (nz/2)-1
    idx2 = (nz/2)

  
  nu2 = array([],float)
  
  for i in range(nr):
    
    d1 = Diff(Phi[i,:],z)
    d2 = Diff(d1,z)
        
    if odd:
      nu2 = concatenate((nu2,array([d2[idx1]])))
    else:
      nu2 = concatenate((nu2, array([0.5*(d2[idx1]+d2[idx2])])))
    
  return where(nu2>0,sqrt(nu2),0 )   



def Vcirc2(R,dPhi):

  return R*dPhi
    
def Vcirc(R,dPhi):

  Vcirc2 = R*dPhi
  return sqrt(Vcirc2)
  

def QToomre(G,R,SigmaR,Kappa,Sdens):
  
  Q = where((Sdens==0),0,SigmaR*Kappa/(3.36*G*Sdens))
  return Q

def XToomre(G,R,Kappa,Sdens,mode):
  X =  where((Sdens==0),0, (R * Kappa**2) / (2*pi*G*Sdens*mode) )
  return X

def AAraki(SigmaR,Sigmaz):
  
  A = where((SigmaR==0),0,Sigmaz/SigmaR)
  return A





def get_1d_Sigma_From_Rho_Phi(rho,phi,r,dr):

  dphi= libgrid.get_First_Derivative(phi,r)

  integrant = rho*dphi
  res = array([],float)
  nr = len(dr)
  

  for i in range(nr):
    
    ia = i
    ib = nr-1
    
    I =  get_Integral(integrant,dr,ia=ia,ib=ib)
    res = concatenate((res,array([I])))


  sigma = where(rho>0,res/rho,0)
  sigma = sqrt(sigma)  

  return sigma


def get_2d_Sigma_From_Rho_Phi(rho,Phi,z,dz):

  res = array([],float) 
  nr = Phi.shape[0]
  nz = Phi.shape[1]

  for i in range(nr):

    dzPhi  = libgrid.get_First_Derivative(Phi[i,:],z)
    integrant = rho[i,:]*dzPhi

    for j in range(nz):

      if (j <= nz/2) :
  	ia = 0
  	ib = j
	I = -get_Integral(integrant,dz,ia=ia,ib=ib)
	#print "-",ia,ib,I
      else:
  	ia = j
  	ib = nz-1
	I = get_Integral(integrant,dz,ia=ia,ib=ib)
	#print "+",ia,ib,I
  	        
      
      res = concatenate((res,array([I])))    

  res.shape = (nr,nz)
  
  sigma_z2 = where(rho>0,res/rho,0)
  sigma_z  = where(sigma_z2>0,sqrt(sigma_z2),0)
  
  
  return sigma_z



def get_2d_Sigma_From_Rho_Phi_Old(m,Phi,z,dz):

  res = array([],float) 
  nr = Phi.shape[0]
  nz = Phi.shape[1]

  for i in range(nr):

    dzPhi  = libgrid.get_First_Derivative(Phi[i,:],z)
    integrant = m[i,:]*dzPhi

    for j in range(nz):

      if (j < (nz-1)/2) :
  	ia = (nz-1) - j
  	ib = nz-1
      else:
  	ia = j
  	ib = nz-1
  	  
      #I =  libgrid.get_Integral(integrant,dz,ia=ia,ib=ib)
      I = get_Integral(integrant,dz,ia=ia,ib=ib)
      
      res = concatenate((res,array([I])))    

  res.shape = (nr,nz)
  
  sigma_z2 = where(m>0,res/m,0)
  sigma_z  = where(sigma_z2>0,sqrt(sigma_z2),0)
  
  
  return sigma_z










