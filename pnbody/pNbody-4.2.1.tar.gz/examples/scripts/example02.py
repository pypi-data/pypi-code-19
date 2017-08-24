'''
 @package   pNbody
 @file      example02.py
 @brief     Create an empty snapshot
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

from pNbody import *

nb = Nbody(ftype='gadget')
nb.info()
