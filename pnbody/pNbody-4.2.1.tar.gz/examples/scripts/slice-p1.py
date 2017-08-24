#!/usr/bin/env python
'''
 @package   pNbody
 @file      slice-p1.py
 @brief     Cut a slice
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''


import sys
from pNbody import *

files = sys.argv[1:]

for file in files:
  print "slicing",file
  nb = Nbody(file,ftype='gadget')
  nb = nb.select('gas')  
  nb = nb.selectc((fabs(nb.pos[:,1])<1000))
  nb.rename(file+'.slice')
  nb.set_pio('yes')
  nb.write()
