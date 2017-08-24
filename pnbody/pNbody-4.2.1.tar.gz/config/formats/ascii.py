'''
 @package   pNbody
 @file      ascii.py
 @brief     
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''
class Nbody_ascii:
  '''
  This class defines the simple ascii format
  '''

  def _init_spec(self):
    pass
    
  def get_excluded_extension(self):
    """
    Return a list of file to avoid when extending the default class.
    """
    return []

  def get_read_fcts(self):
    """
    returns the functions needed to read a file.
    """
    return [self.read_particles]
    
  def get_write_fcts(self):
    """
    returns the functions needed to write a file.
    """
    return [self.write_particles]    


  def read_particles(self,f):
    """
    Function that read particles.
    """
    from pNbody import io    
    x,y,z,vx,vy,vz,m=io.read_ascii(f,range(7))
    self.pos = transpose(array([x,y,z])).astype(float32)	
    self.vel = transpose(array([vx,vy,vz])).astype(float32)
    self.mass = m.astype(float32)
      
  def write_particles(self,f):
    """
    Function that write particles.
    """
    for i in range(self.nbody):  	   
      line = "%g %g %g %g %g %g %g \n" %(self.pos[i][0],self.pos[i][1],self.pos[i][2],self.vel[i][0],self.vel[i][1],self.vel[i][2],self.mass[i])
      f.write(line)     
