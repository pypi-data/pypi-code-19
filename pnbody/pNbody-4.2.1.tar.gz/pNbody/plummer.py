''' 
 @package   pNbody
 @file      plummer.py
 @brief     Defines Plummer profiles
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

'''
plummer model
'''

from numpy import * 

def Potential(G,M,a,r):
   '''
   Plummer Potential
   '''
   return -G*M/sqrt(r**2+a**2)

def dPotential(G,M,a,r):
   '''
   Plummer first derivative of Potential
   '''
   return G*M* r*(r**2+a**2)**(-3./2.)
   
   
def Vcirc(G,M,a,r):
   '''
   Plummer circular velocity
   '''
   return sqrt(  G*M* r**2*(r**2+a**2)**(-3./2.)   )
   
   
def Density(G,M,a,r):
   '''
   Plummer Density
   '''
   return (3.*M/(4.*pi*a**3))*(1+(r/a)**2)**(-5./2.)

def LDensity(G,M,a,r):
   '''
   Plummer Linear Density
   '''
   return (4*pi * r**2) * (3.*M/(4.*pi*a**3))*(1+(r/a)**2)**(-5./2.)

def Sigma(G,M,a,r):
  '''
  Return sigma (radial) from Jeans equation : 1/rho Int( rho * drPhi * dr )
  '''
  sigma = 1./(8*pi*Density(G,M,a,r)) * G * M**2 * a**2 /( r**2 + a**2 )**3
  return sqrt(sigma)
