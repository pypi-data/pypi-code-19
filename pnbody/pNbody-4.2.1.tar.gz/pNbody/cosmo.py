''' 
 @package   pNbody
 @file      cosmo.py
 @brief     Defines function related to cosmology
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

from numpy import *
import ctes
import units
import cosmolib
import types

try:
  from scipy import optimize
  is_scipy = True
except ImportError:
  is_scipy = False 


####################################################################################################################################
#
# SOME COSMOLOGICAL RELATIONS
#
####################################################################################################################################    

UnitLength_in_cm         = 3.085678e+21
UnitMass_in_g            = 1.989e+43
UnitVelocity_in_cm_per_s = 100000.0
UnitTime_in_s            = UnitLength_in_cm / UnitVelocity_in_cm_per_s;
toGyrs			 = UnitTime_in_s / (60*60*24*365*1e9)


HUBBLE      = 3.2407789e-18	# Hubble param in h/sec
HubbleParam = 0.73		# Hubble param in 100 km/s/Mpc
OmegaLambda = 0.76
Omega0      = 0.24

# Hubble constance in code unit
Hubble = HUBBLE * UnitTime_in_s

# deflauts cosmo parameters
defaultpars = {"Hubble":Hubble,"HubbleParam":HubbleParam,"OmegaLambda":OmegaLambda,"Omega0":Omega0}






###################
def setdefault():
###################
  '''
  set default cosmological parameters
  '''
  global defaultpars
  defaultpars = {"Hubble":Hubble,"HubbleParam":HubbleParam,"OmegaLambda":OmegaLambda,"Omega0":Omega0}
  

###################
def Z_a(a):
###################
  '''
  z(a)
  '''
  return 1./a - 1

###################
def A_z(z):
###################
  '''
  a(z)
  '''
  return 1/(z+1)
  
  
###################
def Rho_c(localsystem_of_units):
###################
  '''
  Critical density
  '''
  
  G = ctes.GRAVITY.into(localsystem_of_units)
  H = ctes.HUBBLE.into(localsystem_of_units)
  
  rhoc = 3*H**2/(8*pi*G)
  
  return  rhoc
  

###################
def Hubble_a(a,pars=defaultpars):
###################
  '''
  H(a)
  '''
  OmegaLambda	= pars['OmegaLambda']
  Omega0	= pars['Omega0']
  Hubble	= pars['Hubble']

  hubble_a = Omega0 / (a * a * a) + (1 - Omega0 - OmegaLambda) / (a * a) + OmegaLambda
  hubble_a = Hubble * sqrt(hubble_a)

  return hubble_a

###################
def dt_da(da,a,pars=defaultpars):
###################
  '''
  dt from da 
  in units of 1/Hubble
  '''

  dt = da / (a * Hubble_a(a,pars))  
  # * toGyrs/HubbleParam if we want Gyrs, assuming Hubble=0.1

  return dt

###################
def Adot_a(a,pars=defaultpars):
###################
  '''
  da/dt
  '''
  OmegaLambda	= pars['OmegaLambda']
  Omega0	= pars['Omega0']
  Hubble	= pars['Hubble']

  hubble_a = Omega0 / (a * a * a) + (1 - Omega0 - OmegaLambda) / (a * a) + OmegaLambda
  hubble_a = Hubble * sqrt(hubble_a)
  adot_a   = hubble_a*a

  return adot_a
 
###################
def Age_a(a,pars=defaultpars):
###################
  '''
  cosmic age as a function of a
  Return a physical value (free of h) in Gyrs
  '''
  OmegaLambda	= pars['OmegaLambda']
  Omega0	= pars['Omega0']
  Hubble	= pars['Hubble']
  HubbleParam	= pars['HubbleParam']

  if type(a)==ndarray:
    a = a.astype(float)
  else:
    a = array([a],float)
  
  # here, Hubble is assumed to be in the default gadget units
  # and should thus allways be 0.1
  
  age_a = cosmolib.Age_a(a,Omega0,OmegaLambda,Hubble)  *toGyrs/HubbleParam
 
  return age_a

###################
def CosmicTime_a(a,pars=defaultpars):
###################
  '''
  cosmic time as a function of a in internal units,
  ie, (1/h)
  '''
  OmegaLambda	= pars['OmegaLambda']
  Omega0	= pars['Omega0']
  Hubble	= pars['Hubble']
  
  
  if type(a)==ndarray:
    a0 = zeros(len(a),float)
    a1 = a.astype(float)
  else:
    a0 = array([0],float)
    a1 = array([a],float)


  t0 = cosmolib.Age_a(a0,Omega0,OmegaLambda,Hubble) 
  ta = cosmolib.Age_a(a1,Omega0,OmegaLambda,Hubble) 
 
  return t0-ta
 

###################
def a_CosmicTime(t,pars=defaultpars,a0=0.5):
###################
  '''
  return a for a given cosmic time
  '''

  if not is_scipy:
    raise "module scipy needed for function a_CosmicTime !"

  
  def zfct(a,t,pars):
    t = CosmicTime_a(a,pars)[0] - t
    return t
    
  a = optimize.newton(zfct,x0=a0,args=(t,pars),tol=1e-5)
  return a



