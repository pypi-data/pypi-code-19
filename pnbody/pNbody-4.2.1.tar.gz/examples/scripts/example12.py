'''
 @package   pNbody
 @file      example12.py
 @brief     Select stars
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

from pNbody import *
from pNbody import ic

'''
select component
'''

nb = Nbody('snap.dat',ftype='gadget')
nb = nb.select(1)
nb.show(obs=None,view='yz',size=[50,50])
