'''
 @package   pNbody
 @file      nhg.py
 @brief     
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''
from Nbody import *
from Numeric import *

self.X = self.X.subdis(mode='nhg')
self.display()
self.display_info(self.X)
