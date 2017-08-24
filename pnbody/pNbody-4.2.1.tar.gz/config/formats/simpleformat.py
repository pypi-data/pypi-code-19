'''
 @package   pNbody
 @file      simpleformat.py
 @brief     
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

class Nbody_simpleformat:

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
    return {'tnow'   :0.,
	    }
	    
  def get_default_spec_array(self):
    '''
    return specific array default values for the class
    '''
    return {'meta'   :(0,float),
            }	    
	    

  def read_particles(self,f):
    '''
    read binary particle file
    '''
    
    ##########################################
    # read the header and send it to each proc
    ##########################################    
        
    tpl = (float32,int32,int32)
    header = io.ReadBlock(f,tpl,byteorder=self.byteorder,pio=self.pio)
    tnow, ngas, nstar = header 
    
    nbody = ngas + nstar
    npart = [ngas,nstar,0,0,0,0]
        
    ##########################################
    # set nbody and npart
    ##########################################    
    
    
    if self.pio == 'no':

      npart_tot    = npart	
      npart_all    = libutil.get_npart_all(npart,mpi.mpi_NTask())
      npart        = npart_all[mpi.mpi_ThisTask()]			# local
      npart_read   = npart_tot
      nbody_read   = sum(npart_read)
      ngas_read    = npart_tot[0]
    
    else:
   
      npart_tot    = mpi.mpi_reduce(npart) 
      npart_all    = None						# each proc read for himself
      npart        = npart						# local
      npart_read   = None						# each proc read for himself
      nbody_read   = sum(npart)
      ngas_read    = npart[0]    
    
           		
    ####################################################################################
    # read and send particles position/velocities/mass/metallicity
    ####################################################################################      

    self.pos = io.ReadDataBlock(f,float32,shape=(nbody_read,3),byteorder=self.byteorder,pio=self.pio,npart=npart_read)
    self.vel = io.ReadDataBlock(f,float32,shape=(nbody_read,3),byteorder=self.byteorder,pio=self.pio,npart=npart_read)
    self.mass= io.ReadDataBlock(f,float32,shape=(nbody_read, ),byteorder=self.byteorder,pio=self.pio,npart=npart_read)
    self.meta= io.ReadDataBlock(f,float32,shape=(ngas_read,  ),byteorder=self.byteorder,pio=self.pio,npart=None)
    self.meta= concatenate((self.meta,zeros(nbody_read-ngas_read).astype(float32)))


    #self.pos = io.ReadArray(f,float32,shape=(nbody,3),byteorder=self.byteorder,pio=self.pio,nlocal=npart_all)
    #self.vel = io.ReadArray(f,float32,shape=(nbody,3),byteorder=self.byteorder,pio=self.pio,nlocal=npart_all)
    #self.mass= io.ReadArray(f,float32,                byteorder=self.byteorder,pio=self.pio,nlocal=npart_all)
    #self.meta= io.ReadArray(f,float32,                byteorder=self.byteorder,pio=self.pio,nlocal=npartgas_all)
    #self.meta  = concatenate((self.meta,zeros(nbody-npart[0]).astype(float32)))
    


    self.tpe = array([],int32)
    for i in range(len(npart)):
      self.tpe = concatenate( (self.tpe,ones(npart[i])*i) )
    



    

  def write_particles(self,f):
    '''
    specific format for particle file
    '''
    npart_all = array(mpi.mpi_Allgather(self.npart))
    
    if self.pio == 'yes':
      ngas  = self.npart[0]
      nstar = self.npart[1]
    else:
      ngas  = mpi.mpi_reduce(self.npart[0])
      nstar = mpi.mpi_reduce(self.npart[1])
    
    # header 
    tpl = ((self.tnow,float32),(ngas,int32),(nstar,int32))
    io.WriteBlock(f,tpl,byteorder=self.byteorder)																																		   
    
    # positions 
    io.WriteArray(f,self.pos.astype(float32),byteorder=self.byteorder,pio=self.pio,npart=None)																												   
    io.WriteArray(f,self.vel.astype(float32),byteorder=self.byteorder,pio=self.pio,npart=None)
    io.WriteArray(f,self.mass.astype(float32),byteorder=self.byteorder,pio=self.pio,npart=None)																												   
    io.WriteArray(f,self.meta[:self.npart[0]].astype(float32),byteorder=self.byteorder,pio=self.pio,npart=None)



  def spec_info(self):
    """
    Write spec info
    """	
    infolist = []
    infolist.append("")
    infolist.append("tnow                : %s"%self.tnow)	
    return infolist  

  def Metallicity(self):
    """
    Return the metallicity
    """	
    return self.meta  
