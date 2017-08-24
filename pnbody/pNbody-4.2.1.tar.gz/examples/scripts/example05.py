from pNbody import *

'''
 @package   pNbody
 @file      example05.py
 @brief     Read example
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''


nb = Nbody('gadget.dat',ftype='gadget')
nb.info()
