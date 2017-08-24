'''
 @package   pNbody
 @file      tipsybig.py
 @brief     
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''
class Nbody_tipsybig:

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
    h1 = fromstring(f.read(8),Float).byteswapped()
    h2 = fromstring(f.read(4*5),Int).byteswapped()
    tnow  = h1[0]
    nbody = h2[0]
    ndim  = h2[1] 
    ngas  = h2[2]
    ndark = h2[3]
    nstar = h2[4]
    
    #f.read(4) ?
    # gas
    vec1 = fromstring(f.read(4*12*ngas),Float32).byteswapped()
    # dark
    vec2 = fromstring(f.read(4*9*ndark),Float32).byteswapped()
    # stars 
    vec3 = fromstring(f.read(4*11*nstar),Float32).byteswapped()   
    
    vec1.shape = (ngas,12)
    vec2.shape = (ndark,9)
    vec3.shape = (nstar,11)
    
    mass = concatenate((vec1[:,0],vec2[:,0],vec3[:,0]))
    pos  = concatenate((vec1[:,1:4],vec2[:,1:4],vec3[:,1:4]))
    vel  = concatenate((vec1[:,4:7],vec2[:,4:7],vec3[:,4:7]))
    
    # make global
    self.tnow  = tnow
    self.nbody = nbody
    self.label = 'tipsy file'
    
    self.pos = pos
    self.vel = vel
