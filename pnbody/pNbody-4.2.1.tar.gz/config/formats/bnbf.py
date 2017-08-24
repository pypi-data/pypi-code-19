'''
 @package   pNbody
 @file      bnbf.py
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

class Nbody_bnbf:
  
  def _init_spec(self):
    pass
    
  def get_excluded_extension(self):
    """
    Return a list of file to avoid when extending the default class.
    """
    return []  
  
  def get_read_fcts(self):
    return [self.read_particles]
    
  def get_write_fcts(self):
    return [self.write_particles]    

  def get_mxntpe(self):
    return 6
    
  def get_default_spec_vars(self):
    '''
    return specific variables default values for the class
    '''
    return {'label'   : "0               ",
            'nbody'   : 0,
            'atime'   : 0.,
            'empty'   : 232*''}
      

  def read_particles(self,f):
    '''
    read binary particle file
    '''
    
    ##########################################
    # read the header and send it to each proc
    ##########################################    
    
    tpl = (16,int32,float32,232)
    header = io.ReadBlock(f,tpl,byteorder=self.byteorder,pio=self.pio)
    label,nbody,atime,empty = header 
    
                
    ##########################################
    # read and send particles attribute
    ##########################################        

    pos  = io.ReadDataBlock(f,float32,shape=(nbody,3),byteorder=self.byteorder,pio=self.pio)
    vel  = io.ReadDataBlock(f,float32,shape=(nbody,3),byteorder=self.byteorder,pio=self.pio)
    mass = io.ReadDataBlock(f,float32,shape=(nbody, ),byteorder=self.byteorder,pio=self.pio)
    
    ##########################################
    # make global
    ##########################################    
        
    self.pos = pos
    self.vel = vel
    self.mass= mass
    
            

  def write_particles(self,f):
    '''
    specific format for particle file
    '''
    
    if self.pio == 'yes':
      nbody = self.nbody
    else:
      nbody = mpi.mpi_reduce(self.nbody) 
    
    
    # header 
    tpl = ( (self.label,16) , (nbody,int32), (self.atime,float32), (self.empty,232) )
    io.WriteBlock(f,tpl,byteorder=self.byteorder)																																		   
    
    # positions 	
    io.WriteDataBlock(f,self.pos.astype(float32),byteorder=self.byteorder,pio=self.pio)																												  
    # velocities								        																											  
    io.WriteDataBlock(f,self.vel.astype(float32),byteorder=self.byteorder,pio=self.pio)																												  
    # mass 	
    io.WriteArray(f,self.mass.astype(float32),byteorder=self.byteorder,pio=self.pio)		
	

    
	
        
  def spec_info(self):
    """
    Write spec info
    """	
    infolist = []
    infolist.append("")
    infolist.append("label               : %s"%self.label)
    infolist.append("atime               : %s"%self.atime)	
      
    return infolist  
      

  
