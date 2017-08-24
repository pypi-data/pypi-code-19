''' 
 @package   pNbody
 @file      thermodyn.py
 @brief     init file
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

from numpy import *
from ctes import *
import units
import thermodyn
import io

from pNbody import thermodynlib

####################################################################################################################################
#
# THERMODYNAMIC RELATIONS
#
####################################################################################################################################    

# deflauts parameters in cgs
defaultpars = {"k":BOLTZMANN,"mh":PROTONMASS,"mu":2,"gamma":5/3.,"G":GRAVITY}





# tabulation of the mean weight (from Grackle)
nt = 10
tt = array([1.0e+01, 1.0e+02, 1.0e+03, 1.0e+04, 1.3e+04, 2.1e+04,3.4e+04, 6.3e+04, 1.0e+05, 1.0e+09])
mt = array([1.18701555, 1.15484424,1.09603514, 0.9981496, 0.96346395, 0.65175895,0.6142901,  0.6056833, 0.5897776,  0.58822635])



###################
def old_MeanWeightT(T):
###################
  '''
  mean molecular weight as a function of the Temperature
  '''
  
  
  if type(T)==ndarray:
    
    mu = zeros(len(T))
    for i in xrange(len(T)):
      mu[i] = MeanWeightT(T[i])
      
  
  else:

    logt = log(T)
    ttt = exp(logt)    
  
    if (ttt<tt[0]):
      j = 1
    else:  
      for j in xrange(1,nt):
    	if (ttt > tt[j-1])  and (ttt <= tt[j]):
    	  break

    slope = log(mt[j] / mt[j-1]) / log(tt[j] / tt[j-1])
    mu = exp(slope * (logt - log(tt[j])) + log(mt[j]))
  
  
  return mu


###################
def MeanWeightT(T):
###################
  '''
  mean molecular weight as a function of the Temperature
  '''
  
  
  return thermodynlib.MeanWeightT(T)





###################
def UNt(T):
###################
  '''
  UN(T) = energy normalized as a function of T
        = T/mu(T)
  '''
  
  return T/MeanWeightT(T)
  


# tabultion of the normalized energy vs T
unr = UNt(tt)


###################
def Tun(UN):
###################
  '''
  T(UN) = temperature vs energy normalzed
	
  inverse of UNt(U)	
	
  '''
  


  if type(UN)==ndarray:
    
    T = zeros(len(UN))
    for i in xrange(len(UN)):
      T[i] = Tun(UN[i])
      
  
  else:

    logu = log(UN)
    uuu = exp(logu)    
  
    if (uuu<unr[0]):
      j = 1
    else:  
      for j in xrange(1,nt):
    	if (uuu > unr[j-1])  and (uuu <= unr[j]):
    	  break

    slope = log(tt[j] / tt[j-1]) / log(unr[j] / unr[j-1])
    T = exp(slope * (logu - log(unr[j])) + log(tt[j]))


  return T





###################
def Prt(rho,T,pars=defaultpars):
###################
  '''
  P(rho,T)
  '''
  
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  mumh = mu*mh
  
  return k*T/(mumh/rho) 


###################
def Trp(rho,P,pars=defaultpars):
###################
  '''
  T(rho,P)
  '''
  
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  mumh = mu*mh
  
  return (mumh/rho)/k * ( P )



###################
def Art(rho,T,pars=defaultpars):
###################
  '''
  A(rho,T)
  '''

  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  mumh = mu*mh

  return k/mumh * rho**(1.-gamma) * T
  
###################
def Tra(rho,A,pars=defaultpars):
###################
  '''
  T(rho,A)
  '''

  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  mumh = mu*mh

  return mumh/k * rho**(gamma-1.) * A


###################
def Urt(rho,T,pars=defaultpars):
###################
  '''
  U(rho,T)
  '''
  
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  mumh = mu*mh
  
  #U = 1./(gamma-1.)* k*T/mumh
  U  = UNt(T) /(gamma-1.)* k/mh		# new, using the tabulated mu
  
  return U


###################
def Tru(rho,U,pars=defaultpars):
###################
  '''
  T(rho,U)
  '''  
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  mumh = mu*mh
  
  
  # T = (gamma-1.)* mumh/k * U

  UN = (gamma-1) * mh/k * U  
  #T = Tun(UN)				# new, using the tabulated mu
  T = thermodynlib.Tun(UN)		# new, using the tabulated mu + C version
  
  return T
  
    

###################
def Tmuru(rho,U,pars=defaultpars):
###################
  '''
  T(rho,U)/mu  = UN
  '''  

  k     = pars['k']
  gamma = pars['gamma']    
  mh    = pars['mh']
  
  Tmu = (gamma-1.)* mh/k * U

  return Tmu

   
  
###################
def Pra(rho,A,pars=defaultpars):
###################
  '''
  P(rho,A)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  mumh = mu*mh
    
  return rho**gamma * A 


###################
def Arp(rho,P,pars=defaultpars):
###################
  '''
  A(rho,P)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  mumh = mu*mh
  
  return rho**-gamma * P



###################
def Pru(rho,U,pars=defaultpars):
###################
  '''
  P(rho,U)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  mumh = mu*mh
  
  return (gamma-1.) * rho * U 


###################
def Urp(rho,P,pars=defaultpars):
###################
  '''
  U(rho,P)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
    
  mumh = mu*mh
  
  return  1./(gamma-1.) * (1/rho) *  P


###################
def Ura(rho,A,pars=defaultpars):
###################
  '''
  U(rho,A)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  mumh = mu*mh
  
  return 1./(gamma-1.) * rho**(gamma-1.) * A


###################
def Aru(rho,U,pars=defaultpars):
###################
  '''
  A(rho,U)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
    
  mumh = mu*mh
  
  return (gamma-1.) * rho**(1.-gamma) * U
  
  
  
###################
def SoundSpeed_ru(rho,U,pars=defaultpars):
###################
  '''
  Sound Speed
  Cs(rho,U)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
      
  return sqrt( (gamma-1.) * gamma * U )
  
  
###################
def SoundSpeed_rt(rho,T,pars=defaultpars):
###################
  '''
  Sound Speed
  Cs(rho,T)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  
  U = Urt(rho,T,pars)
  
  return sqrt( (gamma-1.) * gamma * U )
  
###################
def JeansLength_ru(rho,U,pars=defaultpars):
###################
  '''
  Jeans Length
  L_J(rho,U)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  G     = pars['G']
      
  Cs = SoundSpeed_ru(rho,U,pars)
  
  return Cs * sqrt( pi/(G*rho) )
  
  
###################
def JeansLength_rt(rho,T,pars=defaultpars):
###################
  '''
  Jeans Length
  L_J(rho,T)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  G     = pars['G']
  
  Cs = SoundSpeed_rt(rho,T,pars)
  
  return Cs * sqrt( pi/(G*rho) )
  
  
  
  
###################
def JeansMass_ru(rho,U,pars=defaultpars):
###################
  '''
  Jeans Mass
  M_J(rho,T)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  G     = pars['G']
  
  Cs = SoundSpeed_ru(rho,U,pars)
  
  return (pi**(5/2.) * Cs**3)/(6* G**(3/2.) * rho**(1/2.))
  
  
###################
def JeansMass_rt(rho,T,pars=defaultpars):
###################
  '''
  Jeans Mass
  M_J(rho,T)
  '''
  k     = pars['k']
  mh    = pars['mh']
  mu    = pars['mu']
  gamma = pars['gamma']
  G     = pars['G']
  
  Cs = SoundSpeed_rt(rho,T,pars)
  
  return (pi**(5/2.) * Cs**3)/(6* G**(3/2.) * rho**(1/2.))
  
  
  
###################
def MeanWeight(Xi,ionized=0):
###################
  '''
  old version
  '''

  if  ionized: 
    return 4./(8.-5.*(1.-Xi))
  else:
    return 4./(1.+3.*Xi)


###################
def ElectronDensity(rho,pars):
###################
  '''
  Electron density for a mixture of H + He
  '''

  Xi		= pars['Xi']
  mh    	= pars['mh']
  ionisation	= pars['ionisation']

  if  ionisation: 
    return rho.astype(float)/mh*(Xi+(1-Xi)/2.)
  else:
    return rho.astype(float)*0


#############################
def Lambda(rho,u,localsystem,thermopars,coolingfile):
#############################
  '''
  This corresponds to Lambda normalized
  
  Ln = L / nh 2
  
  nh = (xi*rho/mh)
  '''

  UnitLength_in_cm = PhysCte(1,localsystem.UnitDic['m']).into(units.cgs)
  UnitTime_in_s    = PhysCte(1,localsystem.UnitDic['s']).into(units.cgs)
  UnitMass_in_g    = PhysCte(1,localsystem.UnitDic['kg']).into(units.cgs)
 
  UnitVelocity_in_cm_per_s = UnitLength_in_cm/UnitTime_in_s
  UnitEnergy_in_cgs = UnitMass_in_g * pow(UnitLength_in_cm, 2) / pow(UnitTime_in_s, 2)
  
  metalicity       = thermopars['metalicity']
  hubbleparam      = thermopars['hubbleparam']
    
  # compute cooling time
  logT,logL0,logL1,logL2,logL3,logL4,logL5,logL6 = io.read_cooling(coolingfile)
  
  if  metalicity==0:
    logL = logL0
  elif metalicity==1:  
    logL = logL1
  elif metalicity==2: 
    logL = logL2
  elif metalicity==3: 
    logL = logL3
  elif metalicity==4: 
    logL = logL4
  elif metalicity==5: 
    logL = logL5
  elif metalicity==6: 
    logL = logL6 
    
  # compute gas temp  
  logTm = log10(thermodyn.Tru(rho,u,thermopars))  
  c   = ((logTm>=4)*(logTm<8.5))
  u   = where(c,u,1)
  rho = where(c,rho,1)
  # recompute gas temp
  logTm = log10(thermodyn.Tru(rho,u,thermopars))
  
  # get the right L for a given mT
  logLm = take(logL,searchsorted(logT,logTm))
  Lm = 10**logLm
  
  # transform in user units
  Lm =  Lm / UnitEnergy_in_cgs /pow(UnitLength_in_cm,3) *  UnitTime_in_s
  
  L = Lm * hubbleparam
    
    
  return L


#############################
def CoolingTime(rho,u,localsystem,thermopars,coolingfile):
#############################

  UnitLength_in_cm = PhysCte(1,localsystem.UnitDic['m']).into(units.cgs)
  UnitTime_in_s    = PhysCte(1,localsystem.UnitDic['s']).into(units.cgs)
  UnitMass_in_g    = PhysCte(1,localsystem.UnitDic['kg']).into(units.cgs)
 
  UnitVelocity_in_cm_per_s = UnitLength_in_cm/UnitTime_in_s
  UnitEnergy_in_cgs = UnitMass_in_g * pow(UnitLength_in_cm, 2) / pow(UnitTime_in_s, 2)
  
  ProtonMass       = thermopars['mh']
  Xi               = thermopars['Xi']
  metalicity       = thermopars['metalicity']
  hubbleparam      = thermopars['hubbleparam']
    
  # compute cooling time
  logT,logL0,logL1,logL2,logL3,logL4,logL5,logL6 = io.read_cooling(coolingfile)
  
  if  metalicity==0:
    logL = logL0
  elif metalicity==1:  
    logL = logL1
  elif metalicity==2: 
    logL = logL2
  elif metalicity==3: 
    logL = logL3
  elif metalicity==4: 
    logL = logL4
  elif metalicity==5: 
    logL = logL5
  elif metalicity==6: 
    logL = logL6 
    
  # compute gas temp  
  logTm = log10(thermodyn.Tru(rho,u,thermopars))  
  c   = ((logTm>=4)*(logTm<8.5))
  u   = where(c,u,1)
  rho = where(c,rho,1)
  # recompute gas temp
  logTm = log10(thermodyn.Tru(rho,u,thermopars))
  
  # get the right L for a given mT
  logLm = take(logL,searchsorted(logT,logTm))
  Lm = 10**logLm
  
  # transform in user units
  Lm =  Lm / UnitEnergy_in_cgs /pow(UnitLength_in_cm,3) *  UnitTime_in_s
  
  L = Lm * hubbleparam
    
  tc = (ProtonMass)**2/(L*Xi**2) * u/rho
  tc = where(c,tc,0)
    
  return tc,c
