#!/usr/bin/env python

'''
 @package   pNbody
 @file      showmap.py
 @brief     Display snapshot
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

import sys
from pNbody import *

file = sys.argv[1]

nb = Nbody(file,ftype='gadget',pio='yes')
nb.display(size=(10000,10000),shape=(256,256),palette='light')
