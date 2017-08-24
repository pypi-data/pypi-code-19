'''
 @package   pNbody
 @file      binary.py
 @brief     
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''
####################################################################################################################################
#
# BINARY CLASS
#
####################################################################################################################################    

import numpy as np
from pNbody import units, ctes, cosmo, thermodyn, mpi, io

class Nbody_binary:

  
  def _init_spec(self):
    pass
    
  def get_excluded_extension(self):
    """
    Return a list of file to avoid when extending the default class.
    """
    return []
    
  def get_read_fcts(self):
    return [self.read_particles,self.read_mass]
    
  def get_write_fcts(self):
    return [self.write_particles,self.write_mass]    

  def get_mxntpe(self):
    return 6
    
  def get_default_spec_vars(self):
    '''
    return specific variables default values for the class
    '''
    return {'tnow'   :0.,
            'label'  :'binary',
            'dt'     :0.
	    }
      

  def read_particles(self,f):
    '''
    read binary particle file
    '''
    
    ##########################################
    # read the header and send it to each proc
    ##########################################    
    tpl = (np.float32,np.int32,np.float32,40)
    header = io.ReadBlock(f,tpl,byteorder=self.byteorder,pio=self.pio)
    tnow,nbody,dt,label = header 
    
                
    ##########################################
    # read and send particles attribute
    ##########################################        

    pos = io.ReadDataBlock(f,np.float32,shape=(nbody,3),byteorder=self.byteorder,pio=self.pio)
    vel = io.ReadDataBlock(f,np.float32,shape=(nbody,3),byteorder=self.byteorder,pio=self.pio)
    #pos = io.ReadArray(f,float32,shape=(nbody,3),byteorder=self.byteorder,pio=self.pio)
    #vel = io.ReadArray(f,float32,shape=(nbody,3),byteorder=self.byteorder,pio=self.pio)
    
    ##########################################
    # make global
    ##########################################    
    
    self.tnow  = tnow
    self.label = label
    self.dt    = dt
    
    self.pos = pos
    self.vel = vel
    
        

  def read_mass(self,f):
    '''
    read binary mass file
    '''
                
    ##########################################
    # read and send mass
    ##########################################        
    
    mass = io.ReadArray(f,np.float32,byteorder=self.byteorder,pio=self.pio)
        
    ##########################################
    # make global
    ##########################################    
    self.mass = mass
    

  def write_particles(self,f):
    '''
    specific format for particle file
    '''
    
    if self.pio == 'yes':
      nbody = self.nbody
    else:
      nbody = mpi.mpi_reduce(self.nbody) 
    
    
    # header 
    tpl = ((self.tnow,np.float32),(nbody,np.int32),(self.dt,np.float32),(self.label,40))
    io.WriteBlock(f,tpl,byteorder=self.byteorder)																																		   
    
    # positions 	
    io.WriteDataBlock(f,self.pos.astype(np.float32),byteorder=self.byteorder,pio=self.pio)																												  
    # velocities								        																											  
    io.WriteDataBlock(f,self.vel.astype(np.float32),byteorder=self.byteorder,pio=self.pio)																												  
	
	
  def write_mass(self,f):
    '''
    specific format for mass file
    '''
    
    # mass 	
    io.WriteArray(f,self.mass.astype(np.float32),byteorder=self.byteorder,pio=self.pio)																												   
    
    
	
        
  def spec_info(self):
    """
    Write spec info
    """	
    infolist = []
    infolist.append("")
    infolist.append("tnow                : %s"%self.tnow)	
    infolist.append("label               : %s"%self.label)
    infolist.append("dt                  : %s"%self.dt)		
      
    return infolist  
      

  
