''' 
 @package   pNbody
 @file      phot.py
 @brief     Photometry functions
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

from numpy import *
import ctes
import units


try:
  from scipy import optimize
  is_scipy = True
except ImportError:
  is_scipy = False 


####################################################################################################################################
#
# SOME FUNCTIONS RELATED TO PHOTOMETRY / OBSERVATION
#
####################################################################################################################################    

def MvtoLv (Mv,Mvsun=4.83,Lvsun=1.0):
  '''
  Mv    : magnitude in V-band
  Mvsun : magnitude of the sun in V-band
  Lvsun : V-band solar luminosity in solar luminosity unit
  
  Return the corresponding V-band luminosity in solar luminosity unit.
  '''

  Lv = Lvsun * 10**((Mvsun - Mv)/2.5)

  return Lv

def LvtoMv (Lv,Mvsun=4.83,Lvsun=1.0):
  '''
  Lv    : V-band luminosity in solar luminosity unit
  Mvsun : magnitude of the sun in V-band
  Lvsun : V-band solar luminosity in solar luminosity unit
  
  Return the magnitude in V-band
  '''

  Mv = Mvsun - 2.5*log10( Lv/Lvsun )

  return Mv
