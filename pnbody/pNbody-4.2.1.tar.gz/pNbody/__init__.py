''' 
 @package   pNbody
 @file      __init__.py
 @brief     init file
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''


'''
This python module is useful to manipulate N-body data.
It allows to compute simple pysical values like energy, 
kinetic momentum, intertial momentum, centrer of mass etc.
It also allows to modify the data with rotation, translations,
select some particules, add particles etc.
Associated scripts like "gdisp", "mkmovie" or "movie" allow
to visualise the N-body data in different ways : surface density,
velocity map, velocity dispertion map, etc.

Yves Revaz 14.05.05
'''

# nbody classes
from main import *
 

