'''
 @package   pNbody
 @file      example07.py
 @brief     Read a snapshot
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

from pNbody import *

nb = Nbody('gadget.dat',ftype='gadget')
nb.display(size=(50,50),shape=(256,256),palette='light')
