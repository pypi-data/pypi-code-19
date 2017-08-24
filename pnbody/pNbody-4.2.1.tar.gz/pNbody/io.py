# -*- coding: iso-8859-1 -*-

''' 
 @package   pNbody
 @file      io.py
 @brief     Input/Output functions
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

# standard modules
import os,sys,string,types
import pickle

# array module
from numpy import *

import pyfits

import mpi


#################################
def checkfile(name):
#################################
  '''
  Check if a file exists. An error is generated if the file
  does not exists.
  
  Parameters
  ----------
  name : the path to a filename
	

  
  Examples
  --------
  >>> io.checkfile('an_existing_file')
  >>> 
  
  >>> io.checkfile('a_non_existing_file')
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/home/epfl/revaz/local/lib64/python2.6/site-packages/pNbody/io.py", line 33, in checkfile
      raise IOError(915,'file %s not found ! Pease check the file name.'%(name))
  IOError: [Errno 915] file nofile not found ! Pease check the file name.  
  
  '''
  						   						 
  if name == None:	
    raise Exception("file name set to None ! Please check the file name.")	   
  										   
  if not os.path.isfile(name):						   
    raise IOError(915,'file %s not found ! Pease check the file name.'%(name))
 

#################################
def end_of_file(f,pio='no',MPI=None):
#################################
  '''
  Return True if we have reached the end of the file f, False instead
      
  Parameters
  ----------
  f : ndarray or matrix object
      an open file
  pio : 'yes' or 'no'
      if the file is read in parallel or not  
  MPI : MPI communicator
   
    
  Returns
  -------  
  status : Bool
           True if the we reached the end of the file
           False if not
  '''
  
  if pio=='no':
    
    # here, the master decide for all slaves
  
    if mpi.ThisTask == 0:
  
      p1 = f.tell()
      f.seek(0,2)			      
      p2 = f.tell()
      f.seek(p1)
  
      if p1 == p2:
    	status = True
      else:
    	status = False 
  
    else:
      status = None
    	
    status = mpi.mpi_bcast(status,0)	 
    	
    return status   
    
  else:

    # each processus decide for himself   

    p1 = f.tell()
    f.seek(0,2) 			    
    p2 = f.tell()
    f.seek(p1)
  
    if p1 == p2:
      status = True
    else:
      status = False 
      
    return  status 

#####################################################
def write_array(file,vec):	
#####################################################     	 
  '''
  Write an array to a file, in a very simple ascii format.

  Parameters
  ----------
  file : the path to a file
  vec : an ndarray object


  Examples
  --------
  >>> from numpy import *
  >>> x = array([1,2,3])
  >>> io.write_array('/tmp/array.dat',x)
  '''
  
  f = open(file,'w')
  for i in range(len(vec)):
    f.write("%f\n"%vec[i])
  f.close()  
  
  
  
#####################################################
def read_ascii(file,columns=None,lines=None,dtype=float,skipheader=False,cchar='#'):	
#####################################################     	 
  '''
  Read an ascii file.
  The function allows to set the number of columns or line to read.
  If it contains a header, the header is used to label all column. In
  this case, a dictionary is returned.


  Parameters
  ----------
  file : the path to a file or an open file
  columns : list
             the list of the columns to read
	     if none, all columns are read
  lines : list
          the list of the lines to read
	  if none, all lines are read
  dtype : dtype
          the ndtype of the objects to read
  skipheader : bool
               if true, do not read the header
	       if there is one
  cchar : char
          lines begining with cchar are skiped
	  the first line is considered as the header	        
  	     
  Returns
  -------  
  data : Dict or ndarray
         A python dictionary or an ndarray object

  Examples
  --------
  >>> from numpy import *
  >>> x = arange(10)
  >>> y = x*x
  >>> f = open('afile.txt','w')
  >>> f.write("# x y")      
  >>> for i in xrange(len(x)):
  ...	f.write('%g %g'%(x[i],y[i]))
  ... 
  >>> f.close()
  >>> from pNbody import io
  >>> data = io.read_ascii("afile.txt")
  >>> data['x']
  array([ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9.])
  >>> data['y']
  array([  0.,   1.,   4.,   9.,  16.,  25.,  36.,  49.,  64.,  81.])  					 
  ''' 


  def RemoveComments(l):
    if l[0]==cchar:
      return None
    else:
      return l  

  def toNumList(l):
    return map(dtype,l)

  if type(file) != types.FileType:
    f = open(file,'r')
  else:
    f = file
      
 
  # read header while there is one
  while 1:
   fpos = f.tell()
   header = f.readline() 
   if header[0] != cchar:
     f.seek(fpos)
     header = None
     break
   else:
      if skipheader:
        header = None        
      else:
        # create dict from header
        header = string.strip(header[2:])
        elts = string.split(header)
        break  

  '''
  # read header if there is one
  header = f.readline()
  if header[0] != cchar:
    f.seek(0)
    header = None
  else:
    if skipheader:
      header = None    
    else:
      # create dict from header
      header = string.strip(header[2:])
      elts = string.split(header)  
  '''    
  
  # now, read the file content
  lines = f.readlines()

  # remove trailing
  lines = map(string.strip, lines)
  
  
  # remove comments
  #lines = map(RemoveComments, lines)  
  
  # split
  lines = map(string.split, lines)  
  
  # convert into float
  lines = map(toNumList, lines)  
      
  # convert into array
  lines = array(map(array, lines))
    
  # transpose
  lines = transpose(lines)
      
  if header != None:
    iobs = {}
    i = 0
    for elt in elts:
      iobs[elt]=i
      i = i + 1

    vals = {}
    for key in iobs.keys():
      vals[key] = lines[iobs[key]]
    
    return vals
    
  
  # return 
  if columns == None:
    return lines  
  else:
    return lines.take(axis=0,indices=columns)



#####################################################
def write_dmp(file,data):
#####################################################
  '''
  Write a dmp (pickle) file. In other word,
  dump the data object.
  
  Parameters
  ----------
  file : the path to a file
  data : a pickable python object
  
  Examples
  --------
  >>> x = {'a':1,'b':2}
  >>> io.write_dmp('/tmp/afile.dmp',x)
  '''
  f = open(file,'w')
  pickle.dump(data, f)
  f.close()

  
#####################################################
def read_dmp(file):
#####################################################
  '''
  Read a dmp (pickle) file. 
  
  Parameters
  ----------
  file : the path to a file
  
  Returns
  -------
  data : a python object
  
  Examples
  --------
  >>> x = {'a':1,'b':2}
  >>> io.write_dmp('/tmp/afile.dmp',x)
  >>> y = io.read_dmp('/tmp/afile.dmp')
  >>> y
  {'a': 1, 'b': 2}  					 
  ''' 

  f = open(file,'r')
  data = pickle.load(f)
  f.close()
  return data

  
  
  

#####################################################
def WriteFits(data, filename, extraHeader = None) :
#####################################################
  '''
  Write a fits file
  '''
  # image creation							        		   
  fitsimg = pyfits.HDUList()						        		   


  # add data
  hdu = pyfits.PrimaryHDU()						        		   
  hdu.data = data							        		   
  fitsimg.append(hdu)


  # add keys	
  keys = []  
  if extraHeader != None:
    #keys.append(('INSTRUME','st4 SBIG ccd camera','Instrument name'))
    #keys.append(('LOCATION',"175 OFXB St-Luc (VS)",'Location'))
    keys = extraHeader

  									       
  hdr = fitsimg[0].header						        	    
  for key in keys:							        	    
    hdr.update(key[0],key[1],comment=key[2])				        	    


  fitsimg.writeto(filename) 


#####################################################
def ReadFits(filename) :
#####################################################
  '''
  Read a fits file.
  '''
  # read image
  fitsimg = pyfits.open(filename)
  data = fitsimg[0].data
  return data
  
  

  
  
#################################
def readblock(f,data_type,shape=None,byteorder=sys.byteorder,skip=False,htype=int32):
#################################
  '''
  data_type = int,float32,float
  or
  data_type = array
  
  shape	    = tuple
  '''  
  
  # compute the number of bytes that should be read
  nbytes_to_read=None
  if shape!=None:
    shape_a = array(shape)
    nelts_to_read = shape_a[0]
    for n in shape_a[1:]:
      nelts_to_read = nelts_to_read*n
    nbytes_to_read = nelts_to_read*dtype(data_type).itemsize
  
  try:
    nb1 = fromstring(f.read(4),htype)
    if sys.byteorder != byteorder:
      nb1.byteswap(True)
    nb1 = nb1[0]  
   
    nbytes=nb1
   
    # check
    if nbytes_to_read:
      if nbytes_to_read!=nbytes:
        print "inconsistent block header, using nbytes=%d instead"%nbytes_to_read
        nbytes=nbytes_to_read
          
  except IndexError:
    raise "ReadBlockError" 


  if skip:
    f.seek(nbytes,1)  
    data = None
    shape = None
    print "  skipping %d bytes... "%(nbytes)
    
  
  else:

    if type(data_type) == types.TupleType:
    	 
      data = []
      for tpe in data_type:
    	  
    	if type(tpe) == int:
    	  val =  f.read(tpe)
    	else:
    	  bytes = dtype(tpe).itemsize
    	  val = fromstring(f.read(bytes),tpe)
    	  if sys.byteorder != byteorder:
    	    val.byteswap(True)  
    	   
    	  val = val[0]  
    	
    	data.append(val)
    	  
    else:
      data  = fromstring(f.read(nbytes),data_type)   
      if sys.byteorder != byteorder:
    	data.byteswap(True)  


      
  nb2 = fromstring(f.read(4),htype)
  if sys.byteorder != byteorder:
    nb2.byteswap(True)
  nb2 = nb2[0]  

  if nb1 != nb2:
    print "ReadBlockError","nb1=%d nb2=%d"%(nb1,nb2) 
    raise "ReadBlockError","nb1=%d nb2=%d"%(nb1,nb2)   
  
  # reshape if needed
  if shape != None:
    data.shape=shape

    
  return data


#################################
def ReadBlock(f,data_type,shape=None,byteorder=sys.byteorder,pio='no',htype=int32):
#################################
  '''
  data_type = int,float32,float
  or
  data_type = array
  
  shape	    = tuple
  
  pio   : parallel io, 'yes' or 'no'
          if 'yes', each proc read each file
	  if 'no',  proc 0 read and send to each other
  
  '''
  
  if mpi.NTask==1:
    data = readblock(f,data_type=data_type,shape=shape,byteorder=byteorder,htype=htype) 
    return data
    
  if pio == 'yes':
    data = readblock(f,data_type=data_type,shape=shape,byteorder=byteorder,htype=htype) 
    return data
    
  else:
    data = mpi.mpi_ReadAndSendBlock(f,data_type=data_type,shape=shape,byteorder=byteorder,htype=htype) 
    return data
  
  
    
#################################
def ReadArray(f,data_type,shape=None,byteorder=sys.byteorder,pio='no',nlocal=None,htype=int32):
#################################
  '''
  data_type = int,float32,float
  or
  data_type = array
  
  shape	    = tuple
    
  '''
  
  if mpi.NTask==1:
    data = readblock(f,data_type=data_type,shape=shape,byteorder=byteorder,htype=int32) 
    return data
    
  if pio == 'yes':
    data = readblock(f,data_type=data_type,shape=shape,byteorder=byteorder,htype=int32) 
    return data
    
  else:
    data = mpi.mpi_OldReadAndSendArray(f,data_type,shape=shape,byteorder=byteorder,nlocal=nlocal,htype=int32)


  return data

#################################
def ReadDataBlock(f,data_type,shape=None,byteorder=sys.byteorder,pio='no',npart=None,skip=False):
#################################
  '''
  
  Read a block containg data.
  If NTask = 1 or  pio = 'yes', the block is read normally.
  If NTask > 1 and pio = 'no',  the master reads the block and send the data to the slaves.
  
 
  In the second case : 
  
  a) the master send N/Ntask element to each task.
  b) if the var npart is present, he send Np/Ntask to each task, for each Np of npart. 
  
 
  data_type = array
  
  shape	    = tuple
    
  '''
  
  if mpi.NTask==1 or pio == 'yes':
    data = readblock(f,data_type=data_type,shape=shape,byteorder=byteorder,skip=skip) 
    return data
        
  else:
    data = mpi.mpi_ReadAndSendArray(f,data_type,shape=shape,byteorder=byteorder,npart=npart,skip=skip)

  return data

    
#################################
def writeblock(f,data,byteorder=sys.byteorder,htype=int32):
#################################
  '''
  data = array
  or
  data = ((x,float32),(y,int),(z,float32),(label,40))
  
  shape	    = tuple
  '''
  
  if type(data) == types.TupleType: 
    
    # first, compute nbytes
    nbytes = 0
    for dat in data:
      if type(dat[0])==types.StringType:
        nbytes = nbytes + dat[1]
      else:
        nbytes = nbytes + array([dat[0]],dat[1]).type().bytes* array([dat[0]],dat[1]).size()
      
    nbytes = array([nbytes],htype)
    
    # write block
    if sys.byteorder != byteorder:
      nbytes.byteswap(True)
    
    f.write(nbytes.tostring())
    for dat in data:
      if type(dat[0])==types.StringType:
        f.write(string.ljust(dat[0],dat[1])[:dat[1]])
      else:
        ar = array([dat[0]],dat[1])
        if sys.byteorder != byteorder:
	  ar.byteswap(True)
        f.write(ar.tostring())
	
    f.write(nbytes.tostring())
  
  else:
    # write block
    #nbytes = array([data.type().bytes*data.size()],int)
    nbytes = array([data.nbytes],htype)
       
    if sys.byteorder != byteorder:
      nbytes.byteswap(True)
      data.byteswap(True)  
    
    f.write(nbytes.tostring())  
    f.write(data.tostring())
    f.write(nbytes.tostring()) 
  
  
  
#################################
def WriteBlock(f,data,byteorder=sys.byteorder,htype=int32):
#################################
  '''
  data = ((x,float32),(y,int),(z,float32),(label,40))
  
  shape	    = tuple
  '''
  
  if f!=None:
  
    if type(data) == types.TupleType: 
      
      # first, compute nbytes
      nbytes = 0
      for dat in data:
    	if type(dat[0])==types.StringType:
    	  nbytes = nbytes + dat[1]
    	elif type(dat[0]) == string_:
	  nbytes = nbytes + dat[1]
	else:
	  #nbytes = nbytes + array([dat[0]],dat[1]).type().bytes* array([dat[0]],dat[1]).size()
	  nbytes = nbytes + array([dat[0]],dat[1]).nbytes
    	
      nbytes = array([nbytes],htype)
      
      # write block
      if sys.byteorder != byteorder:
    	nbytes.byteswap(True)
      
      f.write(nbytes.tostring())
      for dat in data:
    	if type(dat[0])==types.StringType:
    	  f.write(string.ljust(dat[0],dat[1])[:dat[1]])
    	elif type(dat[0]) == string_:
	  f.write(string.ljust(dat[0],dat[1])[:dat[1]])
    	else:
    	  ar = array([dat[0]],dat[1])
    	  if sys.byteorder != byteorder:
    	    ar.byteswap(True)
    	  f.write(ar.tostring())
    	  
      f.write(nbytes.tostring())
  


#################################
def WriteArray(f,data,byteorder=sys.byteorder,pio='no',npart=None,htype=int32):
#################################
  '''
  data = array
  
  shape	    = tuple
  '''
  
  
  if mpi.NTask==1 or pio == 'yes':
    writeblock(f,data,byteorder=byteorder,htype=htype)
        
  else:
    mpi.mpi_GatherAndWriteArray(f,data,byteorder=byteorder,npart=npart,htype=htype)


#################################
def WriteDataBlock(f,data,byteorder=sys.byteorder,pio='no',npart=None):
#################################
  '''

  Write a block containg data.
  If NTask = 1 or  pio = 'yes', the block is written normally.
  If NTask > 1 and pio = 'no',  the master get the block from the slaves and write it.
  
  In the second case : 
  
  a) the master get N/Ntask element from each task.
  b) if the var npart is present, he get Np/Ntask from each task, for each Np of npart. 


  data = array
  
  shape	    = tuple
  '''
  
  if mpi.NTask==1 or pio == 'yes':
    writeblock(f,data,byteorder=byteorder)
    
  else:
    mpi.mpi_GatherAndWriteArray(f,data,byteorder=byteorder,npart=npart)



###############################################################
#
# some special function reading gadget related files
#
###############################################################


#################################
def read_cooling(file):
#################################
  '''
  Read cooling file
  '''

  f = open(file,'r')
  f.readline()
  f.readline()
  lines = f.readlines()
  f.close()
  
  lines = map(string.strip,lines)
  elts = map(string.split,lines)
  
  logT	= array(map(lambda x:float(x[0]),elts))
  logL0	= array(map(lambda x:float(x[1]),elts))
  logL1	= array(map(lambda x:float(x[2]),elts))
  logL2	= array(map(lambda x:float(x[3]),elts))
  logL3	= array(map(lambda x:float(x[4]),elts))
  logL4	= array(map(lambda x:float(x[5]),elts))
  logL5	= array(map(lambda x:float(x[6]),elts))
  logL6	= array(map(lambda x:float(x[7]),elts))          
      
  return logT,logL0,logL1,logL2,logL3,logL4,logL5,logL6




#################################
def read_params(file):
#################################
  '''
  Read params Gadget file and return the content in
  a dictionary
  '''

  f = open(file)
  lines = f.readlines()
  f.close()

  # remove empty lines
  lines = filter(lambda l:l!='\n', lines)
  
  # remove trailing
  lines = map(string.strip, lines)

  # remove comments
  lines = filter(lambda x:x[0]!='%', lines)
  
  # split lines
  elts = map(string.split,lines)
  
  # make dictionary
  params = {}
  for e in elts:
    
    try :
      params[e[0]]=float(e[1])
    except ValueError:
      params[e[0]]= e[1] 
        
  return params



