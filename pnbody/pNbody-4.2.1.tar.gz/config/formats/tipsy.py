'''
 @package   pNbody
 @file      tipsy.py
 @brief     
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''
class Nbody_tipsy:

  def _init_spec(self):
    pass
    
  def get_excluded_extension(self):
    """
    Return a list of file to avoid when extending the default class.
    """
    return []
    
  def read_p(self,f):
    '''
    specific format for particle file
    '''
    # header
    h1 = fromstring(f.read(8),Float)
    h2 = fromstring(f.read(4*5),Int)
    tnow  = h1[0]
    nbody = h2[0]
    ndim  = h2[1] 
    ngas  = h2[2]
    ndark = h2[3]
    nstar = h2[4]
               
    # gas
    if ngas!=0:
      vec = fromstring(f.read(4*12*ngas),Float32)
      vec.shape = (ngas,12)
      mass = vec[:,0]
      pos  = vec[:,1:4]
      vel  = vec[:,4:7]
 
    # dark
    if ndark!=0:
      vec = fromstring(f.read(4*9*ndark),Float32)
      vec.shape = (ndark,9)
      
      if ngas==0:
        mass  = vec[:,0]
	pos   = vec[:,1:4]
	vel   = vec[:,4:7]
      else:  
        mass = concatenate((mass,vec[:,0]))
        pos  = concatenate((pos,vec[:,1:4]))
        vel  = concatenate((vel,vec[:,4:7])) 
      
    # stars
    if nstar!=0:
      vec = fromstring(f.read(4*11*nstar),Float32)
      vec.shape = (nstar,11)
      
      if ngas==0 and ndark==0:
        mass  = vec[:,0]
        pos   = vec[:,1:4]
        vel   = vec[:,4:7]
      else:  
        mass = concatenate((mass,vec[:,0]))
        pos  = concatenate((pos,vec[:,1:4]))
        vel  = concatenate((vel,vec[:,4:7]))	
      
       
    # make global
    self.tnow  = tnow
    self.nbody = nbody
    self.label = 'tipsy file'
    
    self.pos = pos
    self.vel = vel
