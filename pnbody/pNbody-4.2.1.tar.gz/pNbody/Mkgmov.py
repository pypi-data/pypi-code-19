''' 
 @package   pNbody
 @file      Mkgmov.py
 @brief     init file
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

import Mtools
import Mtools as mt

import os
import glob
from pNbody import *
from pNbody.param import Params
import copy
import types

import gzip


########################################################################################################
#
#  Some info on the structure :
#
#  1) nb   : the full nbody object (main loop)
#
#  2) nbf  : normally set the display parameters, position of the observer
#            but could be used to set the component
#
#  3) nbfc : normally set the component to display and/or the value to dispplay
#
#      component['id'][0] == '@'
#        this is used to open simple nbody object (to draw a box, for example)
#      component['id'][0] == '#'
#        no selection
#      component['id']    == 'gas'
#        selection gas
#        
#
#
#
#  a script may be called at level 2)
#     
#    frame['ext_cmd'] = []
#    frame['ext_cmd'].append("""from plot_P import MakePlot""")
#    frame['ext_cmd'].append("""MakePlot([nbf],output)""")
#   
#    it must save an output output, the latter is opened as an img
#    and appened to imgs
#
#
#  a script may be called at level 3)
#
#    1)
#    component['ext_cmd'] = []
#    component['ext_cmd'].append("""from plot_P import MakePlot""")
#    component['ext_cmd'].append("""MakePlot([nbfc],output)""")
#   
#    it must save an output output, the latter is opened as an img
#    and appened to imgs  
#
#    
#    2) using
#    component['to_img']='script_name'
#
#
########################################################################################################





#######################################################################
# some usefull functions
#######################################################################


def ReadNbodyParameters(paramname):
  '''
  read param from a parameter Nbody file
  '''
  
  gparams = Params(paramname,None)
  
  param = {}
  # create new params
  for p in gparams.params:
    param[p[0]]=p[3]    

  return param


def gzip_compress(file):

  f = open(file,'r')
  content = f.read()
  f.close()

  f = gzip.open(file+'.gz', 'wb')
  f.write(content)
  f.close()



#######################################################################
#
#	C L A S S   D E F I N I T I O N
#
#######################################################################



class Movie():
  
  
  def __init__(self,parameterfile='filmparam.py',format=None,imdir=None,timesteps=None,pio=False,compress=True,ifile=0):


    self.DEFAULT_TIMESTEPS = None
    self.DEFAULT_FORMAT    = "fits"
    self.DEFAULT_IMDIR     = "fits"
    self.DEFAULT_PIO       = False
    self.DEFAULT_COMPRESS  = True
    
    self.DEFAULT_SCALE     = "log"
    self.DEFAULT_CD        = 0.
    self.DEFAULT_MN        = 0.
    self.DEFAULT_MX        = 0.
    self.DEFAULT_PALETTE   = "light" 
    
    self.DEFAULT_SKIPPED_IO_BLOCKS = []
  
    self.parameterfile=parameterfile       

    # read the parameter file
    self.read_parameterfile()

    # use options
    if format != None:
      self.film['format'] = format
    if imdir != None:
      self.film['imdir'] = imdir
    if timesteps != None:
      self.film['timesteps'] = timesteps
    if pio != None:
      self.film['pio'] = pio
    if compress != None:
      self.film['compress'] = compress      


    self.imdir    = self.film['imdir']
    self.pio      = self.film['pio']
    self.compress = self.film['compress']

    # deal with timesteps
    self.set_timesteps() 
    
 
    self.ifile=ifile-1
    self.file_offset=0
        
    if mpi.mpi_IsMaster():			# whith gmkgmov, the init is only runned by the master, this line is not needed...
    
      
      if self.pio:
        self.pio = "yes"
      else:
        self.pio = "no"
  

      if self.parameterfile==None:
        print "you must specify a parameter file"
        sys.exit()
        
      if not os.path.exists(self.parameterfile):
        print "file %s does not exists"%self.parameterfile
        sys.exit()

      if not os.path.exists(self.imdir):
        os.mkdir(self.imdir)
      else:
        print "directory %s exists !!!"%self.imdir
	
	files = os.listdir(self.imdir)
	print "the directory contains %d files"%(len(files))
	
	
	# png files
	png_files = glob.glob(os.path.join(self.imdir,"*.png"))
	n_png_files = len(png_files)

	print "the directory contains %d png files"%(n_png_files)

	# fits files
	fits_files = glob.glob(os.path.join(self.imdir,"*.fits"))
	n_fits_files = len(fits_files)
	
	print "the directory contains %d fits files"%(n_fits_files)
	
	
	if n_png_files > 0:
	  self.file_offset = n_png_files
	
    
  
  
  def info(self):
    print "INFO INFO INFO"
    #print self.film
    print self.parameterfile
    print self.getftype()
    print "INFO INFO INFO"
  
  def read_parameterfile(self):     
  
    if not os.path.isfile(self.parameterfile):
      raise IOError(915,'file %s not found ! Pease check the file name.'%(self.parameterfile))
    

    # import the parameter file as a module
        
    module_name = os.path.basename(os.path.splitext(self.parameterfile)[0])
    module_dir  = os.path.dirname(self.parameterfile)
            
    if sys.path.count(module_dir) == 0:
      sys.path.append(module_dir)  
     
    filmparam = __import__(module_name,globals(), locals(), [], -1)



    self.film = filmparam.film   
    
    # set some defaults
    if not self.film.has_key('timesteps'):
      self.film['timesteps'] = self.DEFAULT_TIMESTEPS
    if not self.film.has_key('imdir'):
      self.film['imdir'] = self.DEFAULT_IMDIR  
    if not self.film.has_key('format'):
      self.film['format'] = self.DEFAULT_FORMAT                   
    if not self.film.has_key('pio'):
      self.film['pio'] = self.DEFAULT_PIO    
    if not self.film.has_key('compress'):
      self.film['compress'] = self.DEFAULT_COMPRESS   
    if not self.film.has_key('skipped_io_blocks'):
      self.film['skipped_io_blocks'] = self.DEFAULT_SKIPPED_IO_BLOCKS         
    
    self.setftype(self.film['ftype'])

    # post process
    for i,frame in enumerate(self.film['frames']):
      frame['id'] = i

    # check
    #for frame in self.film['frames']:
    #  print frame['id']
    #  for component in frame['components']:
    #	print "  ",component['id']



  ##################################
  # time steps stuffs
  ##################################

  def set_timesteps(self):
    """
    define self.times (which is a list) based
    on the value contained in self.film['timesteps']
    """
    
    # self.times
    if self.film['timesteps']=='every':
      self.times="every"
    
    elif type(self.film['timesteps']) == types.StringType:
      fname = self.film['timesteps']
      if not os.path.isfile(fname):
        raise IOError(916,'file %s not found ! Pease check the file name.'%(fname))
      times = io.read_ascii(fname,[0])[0]
      times = take( times,len(times)-1-arange(len(times)))	# invert order
      times = times.tolist()
      self.times = times
    
    elif type(self.film['timesteps']) == types.ListType:
      self.times = self.film['timesteps']
      
    elif type(self.film['timesteps']) == types.TupleType:
      t0 = self.film['timesteps'][0]
      t1 = self.film['timesteps'][1]
      dt = self.film['timesteps'][2]
      times = arange(t0,t1,dt)      
      times = take( times,len(times)-1-arange(len(times)))	# invert order      
      times = times.tolist()
      self.times = times
    
    else:
      self.times=[]  
       

  def set_next_time(self):
    if self.times!="every":
      if len(self.times)>0:
        self.times.pop()
    
    
  def get_next_time(self):
    if self.times=="every":
      return 0.0
  
    if len(self.times)==0:
      return None 
    else:
      return self.times[-1]
    


  def getftype(self):
    return self.ftype    

  def setftype(self,ftype):
    self.ftype = ftype


  def get_skipped_io_blocks(self):
    return self.film["skipped_io_blocks"]




  def ApplyFilmParam(self,nb,film):
        
    # set time reference for this file
    exec("nb.tnow = %s"%film['time'])
    # exec1
    if film.has_key('exec'):
      if film['exec'] != None:
        exec(film['exec']) 

    # macro
    if film.has_key('macro'):
      if film['macro'] != None:
        execfile(film['macro'])	  
    
    return nb
    


    

  def ApplyFrameParam(self,nb,frame):
        
    nbf = nb
    	
    # exec
    if frame.has_key('exec'):
      if frame['exec'] != None:
        exec(frame['exec']) 

    # macro
    if frame.has_key('macro'):
      if frame['macro'] != None:
        execfile(frame['macro']) 
    
    return nbf




  def ApplyComponentParam(self,nbf,component):
        

    if component['id'][0] == '@':
      # here, all tasks must have an object containing all particles
      # ok, but not in the right order !!!
      nbfc = Nbody(componentid,self.getftype())
      nbfc = nbfc.SendAllToAll()
      nbfc.sort()
      nbfc.componentid=component['id']#[1:]
    elif component['id'][0] == '#':
      nbfc = nbf
      nbfc.componentid = component['id']#[1:]
    else:
      nbfc = nbf.select(component['id'])
      nbfc.componentid = component['id']
    
    # exec
    if component.has_key('exec'):
      if component['exec'] != None:
        exec(component['exec']) 

    # macro    
    if component.has_key('macro'):
      if component['macro'] != None:
        execfile(component['macro']) 
      
    #print "------------------------"
    #print min(nbfc.u),max(nbfc.u)
    #print min(nbfc.rho),max(nbfc.rho)
    #print min(nbfc.tpe),max(nbfc.tpe)
    #print "temperature",min(nbfc.T()),max(nbfc.T())
    #print nbfc.nbody
    #print min(nbfc.rsp),max(nbfc.rsp)
    #print "------------------------"  
    
    return nbfc



  def dump(self,dict):
    
    # exctract dict
    atime = dict['atime']
    pos   = dict['pos']

    # create nbody object
    nb = Nbody(pos=pos,ftype='gadget')   
    nb.atime = atime

    # add other arrays
    if dict.has_key('vel'):
      nb.vel = dict['vel']      

    if dict.has_key('num'):
      nb.num = dict['num']
    
    if dict.has_key('mass'):
      nb.mass = dict['mass']      
    
    
    if dict.has_key('tpe'):
      nb.tpe = dict['tpe']
            
    if dict.has_key('u'):
      nb.u = dict['u']
    if dict.has_key('rho'):
      nb.rho = dict['rho']        
    if dict.has_key('rsp'):
      nb.rsp = dict['rsp']  

    if dict.has_key('metals'):
      nb.metals = dict['metals']  
      
      #!!!
      nb.flag_chimie_extraheader=1
      nb.ChimieNelements = 5
      nb.flag_metals = 5
      nb.ChimieSolarMassAbundances={}
      nb.ChimieSolarMassAbundances['Fe']=0.00176604


    nb.init()
    
    #print "################################"
    #print "writing qq.dat"
    #print "################################"
    #nb.rename('qq.dat')
    #nb.write()

    
    self.dumpimage(nb=nb)
  
  
  

  
  def dumpimage(self,nb=None,file=None):
      
    
    # increment counter
    self.ifile+=1

    
    # skip file if needed
    if self.ifile<self.file_offset:
      if mpi.mpi_IsMaster():
        print "skipping file %04d"%self.ifile
      
      return


    
    # for each frame one can create an img
    imgs = []
    	
    if file!=None:
      #print "(task=%04d) reading "%(mpi.ThisTask),file,self.getftype(),self.pio
      
      if mpi.mpi_IsMaster():
        print
        print "#############################################################"
        print "reading...",file
        print "#############################################################"	    
      
      nb = Nbody(file,ftype=self.getftype(),pio=self.pio,skipped_io_blocks=self.get_skipped_io_blocks())      
    else:
      if nb==None:
        raise "you must specify at least a file or give an nbody object" 
      
	
    film = self.film	
    	
    nb = self.ApplyFilmParam(nb,film)    
          
      
    for frame in film['frames']:
      nbf = self.ApplyFrameParam(nb,frame)
   
     
      if frame.has_key('ext_cmd'):	
        if len(frame['ext_cmd'])>0:
          #################################################
          # 1) use an outer script to create an img		(this is a bit redundant with 2.2, see below )
          #################################################
          output= "/tmp/%015d.png"%(int(random.random()*1e17))

         
	  for cmd in frame['ext_cmd']:
            exec(cmd)	 
        
	
	  if mpi.mpi_IsMaster():
	    img = Image.open(output)
	    imgs.append(img)
	
      	    if os.path.exists(output):
      	      os.remove(output)	    
	
	continue	  



      # composition parameters 
      
      if frame.has_key('cargs'):
        if len(frame['cargs'])!=0:
          frame['compose']=True
	  datas = []
        else:
	  frame['compose']=False
      else:
        frame['cargs']=[]
        frame['compose']=False	  
	  
               
      for component in frame['components']:
        if mpi.mpi_IsMaster():
          print "------------------------"
	  print "component",component['id']  
	  print "------------------------"	 	  
	
        nbfc = self.ApplyComponentParam(nbf,component)
	

      	# find the observer position
      	# 1) from params
      	# 2) from pfile
      	# 3) from tdir
      	# and transform into parameter

      	if frame['tdir']!=None:
      	  
      	  tfiles = glob.glob(os.path.join(frame['tdir'],"*")) 
      	  tfiles.sort()
      	  
      	  bname = os.path.basename(file)
	  
	        	  
      	  tfiles_for_this_file = []
      	  for j in xrange(len(tfiles)):
      	    tfile = "%s.%05d"%(bname,j)  
	    #tfile = "%s.0.%05d"%(bname,j) # old or new version ?
      	    tmp_tfile = os.path.join(frame['tdir'],tfile)
	    
      	    if os.path.exists(tmp_tfile):
      	      tfiles_for_this_file.append(tmp_tfile)


      	elif frame['pfile']!=None:
      		  
      	  if not os.path.isfile(frame['pfile']):
      	    print "parameter file %s does not exists(1)..."%(frame['pfile'])
      	  
      	  # read from pfile defined in frame
      	  param = ReadNbodyParameters(frame['pfile']) 
      	  tfiles_for_this_file = [None]   
      	  
      	else:
      	  
      	  # take frame as parameter
      	  param = copy.copy(frame)
      	  tfiles_for_this_file = [None]
	  
	
	
	
      	# loop over different oberver positions for this file  
      	for iobs,tfile in enumerate(tfiles_for_this_file):
      
      	  if tfile!=None:
	    if mpi.mpi_IsMaster():
	      print "  using tfile : %s"%(tfile)
      	    param = ReadNbodyParameters(tfile)  
  
      	  
      	  # add parameters defined by user in the parameter file
      	  for key in component.keys():
      	    param[key] = component[key]

 
      	  # set image shape using frame
      	  param['shape'] = (frame['width'],frame['height'])
	        	      
  
      	  # compute map
      	  mat = nbfc.CombiMap(param)	
	  
	  
	  
	  
      	  if mpi.mpi_IsMaster():
	  
	    if frame['compose']:
	      datas.append(mat)
	      	      
            

            if component.has_key('ext_cmd'):	
	      #################################################       
	      # 1) use an outer script to create an img 	    
	      #################################################       
              if len(component['ext_cmd'])>0:									      
                    					  	            					  
                output= "/tmp/%015d.png"%(int(random.random()*1e17))						      

	        for cmd in component['ext_cmd']:									      
                  exec(cmd)											      
        
	
	        if mpi.mpi_IsMaster():  									      
	          img = Image.open(output)									      
	          imgs.append(img)										      
	
      	          if os.path.exists(output):									      
      	            os.remove(output)										      
	

	    	    
	    elif self.film["format"]=="fits":
	      #################################
	      # 1) save fits file
	      #################################
      	      output = '%04d_%04d-%s-%06d.fits'%(self.ifile,frame['id'],component['id'],iobs)
      	      output = os.path.join(self.imdir,output)
      	      print nb.atime,output
      	  
    
      	      if os.path.exists(output):
      	        os.remove(output)

      	      header = [('TIME',nb.tnow,'snapshot time')] 	       
      	      io.WriteFits(transpose(mat), output, extraHeader = header)   
	      	    
              # compress
	      if self.compress:
	        gzip_compress(output)
	        os.remove(output)
	  

            elif self.film["format"]=="png":
	      #################################
	      # 2) output png file or ...
	      #################################
	      
     	      output = '%04d_%04d-%s-%06d.png'%(self.ifile,frame['id'],nbfc.componentid,iobs)
	      
	      
      	      output = os.path.join(self.imdir,output)
      	      print nb.atime,output


              # here, we should use component['scale'] ... not frame['scale'], no ?
   
    	      if not frame.has_key('scale'):
    	        frame['scale']=self.DEFAULT_SCALE
    	      if not frame.has_key('cd'):
    	        frame['cd']=self.DEFAULT_CD
    	      if not frame.has_key('mn'):
    	        frame['mn']=self.DEFAULT_MN
    	      if not frame.has_key('mx'):
    	        frame['mx']=self.DEFAULT_MX
    
    	      if not frame.has_key('palette'):
    	        frame['palette']=self.DEFAULT_PALETTE
    
              matint,mn_opt,mx_opt,cd_opt = set_ranges(mat,scale=frame['scale'],cd=frame['cd'],mn=frame['mn'],mx=frame['mx'])
              frame['mn'] = mn_opt 
              frame['mx'] = mx_opt
              frame['cd'] = cd_opt
              img = get_image(matint,palette_name=frame['palette'])
              img.save(output) 
	      
              print frame['mn'],frame['mx'],frame['cd']


            # need to create an img
            if component.has_key('to_img'):
	    
	      if component['to_img']==True:
	      	##########################################
	        # 2.1) create an img and apply commmands
	        ##########################################

	    			
		# get params
		if not component.has_key('scale'):
    	      	  component['scale']=self.DEFAULT_SCALE
    	      	if not component.has_key('cd'):
    	      	  component['cd']=self.DEFAULT_CD
    	      	if not component.has_key('mn'):
    	      	  component['mn']=self.DEFAULT_MN
    	      	if not component.has_key('mx'):
    	      	  component['mx']=self.DEFAULT_MX
    	      	if not component.has_key('palette'):
    	      	  component['palette']=self.DEFAULT_PALETTE
    	      
	      
                matint,mn_opt,mx_opt,cd_opt = set_ranges(mat,scale=component['scale'],cd=component['cd'],mn=component['mn'],mx=component['mx'])
                img = get_image(matint,palette_name=component['palette'])
		
                print mn_opt,mx_opt,cd_opt
		
		# here we can add img commands....
		if component.has_key('img_cmd'):
                  if len(component['img_cmd'])>0:
		    
		    for cmd in component['img_cmd']:
		      exec(cmd)
				
		# append img to list
		img.atime = nb.atime
		imgs.append(img)
	    
	    
              elif type(component['to_img'])==types.StringType:
	      	##########################################
	        # 2.2) use an outer script to create an img from mat
	        ##########################################
	        
		output= "/tmp/%015d.png"%(int(random.random()*1e17))


		# get params
		if not component.has_key('scale'):
    	      	  component['scale']=self.DEFAULT_SCALE
    	      	if not component.has_key('cd'):
    	      	  component['cd']=self.DEFAULT_CD
    	      	if not component.has_key('mn'):
    	      	  component['mn']=self.DEFAULT_MN
    	      	if not component.has_key('mx'):
    	      	  component['mx']=self.DEFAULT_MX
    	      	if not component.has_key('palette'):
    	      	  component['palette']=self.DEFAULT_PALETTE
		
		component['atime']=nbfc.atime

				
                mk = __import__(component['to_img'],globals(), locals(), [], -1)
		mk.MkImage(mat,output,component)
	  
	        img = Image.open(output)
	        imgs.append(img)	     
	        
		os.remove(output)
	     
	     

      del nbf
      
      #######################
      # compose components
      #######################

      if frame['compose']:
	
        if mpi.mpi_IsMaster():
          	            	  	    	    
          img,cargs =  Mtools.fits_compose_colors_img(datas,frame['cargs'])
          
          # save 
     	  #output = '%04d_%04d.png'%(self.ifile,frame['id'])
      	  #output = os.path.join(self.imdir,output)
	  #img.save(output)
	  
	  # append img to list
	  img.atime = nb.atime
          imgs.append(img)


    del nb
    	       	  
    #######################
    # compose frames
    #######################	
    
    if mpi.mpi_IsMaster():
      if film.has_key('img_cmd'): 
        if len(film['img_cmd'])>0:
          
          
          for cmd in film['img_cmd']:
            exec(cmd)	   
            
          output = '%04d.png'%(self.ifile)
          output = os.path.join(self.imdir,output)
          img.save(output)
          
          img.i=0
	  




 
      
      
  






