''' 
 @package   pNbody
 @file      cooling.py
 @brief     Cooling functions
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

from numpy import *
from pNbody import *

try:
  import cooling_with_metals as libcooling
except:
  pass

'''
In pNbody we need to wrap cooling_with_metals in cooling
in order to initialize it safely with the default parameters.

This module is a wrapper around the defaut GEAR cooling function
using the metallicity.
'''



'''
THIS IS NOW DOWN OUTSIDE
as we cannot acess to nb.localsystem_of_units

print "!!!!!! in cooling.py  !!!!"
print "!!!!!! this is bad    !!!! we should never use UNITSPARAMETERFILE"
print "!!!!!! this is bad    !!!! we should never use UNITSPARAMETERFILE"

unitsparameters = param.Params(UNITSPARAMETERFILE,None)
libcooling.init_cooling(unitsparameters.get_dic())
print unitsparameters.get_dic()
sys.exit()

# set system of units
params = {}
params['UnitLength_in_cm']	   = unitsparameters.get('UnitLength_in_cm')
params['UnitVelocity_in_cm_per_s'] = unitsparameters.get('UnitVelocity_in_cm_per_s')
params['UnitMass_in_g'] 	   = unitsparameters.get('UnitMass_in_g')
localsystem_of_units = units.Set_SystemUnits_From_Params(params)
'''



init_cooling 					= libcooling.init_cooling

get_lambda_from_Density_Temperature_FeH 	= libcooling.get_lambda_from_Density_Temperature_FeH
get_lambda_from_Density_EnergyInt_FeH   	= libcooling.get_lambda_from_Density_EnergyInt_FeH
get_lambda_from_Density_Entropy_FeH     	= libcooling.get_lambda_from_Density_Entropy_FeH
get_lambda_normalized_from_Temperature_FeH    	= libcooling.get_lambda_normalized_from_Temperature_FeH
get_cooling_time_from_Density_Temperature_FeH	= libcooling.get_cooling_time_from_Density_Temperature_FeH
get_cooling_time_from_Density_EnergyInt_FeH	= libcooling.get_cooling_time_from_Density_EnergyInt_FeH



def check():
  
  print
  libcooling.PrintParameters()

  rho = 3.0364363e-06
  u   = 0.0015258887
  fe  = 0.
  l = libcooling.get_lambda_from_Density_EnergyInt_FeH(rho,u,fe)

  dudt = l/rho
  dt   = u/dudt
  print 
  print "cooling time = ",dt

