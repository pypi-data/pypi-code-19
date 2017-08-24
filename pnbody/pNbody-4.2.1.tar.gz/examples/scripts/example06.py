'''
 @package   pNbody
 @file      example06.py
 @brief     Display a snapshot
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

from pNbody import *

nb = Nbody('gadget.dat',ftype='gadget')
nb.display(palette='light')
