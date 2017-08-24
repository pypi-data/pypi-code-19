''' 
 @package   pNbody
 @file      ctes.py
 @brief     Physics Constants
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

####################################################################################################################################
#
# CONSTANTES
#
####################################################################################################################################    

from units import *


GRAVITY 	  = PhysCte(6.6732e-11,Unit_G)   
SOLAR_MASS	  = PhysCte(1.989e33,Unit_g)
SOLAR_LUM	  = PhysCte(3.826e33,Unit_erg/Unit_s)
AVOGADRO	  = PhysCte(6.0220e+23,Unit_mol)
BOLTZMANN	  = PhysCte(1.3807e-23,Unit_J/Unit_K)
GAS_CONST	  = PhysCte(8.3144e+00,Unit_J/Unit_mol)
C		  = PhysCte(2.99792458e8,Unit_m/Unit_s)
PLANCK  	  = PhysCte(6.6262e-34,Unit_J*Unit_s)
PROTONMASS	  = PhysCte(1.6726e-27,Unit_kg)
ELECTRONMASS	  = PhysCte(9.1095e-31,Unit_kg)
ELECTRONCHARGE    = PhysCte(4.8032e-10,Unit_C)
AV                = PhysCte(6.828e-50 ,Unit_Pa*Unit_m**6)
BV                = PhysCte(4.419e-29,Unit_m**3)
HUBBLE		  = PhysCte(3.2407789e-18,1/Unit_s)	# in h/s

def convert_ctes(units):
  '''
  convert a constante into a given unit system.
  '''
    
  UnitLength_in_cm		  = units[0]
  UnitMass_in_g 		  = units[1]
  UnitVelocity_in_cm_per_s	  = units[2]
  UnitTime_in_s = UnitLength_in_cm / UnitVelocity_in_cm_per_s
  
  BOLTZMANN  = BOLTZMANN/UnitEnergy_in_cgs
  PROTONMASS = PROTONMASS/UnitMass_in_g
  
 
