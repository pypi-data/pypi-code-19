'''
 @package   pNbody
 @file      example04.py
 @brief     Creates a pNbody object
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

from pNbody import *

pos = ones((10,3),float32)
nb = Nbody(pos=pos,ftype='gadget')
nb.info()
