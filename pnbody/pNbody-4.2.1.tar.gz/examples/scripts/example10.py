'''
 @package   pNbody
 @file      example10.py
 @brief     Merge to pNbody object together
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''


from pNbody import *

'''
merge two models
'''

nb1 = Nbody('gadget.dat',ftype='gadget')
nb2 = Nbody('gadget.dat',ftype='gadget')

nb1.rotate(angle=pi/4,axis=[0,1,0])
nb1.translate([-50,0,0])
nb1.vel = nb1.vel + [20,0,0]

nb2.rotate(angle=pi/4,axis=[1,0,0])
nb2.translate([+50,0,20])
nb2.vel = nb2.vel - [50,0,0]

nb3 = nb1 + nb2
nb3.rename('merge.gad')
nb3.write()
