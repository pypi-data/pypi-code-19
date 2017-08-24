#!/usr/bin/env python

'''
 @package   pNbody
 @file      findmax.py
 @brief     Find max radius
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

import sys
from pNbody import *

file = sys.argv[1]

nb = Nbody(file,ftype='gadget',pio='yes')
local_max  = max(nb.rxyz())
global_max = mpi.mpi_max(nb.rxyz())

print "proc %d local_max = %f global_max = %f"%(mpi.ThisTask,local_max,global_max)
