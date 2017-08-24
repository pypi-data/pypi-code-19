# -*- coding: utf-8 -*-
'''
 @package   pNbody
 @file      main.py
 @brief     Defines abstract class for Nbody objects
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''
# some standard modules
import os, sys, string, types, glob, inspect
from types import FunctionType
from copy import deepcopy
import warnings

# array module
from numpy import *
from numpy import clip as numclip
from numpy import random as RandomArray


# module that init parameters
from parameters import *

# nbody python modules
import io
from libutil import *
from palette import *
import geometry as geo
import fourier
import param
import liblog
import libgrid
import libdisk
import libutil
import nbdrklib
import error

# nbody C modules
from myNumeric import *
from mapping import *
from nbodymodule import *

# Gtools module (now integrated in nbody)
#import Gtools as Gt
import units
import ctes
import thermodyn
import coolinglib
import cosmo
import treelib
import asciilib



try:
  import ptreelib
except:
  pass

try:
 import libqt
except:
 pass

try:
 import SM
except:
 pass




try:				# all this is usefull to read files
 from mpi4py import MPI
except:
 MPI = None

import mpi			# maybe we should send mpi instead of MPI



FLOAT = float

if FORMATSDIR is not None:
  formatsfiles = glob.glob(os.path.join(FORMATSDIR,'*.py'))

def get_methods(cls):
  return [(x,y) for x, y in cls.__dict__.items() if type(y) == FunctionType]

def get_module_name(filename):
  module_dir, module_file = os.path.split(filename)
  module_name, module_ext = os.path.splitext(module_file)
  if module_dir not in sys.path:
    sys.path.append(module_dir)
  return module_dir, module_name


  ####################################################################################################################################
#
# DEFAULT CLASS NBODY
#
####################################################################################################################################


class Nbody:
  '''
  This is the reference Nbody class.


  This is the constructor for the **Nbody** object. Optional arguments are:

  p_name      : name of the file
                in case of multiple files, files must be included in a list ["file1","file2"]

  pos         : positions (3xN array)
  vel         : positions (3xN array)
  mass        : positions (1x array)
  num         : id of particles (1xN array)
  tpe         : type of particles (1xN array)

  ftype       : type of input file (binary,ascii)

  status      : 'old' : open an old file
                'new' : create a new object

  byteorder   : 'little' or 'big'
  pio         : parallel io : 'yes' or 'no'

  local       : True=local object, False=global object (paralellized)	Not implemeted Yet

  log         : log file

  unitsfile   : define the type of units


  by default this class initialize the following variables :

    self.p_name       : name of the file(s) to read or write

    self.pos          : array of positions
    self.vel          : array of velocities
    self.mass         : array of masses
    self.num          : array of id
    self.tpe          : array of types

    self.ftype        : type of the file
    self.status       : object status ('old' or 'new')
    self.byteorder    : byter order ('little' or 'big')
    self.pio          : parallel io ('yes' or 'no')
    self.log          : log object


    # new variables

    self.nbody        : local number of particles
    self.nbody_tot    : total number of particles
    self.mass_tot     : total mass
    self.npart        : number of particles of each type
    self.npart_tot    : total number of particles of each type
    self.spec_vars    : dictionary of variables specific for the format used
    self.spec_vect    : dictionary of vector specific for the format used


  '''

  def __init__(self,p_name=None,pos=None,vel=None,mass=None,num=None,tpe=None,ftype='default',status='old',byteorder=sys.byteorder,pio='no',local=False,log=None,unitsfile=None,skipped_io_blocks=[]):


    #################################
    # init vars
    #################################


    if p_name is None:
      status = 'new'
    if status=="new":
      self.verbose=False
    else:
      self.verbose=True

    self.set_filenames(p_name,pio=pio)
    self.pos = pos
    self.vel = vel
    self.mass = mass
    self.num  = num
    self.tpe = tpe

    self.ftype = ftype
    self.status = status
    self.byteorder = byteorder
    self.pio = pio
    self.log = log

    self.nbody = None
    self.nbody_tot = None
    self.mass_tot  = None
    self.npart = None
    self.npart_tot = None

    self.unitsfile = unitsfile
    self.localsystem_of_units=None

    self.skipped_io_blocks = skipped_io_blocks

    #################################
    # check format
    #################################

    if status != "new":
      self.find_format(ftype)

    #################################
    # Extend format
    #################################

    self.extend_format()

    #################################
    # init units
    #################################
    
    self.init_units()

    #################################
    # init some parameters before reading
    #################################
    
    self._init_pre()


    #################################
    # init other parameters
    #################################

    self.parameters      = param.Params(PARAMETERFILE,None)
    self.defaultparameters = self.parameters.get_dic()


    # log
    if self.log is None:
      self.log = liblog.Log(os.path.join(HOME,'.nbodylog'),show='yes')


    ###################################################
    # in case of an old file, open and read the file(s)
    ###################################################

    if status=='old':
      self.read()


    ###################################################
    # in case of a new file
    ###################################################

    elif status=='new':

      for i in range(len(self.p_name)):
        if self.p_name[i] is None:
           self.p_name[i] = 'file.dat'



    ###################################################
    # final initialisation
    ###################################################
    self.init()


    ###################################################
    # check consistency
    ###################################################
    # to be done



  #################################
  #
  # init functions
  #
  #################################

  #################################
  def _init_pre(self):
  #################################
    """
    Initialize some variables before reading.
    """
    pass


  #################################
  def _init_spec(self):
  #################################
    """
    Initialize specific variable for the current format
    """
    pass
    
  #################################  
  def get_excluded_extension(self):
  #################################
    """
    Return a list of file to avoid when extending the default class.
    """
    return []
    

  #################################
  def import_check_ftype(self, filename):
  #################################
    """
    Import check_spec_ftype from the format file.
    """
    module_dir, module_name = get_module_name(filename)
    if module_dir not in sys.path:
      sys.path.append(module_dir)
    mod = __import__(module_name)

    # look a all classes in the loaded module
    clsmembers = inspect.getmembers(mod, inspect.isclass)
    if len(clsmembers) != 1:
      raise Exception.ImportError("Module %s should contains exactly 1 class!" % module_name)
    cls = clsmembers[0][1]
    methods = get_methods(cls)
    check_name = "check_spec_ftype"
    for name, m in methods:
      if name == check_name:
        m = m.__get__(self, self.__class__)
        setattr(self, name, m)
        return
    raise Exception.ImportError("% not found in module %s!" % (check_name, module_name))

  #################################
  def find_format(self, default):
  #################################
    """
    Test the default format and if not good, test a few.
    :returns: format name
    """
    ftypes = []

    # add the default format
    if default is not None:
      ftypes.append(default)    
      
            
    preferred_format = FORMATSDIR + "/" + PREFERRED_FORMATFILE + ".py"
    if os.path.isfile(preferred_format):
      module_dir, module_name = get_module_name(preferred_format)
      mod = __import__(module_name)
      ftypes.extend(mod.ftype)


    tmp = glob.glob(os.path.join(FORMATSDIR,'*.py'))
    for i in range(len(tmp)):
      module_dir, module_name = get_module_name(tmp[i])
      if module_name not in ftypes and module_name != PREFERRED_FORMATFILE:
        ftypes.append(module_name)
    
    for ftype in ftypes:
      # find the right file
      formatfile = os.path.join(FORMATSDIR,"%s.py"%ftype)

      try:
        formatsfiles.index(formatfile)
      except ValueError:
        print "format %s is unknown !"%ftype
        print "%s does not exists"%formatfile
        sys.exit()

      self.import_check_ftype(formatfile)
      try:
        self.check_ftype()
      except error.FormatError as e:
        #print "Error with format %s"%e.value
        print "the format file is not %s"%ftype
        continue         # to the next format
      self.ftype = ftype
      return

    raise error.FormatError("Not able to read the data, format not found")

  #################################
  def extend_format(self):
  #################################
    """
    Extend format with format file (e.g. gh5) and extensions (config/extension)
    """
    
        
    formatfile = os.path.join(FORMATSDIR,"%s.py" % self.ftype)
    self._extend_format(formatfile)    
    
    
    # first, force to load the default extension
    ext = os.path.join(CONFIGDIR,EXTENSIONS,'%s.py'%DEFAULT_EXTENSION)
    self._extend_format(ext)


    # do not continue in case we want to exclude all other extensions
    if self.get_excluded_extension() == "all":
      return
       
    
    # add other extensions
    for EXTENSIONSDIR in EXTENSIONSDIRS:
    
      extension_files = glob.glob(os.path.join(EXTENSIONSDIR,'*.py'))
      for ext in extension_files:
        tmp, module_name = get_module_name(ext)       
        
        if module_name not in self.get_excluded_extension():
          self._extend_format(ext)



  #################################
  def _extend_format(self, filename):
  #################################
    """
    Extend format with class in file
    """
    module_dir, module_name = get_module_name(filename)
    if module_dir not in sys.path:
      #sys.path.append(module_dir)
      sys.path.insert(0,module_dir)     # append to the top of the list, this will ensure
                                        # that the imported module is the one in module_dir
                                        # in case we have different modules with the same name
                                        # but in fact, this does not work...
    mod = __import__(module_name)
    
    # look at all classes in the loaded module
    clsmembers = inspect.getmembers(mod, inspect.isclass)
        
    for clsname, cls in clsmembers:
      methods = get_methods(cls)
      for name, m in methods:
        m = m.__get__(self, self.__class__)
        setattr(self, name, m)
        
  
  #################################
  def init(self):
  #################################
    '''
    Initialize normal and specific class variables
    '''
    self._init_spec()

    # 1) find the number of particles
    self.nbody = self.get_nbody()

    # 2) define undefined vectors

    if self.pos is None:
      self.pos = zeros((self.nbody,3),float32)
      self.pos  = self.pos.astype(float32)
    else:
      self.pos = self.pos.astype(float32)

    if self.vel is None:
      self.vel = zeros((self.nbody,3),float32)
      self.vel  = self.vel.astype(float32)
    else:
      self.vel = self.vel.astype(float32)

    if self.mass is None:
      self.mass = ones((self.nbody, ),float32)/self.nbody
      self.mass = self.mass.astype(float32)
    else:
      self.mass = self.mass.astype(float32)

    if self.tpe is None:
      self.tpe = zeros(self.nbody,int)
      self.tpe  = self.tpe.astype(int)
    else:
      self.tpe = self.tpe.astype(int)

    if self.num is None:
      self.num = self.get_num()
      self.num  = self.num.astype(int)
    else:
      self.num = self.num.astype(int)



    # 3) other variables

    self.nbody_tot = self.get_nbody_tot()
    self.mass_tot = self.get_mass_tot()
    self.npart = self.get_npart()
    self.npart_tot = self.get_npart_tot()



    # Init specific class variables
    # (may be redundant with make_specific_variables_global)

    self.spec_vars = self.get_default_spec_vars()
    list_of_vars = self.get_list_of_vars()

    for name in self.spec_vars.keys():
      try:
        list_of_vars.index(name)
      except ValueError:
        setattr(self, name, self.spec_vars[name])

    # Init specific class vectors
    self.spec_vect = self.get_default_spec_array()
    list_of_vect = self.get_list_of_array()


    for name in self.spec_vect.keys():
      try:
        list_of_vect.index(name)
      except ValueError:
        setattr(self, name, ones(self.nbody,self.spec_vect[name][1])*self.spec_vect[name][0])


    # sph parameters/variables
    self.InitSphParameters()

  #################################
  def check_ftype(self):
  #################################
    "check the file format"

    for i in range(len(self.p_name)):

      name = self.p_name[i]

      #print "checking...", name

      # check p_name
      io.checkfile(name)
      # open file
      f = open(name,'r')
      self.check_spec_ftype(f)


  #################################
  def get_format_file(self):
  #################################
    "return the format file"
    return self._formatfile


  #################################
  def get_ftype(self,ftype='binary'):
  #################################
    """
    get the current used format
    """
    return self.ftype

  #################################
  def set_ftype(self,ftype='binary'):
  #################################
    """
    Change the type of the file

    ftype	: type of the file
    """

    if mpi.NTask > 1:
      raise "Warning","set_ftype function is currently not suported with multi proc."

    new = Nbody(status='new',ftype=ftype)

    # now, copy all var linked to the model
    for name in self.get_list_of_vars():
      if name != 'ftype':
        setattr(new, name, getattr(self,name))

    # now, copy all array linked to the model
    for name in self.get_list_of_array():
      vec = getattr(self,name)
      setattr(new, name, vec)


    # other vars
    new.init()

    return new


  #################################
  def get_num(self):
  #################################
    """
    Compute the num variable in order to be consistent with particles types
    """

    # compute npart_all
    if self.npart is None:
      npart = self.get_npart()
    else:
      npart = self.npart

    npart_all = array(mpi.mpi_allgather(npart))

    return mpi.mpi_sarange(npart_all) # + 1


  #################################
  def get_default_spec_vars(self):
  #################################
    '''
    return specific variables default values for the class
    '''
    return {}

  #################################
  def get_default_spec_array(self):
  #################################
    '''
    return specific array default values for the class
    '''
    return {}


  #################################
  def set_pio(self,pio):
  #################################
    """
    Set parallel input/output or not io

    pio : 'yes' or 'no'
    """

    self.pio = pio
    self.set_filenames(self.p_name_global,pio=pio)
    if pio=='yes':
      self.num_files = mpi.NTask
    else:
      self.num_files = 1



  #################################
  def rename(self,p_name=None):
  #################################
    """
    Rename the files

    p_name : new name(s)
    """
    if p_name is not None:
      self.set_filenames(p_name,pio=self.pio)

  #################################
  def set_filenames(self,p_name,pio=None):
  #################################
    """
    Set the local and global names

    p_name : new name(s)
    pio    : 'yes' or 'no'
    """
    if type(p_name) ==  types.ListType:

       self.p_name_global = []
       self.p_name        = []
       for name in p_name:

         if pio == 'yes':
           self.p_name_global.append(name)
           self.p_name.append("%s.%d"%(name,mpi.mpi_ThisTask()))
         else:
           self.p_name_global.append(name)
           self.p_name.append(name)

    else:

      if pio == 'yes':
        self.p_name_global = [p_name]
        self.p_name        = ["%s.%d"%(p_name,mpi.mpi_ThisTask())]
      else:
        self.p_name_global = [p_name]
        self.p_name        = [p_name]

  #################################
  def get_ntype(self):
  #################################
    """
    return the number of paticles types
    """
    return len(self.npart)



  #################################
  def get_nbody(self):
  #################################
    """
    Return the local number of particles.
    """

    if self.pos is not None:
      nbody = len(self.pos)

    elif self.vel is not None:
      nbody = len(self.vel)

    elif self.mass is not None:
      nbody = len(self.mass)

    elif self.num is not None:
      nbody = len(self.num)

    elif self.tpe is not None:
      nbody = len(self.tpe)

    else:
      nbody = 0

    return nbody



  #################################
  def get_nbody_tot(self):
  #################################
    """
    Return the total number of particles.
    """
    nbody_tot = mpi.mpi_allreduce(self.nbody)
    return nbody_tot


  #################################
  def get_npart(self):
  #################################
    """
    Return the local number of particles of each types,
    based on the variable tpe
    """
    npart = array([],int)
    n = 0

    if self.tpe is None:
      return npart.tolist()

    for tpe in range(self.get_mxntpe()):
      np = sum( (self.tpe==tpe).astype(int) )
      npart = concatenate((npart,array([np])))

      n = n + np

    if n != self.nbody:
      print "get_npart : n (=%d) is different from self.nbody (=%d)"%(n,self.nbody)
      raise "get_npart : n  is different from self.nbody"


    return npart.tolist()



  #################################
  def get_npart_tot(self):
  #################################
    """
    Return the total number of particles of each types.
    """

    npart = array(self.npart)
    npart_tot = mpi.mpi_allreduce(npart)
    npart_tot = npart_tot.tolist()


    return npart_tot





  #################################
  def get_npart_all(self,npart_tot,NTask):
  #################################
    '''
    From npart_tot, the total number of particles per type,
    return npart_per_proc, an array where each element corresponds
    to the value of npart of each process.
    '''

    if (type(npart_tot) != types.ListType) and (type(npart_tot) !=ndarray):
      npart_tot = array([npart_tot])


    ntype = len(npart_tot)
    npart_all = zeros((NTask,ntype))

    for i in range(len(npart_tot)):
      for Task in range(NTask-1,-1,-1):
        npart_all[Task,i] =  npart_tot[i]/NTask +  npart_tot[i]%NTask*(Task==0)

    return npart_all




  #################################
  def get_npart_and_npart_all(self,npart):
  #################################
    '''
    From npart (usually read for the header of a file), compute :

    npart     : number of particles in each type
    npart_tot : total number of particles in each type
    npart_all : npart for each process.

    '''



  #################################
  def get_mxntpe(self):
  #################################
    '''
    Return the max number of type for this format

    '''
    return 6


  #################################
  def make_default_vars_global(self):
  #################################
    '''
    Make specific variables global
    '''

    self.spec_vars = self.get_default_spec_vars()

    for name in self.spec_vars.keys():
      if not self.has_var(name):
        setattr(self, name, self.spec_vars[name])





  #################################
  def set_npart(self,npart):
  #################################
    """
    Set the local number of particles of each types.
    This function modifies the variable self.tpe
    """

    if sum(array(npart)) > self.nbody:
      raise "Error (set_npart)","sum(npart) is greater than nbody"


    i = 0
    n0 = 0
    for n in npart:
      self.tpe[n0:n0+n] = ones(n)*i
      i = i + 1
      n0 = n0+n


    self.tpe[n0:self.nbody] = ones(self.nbody-n0)*i


    self.npart     = self.get_npart()
    self.npart_tot = self.get_npart_tot()


  #################################
  def set_tpe(self,tpe):
  #################################
    """
    Set all particles to the type tpe
    """

    self.tpe = ones(self.nbody)*tpe

    self.npart     = self.get_npart()
    self.npart_tot = self.get_npart_tot()



  #################################
  #
  # parameters functions
  #
  #################################

  '''
  Warning, these routines are a bit bad...
  '''

  def set_parameters(self,params):
    '''
    Set parameters for the class
    '''
    self.parameters = param.Params(PARAMETERFILE,None)
    self.parameters.params = params.params

    self.defaultparameters = self.parameters.get_dic()

  #################################
  #
  # units functions
  #
  #################################
  '''

  There is several ways to set the units in pNbody
  In an object, the units are stored in

  self.localsystem_of_units

  which is a UnitSystem object defined in units.py

  We define a unit system by giving   Unit_lenght,  Unit_mass, Unit_time, Unit_K, Unit_mol, and Unit_C
  Actually only Unit_lenght,  Unit_mass, Unit_time are used, all are Units object (units.py)

  Following Gadget2, easy ways to definde units is to give three floats,

  UnitVelocity_in_cm_per_s
  UnitMass_in_g
  UnitLength_in_cm

  This is done using the method

  self.set_local_system_of_units()

  which uses UnitVelocity_in_cm_per_s,UnitMass_in_g,UnitLength_in_cm if they are given,
  or read a gadget parameter file
  or read a pNbody unitsparameter file
  or use the default unitsparameter file.


  '''



  def init_units(self):
    '''
    This function is responsible for the units initialization.

    It will create :

      self.unitsparameters

        that contains parameters like
          - the hydrogen mass fraction,
          - the metalicity ionisation flag
          - the adiabatic index
          - ...

    and

      self.localsystem_of_units

         a UnitSystem object that really defines the system of units
         in the Nbody object. It uses the values :

           UnitLength_in_cm
           UnitMass_in_g
           UnitVelocity_in_cm_per_s


    All physical values computed in pNbody should use self.localsystem_of_units	to
    be converted in other units.
    self.unitsparameters is usefull if other parameters needs to be known, like
    the adiabatic index, etc.
    '''


    # do not init the system of unit if it already exists
    if self.localsystem_of_units is not None:
      return



    self.unitsparameters = param.Params(UNITSPARAMETERFILE,None)

    if self.unitsfile is not None:


      ##############################################################
      # 1) this part should be only in the gadget.py format file, no ?	BOF, non
      # 2) we could simplify using self.set_local_system_of_units()
      # 3) and some options -> but this needs to update self.unitsparameters
      ##############################################################

      # if it is a gadget parameter file
      try:
        gparams = io.read_params(self.unitsfile)

        self.unitsparameters.set('HubbleParam',             gparams['HubbleParam'])
        self.unitsparameters.set('UnitLength_in_cm',        gparams['UnitLength_in_cm'])
        self.unitsparameters.set('UnitMass_in_g',           gparams['UnitMass_in_g'])
        self.unitsparameters.set('UnitVelocity_in_cm_per_s',gparams['UnitVelocity_in_cm_per_s'])


        # those parameters may be in the header of the file
        self.unitsparameters.set('Omega0',                  gparams['Omega0'])
        self.unitsparameters.set('OmegaLambda',             gparams['OmegaLambda'])
        self.unitsparameters.set('OmegaBaryon',             gparams['OmegaBaryon'])
        self.unitsparameters.set('BoxSize',                 gparams['BoxSize'])
        self.unitsparameters.set('ComovingIntegrationOn',   gparams['ComovingIntegrationOn'])

        #self.set_local_system_of_units(gadgetparameterfile=self.unitsfile)

      except:

        # try to read a pNbody units file
        try:
          self.unitsparameters = param.Params(self.unitsfile,None)
          #self.set_local_system_of_units(unitparameterfile=self.unitsfile)
        except:
          raise IOError(015,'format of unitsfile %s unknown ! Pease check.'%(self.unitsfile))




    # define local system of units it it does not exists
    #if not self.has_var("localsystem_of_units"):
    self.set_local_system_of_units()

    # print info
    #self.localsystem_of_units.info()







  def set_unitsparameters(self,unitsparams):
    '''
    Set units parameters for the class.
    '''

    print "!!!!!! in set_unitsparameters  !!!!"
    print "!!!!!! this is bad    !!!! we should never use UNITSPARAMETERFILE"
    print "!!!!!! this is bad    !!!! we should never use UNITSPARAMETERFILE"

    self.unitsparameters = param.Params(UNITSPARAMETERFILE,None)
    self.unitsparameters.params = unitsparams.params
    self.set_local_system_of_units()


  def set_local_system_of_units(self,params=None,UnitLength_in_cm=None,UnitVelocity_in_cm_per_s=None,UnitMass_in_g=None,unitparameterfile=None,gadgetparameterfile=None):
    '''
    Set local system of units using UnitLength_in_cm,UnitVelocity_in_cm_per_s,UnitMass_in_g

    1) if nothing is given, we use self.unitsparameters to obtain these values

    2) if UnitLength_in_cm
          UnitVelocity_in_cm_per_s
          UnitMass_in_g
       are given, we use them

    2b) if    UnitLength_in_cm,UnitVelocity_in_cm_per_s,UnitMass_in_g
        are given in a dictionary

    3) if unitparameterfile   is given we read the parameters from the file (units parameter format)

    4) if gadgetparameterfile is given we read the parameters from the file (gadget param format)
    '''


    if gadgetparameterfile is not None:
      params = io.read_params(gadgetparameterfile)
      #print "Units Set From %s"%gadgetparameterfile

    elif unitparameterfile is not None:

      unitsparameters = param.Params(unitparameterfile,None)

      params = {}
      params['UnitLength_in_cm']         = unitsparameters.get('UnitLength_in_cm')
      params['UnitVelocity_in_cm_per_s'] = unitsparameters.get('UnitVelocity_in_cm_per_s')
      params['UnitMass_in_g']            = unitsparameters.get('UnitMass_in_g')
      #print "Units Set From %s"%unitparameterfile

    elif params is not None:
      pass
      #print "Units Set From %s"%params

    elif UnitLength_in_cm is not None and UnitVelocity_in_cm_per_s is not None and UnitMass_in_g is not None:
      params = {}
      params['UnitLength_in_cm']         = UnitLength_in_cm
      params['UnitVelocity_in_cm_per_s'] = UnitVelocity_in_cm_per_s
      params['UnitMass_in_g']            = UnitMass_in_g
      #print "Units Set From UnitLength_in_cm,UnitVelocity_in_cm_per_s,UnitMass_in_g"

    else:
      params = {}
      params['UnitLength_in_cm']         = self.unitsparameters.get('UnitLength_in_cm')
      params['UnitVelocity_in_cm_per_s'] = self.unitsparameters.get('UnitVelocity_in_cm_per_s')
      params['UnitMass_in_g']            = self.unitsparameters.get('UnitMass_in_g')
      #print "Units Set From %s (%s)"%("self.unitsparameters",self.unitsparameters.filename)


    # now, create the
    self.localsystem_of_units = units.Set_SystemUnits_From_Params(params)


  #################################
  #
  # info functions
  #
  #################################

  #################################
  def info(self):
  #################################
    """
    Write info
    """

    infolist = []
    infolist.append("-----------------------------------")

    if mpi.NTask>1:
      infolist.append("")
      infolist.append("ThisTask            : %s"%mpi.ThisTask.__repr__())
      infolist.append("NTask               : %s"%mpi.NTask.__repr__())
      infolist.append("")

    infolist.append("particle file       : %s"%self.p_name.__repr__())
    infolist.append("ftype               : %s"%self.ftype.__repr__())
    infolist.append("mxntpe              : %s"%self.get_mxntpe().__repr__())
    infolist.append("nbody               : %s"%self.nbody.__repr__())
    infolist.append("nbody_tot           : %s"%self.nbody_tot.__repr__())
    infolist.append("npart               : %s"%self.npart.__repr__())
    infolist.append("npart_tot           : %s"%self.npart_tot.__repr__())
    infolist.append("mass_tot            : %s"%self.mass_tot.__repr__())
    infolist.append("byteorder           : %s"%self.byteorder.__repr__())
    infolist.append("pio                 : %s"%self.pio.__repr__())
    if self.nbody != 0:
      infolist.append("")
      infolist.append("len pos             : %s"%len(self.pos).__repr__())
      infolist.append("pos[0]              : %s"%self.pos[0].__repr__())
      infolist.append("pos[-1]             : %s"%self.pos[-1].__repr__())
      infolist.append("len vel             : %s"%len(self.vel).__repr__())
      infolist.append("vel[0]              : %s"%self.vel[0].__repr__())
      infolist.append("vel[-1]             : %s"%self.vel[-1].__repr__())
      infolist.append("len mass            : %s"%len(self.mass).__repr__())
      infolist.append("mass[0]             : %s"%self.mass[0].__repr__())
      infolist.append("mass[-1]            : %s"%self.mass[-1].__repr__())
      infolist.append("len num             : %s"%len(self.num).__repr__())
      infolist.append("num[0]              : %s"%self.num[0].__repr__())
      infolist.append("num[-1]             : %s"%self.num[-1].__repr__())
      infolist.append("len tpe             : %s"%len(self.tpe).__repr__())
      infolist.append("tpe[0]              : %s"%self.tpe[0].__repr__())
      infolist.append("tpe[-1]             : %s"%self.tpe[-1].__repr__())


    if self.spec_info() is not None:
      infolist = infolist + self.spec_info()

    all_infolist = mpi.mpi_allgather(infolist)

    if mpi.mpi_IsMaster():
      for infolist in all_infolist:
        for line in infolist:
          #print line
          self.log.write(line)

  #################################
  def spec_info(self):
  #################################
    """
    Write specific info
    """
    return None

  #################################
  def object_info(self):
  #################################
    """
    Write class(object) info
    """
    list_of_vars = self.get_list_of_vars()
    list_of_array = self.get_list_of_array()

    self.log.write("#############################")
    self.log.write("list of vars")
    self.log.write("#############################")
    for name in list_of_vars:
      self.log.write("%s %s"%( name,str(type(getattr(self,name)))))

    self.log.write("#############################")
    self.log.write("list of arrays")
    self.log.write("#############################")
    for name in list_of_array:
      self.log.write("%s %s"%(name,str(type(getattr(self,name)))))

  #################################
  def nodes_info(self):
  #################################
    """
    Write info on nodes
    """

    all_npart = mpi.mpi_allgather(self.npart)
    all_nbody = mpi.mpi_allgather(self.nbody)

    if mpi.mpi_IsMaster():
      for Task in range(mpi.NTask):
         line = "Task=%4d nbody=%10d"%(Task,all_nbody[Task])

         line = line + " npart= "
         for npart in all_npart[Task]:
           line = line + "%10d "%npart

         self.log.write(line)


  #################################
  def memory_info(self):
  #################################
    """
    Write info on memory size of the current object (only counting arrays size)
    """

    total_size = 0
    array_size = 0

    elts = self.get_list_of_array()
    for elt in elts:

      #num_of_elts = getattr(self,elt).size
      #byte_per_elts = getattr(self,elt).itemsize
      #bytes = num_of_elts*byte_per_elts
      bytes = getattr(self,elt).nbytes

      total_size = total_size + bytes
      array_size = array_size + bytes

      print "(%d) %10s %14d"%(mpi.ThisTask,elt,bytes)

    #elts = self.get_list_of_vars()
    #for elt in elts:

    array_size = mpi.mpi_reduce(array_size)		# only the master return the info
    total_size = mpi.mpi_reduce(total_size)

    if mpi.mpi_IsMaster():

      print "total size = %d octets"%(total_size)

      if array_size < 1024:
        print "total arrays size = %d octets"%(array_size)
      else:

        array_size = array_size/1024.0
        if array_size < 1024:
          print "total arrays size = %dK"%(array_size)
        else:

          array_size = array_size/1024.0
          if array_size < 1024:
            print "total arrays size = %dM"%(array_size)
          else:

            array_size = array_size/1024.0
            if array_size < 1024:
              print "total arrays size = %dG"%(array_size)




  #################################
  def print_filenames(self):
  #################################
    """
    Print files names
    """

    self.log.write("p_name_global = %s"%str(self.p_name_global))
    self.log.write("p_name        = %s"%str(self.p_name))


  #################################
  #
  # list of variables functions
  #
  #################################



  def get_list_of_array(self):
    """
    Return the list of numpy vectors of size nbody.
    """
    list_of_arrays = []
    for name in dir(self):
      if type(getattr(self,name)) == ndarray:
        if len(getattr(self,name)) == self.nbody:
          #if (name!="nall") and (name!="nallhw") and (name!="massarr") and (name!="npart") and (name!="npart_tot"):
          list_of_arrays.append(name)
    return list_of_arrays


  def get_list_of_method(self):
    """
    Return the list of instance methods (functions).
    """
    list_of_instancemethod = []
    for name in dir(self):
      if type(getattr(self,name)) == types.MethodType:
        list_of_instancemethod.append(name)
    return list_of_instancemethod


  def get_list_of_vars(self):
    """
    Get the list of vars that are linked to the model
    """
    list_of_allvars = dir(self)
    list_of_arrays = self.get_list_of_array()
    list_of_method = self.get_list_of_method()

    for name in  list_of_arrays:
      list_of_allvars.remove(name)

    for name in  list_of_method:
      list_of_allvars.remove(name)

    #list_of_allvars.remove('log')
    #list_of_allvars.remove('read_fcts')        # becose these vars are linked to fcts
    #list_of_allvars.remove('write_fcts')       # should be definitely removed

    return list_of_allvars

  def has_var(self,name):
    '''
    Return true if the object pNbody has
    a variable called self.name
    '''
    get_list_of_vars = self.get_list_of_vars()
    try:
      getattr(self,name)
      return True
    except AttributeError:
      return False

  def has_array(self,name):
    '''
    Return true if the object pNbody has
    an array called self.name
    '''
    list_of_array = self.get_list_of_array()
    try:
      list_of_array.index(name)
      return True
    except ValueError:
      return False


  def find_vars(self):
    '''
    This function return a list of variables defined in the current object
    '''

    elts = dir(self)
    lst = []

    for elt in elts:
      exec("obj = self.%s"%(elt))
      if type(obj) != types.MethodType:
        lst.append(elt)

    return lst



  #################################
  #
  # check special values
  #
  #################################

  def check_arrays(self):
    '''
    check if the array contains special values like NaN or Inf
    '''

    status = 0

    for name in self.get_list_of_array():
      vec = getattr(self,name)

      # check nan

      if isnan(vec).any():
        msg = "array %s contains Nan !!!"%name
        warnings.warn(msg)
        status = 1

      # check nan
      if isinf(vec).any():
        msg = "array %s contains Inf !!!"%name
        warnings.warn(msg)
        status = 1

    return status


  #################################
  #
  # read/write functions
  #
  #################################


  def read(self):
    """
    Read the particle file(s)
    """
    for i in range(len(self.p_name)):
      self.open_and_read(self.p_name[i],self.get_read_fcts()[i])

    self.make_default_vars_global()


  def open_and_read(self,name,readfct):
    '''
    open and read file name

    name     : name of the input
    readfct  : function used to read the file
    '''

    # check p_name
    if self.pio=='yes' or mpi.mpi_IsMaster():
      io.checkfile(name)

    # get size
    if self.pio=='yes' or mpi.mpi_IsMaster():
      isize = os.path.getsize(name)

    # open file
    if self.pio=='yes' or mpi.mpi_IsMaster():
      f = open(name,'r')
    else:
      f = None
    # read the file
    readfct(f)
    
    if self.pio=='yes' or mpi.mpi_IsMaster():
      fsize = f.tell()
    else:
      fsize = None

    if self.pio=='yes' or mpi.mpi_IsMaster():
      if fsize != isize:
        raise IOError("file %s not read completely"%name)

    # close file
    if self.pio=='yes' or mpi.mpi_IsMaster():
      f.close()

  def get_read_fcts(self):
    """
    returns the functions needed to read a snapshot file.
    """
    return []



  def write(self):
    """
    Write the particle file(s)
    """

    for i in range(len(self.p_name)):
      self.open_and_write(self.p_name[i],self.get_write_fcts()[i])


  def open_and_write(self,name,writefct):
    """
    Open and write file

    name     : name of the output
    writefct : function used to write the file
    """

    if self.pio=='yes' or mpi.mpi_IsMaster():
      f = open(name,'w')
    else:
      f = None

    writefct(f)

    if self.pio=='yes' or mpi.mpi_IsMaster():
      f.close()


  def get_write_fcts(self):
    """
    returns the functions needed to write a snapshot file.
    """
    return []



  def write_num(self,name):
    """
    Write a num file

    name     : name of the output
    """

    if self.pio =='yes':

      f = open("%s.%d"%(name,mpi.ThisTask),'w')
      for n in self.num:
        f.write('%8i\n'%(n))
      f.close()

    else:

      if mpi.mpi_IsMaster():

        f = open(name,'w')

        for Task in range(mpi.NTask-1,-1,-1):

          if Task != 0:
            num = mpi.mpi_recv(source = Task)
            for n in num:
              f.write('%8i\n'%(n))
          else:
            for n in self.num:
              f.write('%8i\n'%(n))

      else:
        mpi.mpi_send(self.num, dest = 0)



  def read_num(self,name):
    """
    Read a num file

    name     : name of the input
    """


  def skip_io_block(self,s):

    #self.skipped_io_blocks = ['vel','num','u','rho','metals','tstar','minit','idp']

    c = self.skipped_io_blocks.count(s)
    if c==0:
      return False
    else:
      return True
