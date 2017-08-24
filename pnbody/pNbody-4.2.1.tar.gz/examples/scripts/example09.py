'''
 @package   pNbody
 @file      example09.py
 @brief     Format Conversion
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''


from pNbody import *


'''
conversion binary -> gadget -> binary
'''



nb = Nbody(['binary.dat'],ftype='binary')

nb = nb.set_ftype('gadget')
nb.rename('gadget.dat')
nb.write()

nb = nb.set_ftype('binary')
nb.rename('newbinary.dat')
nb.write()
