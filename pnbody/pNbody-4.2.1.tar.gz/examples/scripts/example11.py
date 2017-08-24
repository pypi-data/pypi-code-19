'''
 @package   pNbody
 @file      example11.py
 @brief     Create a snapshot from 3 differents distribution
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

from pNbody import *
from pNbody import ic

'''
create a multi component model
'''

ftype = 'gadget'

nb_gas  = ic.miyamoto_nagai(1000,3,0.1,30,2,ftype=ftype)
nb_disk = ic.expd(n=2000,Hr=3.,Hz=0.3,Rmax=20,Zmax=2,irand=1,ftype=ftype)
nb_halo = ic.plummer(3000,1,1,1,10,40,ftype=ftype)

nb_gas.set_tpe(0) 
nb_halo.set_tpe(1) 
nb_disk.set_tpe(2) 

#nb = nb_gas + nb_halo + nb_disk
nb = nb_gas + nb_disk + nb_halo  


nb.rename('snap.dat')
nb.write()

nb.show(obs=None,view='yz',size=[50,50])
