'''
 @package   pNbody
 @file      example13.py
 @brief     Select particles based on position
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
nb = nb.selectc(fabs(nb.x())<5)
nb.show(obs=None,view='xy',size=[50,50])
