#!/usr/bin/env python
'''
@package   pNbody
@file      libvazdekis.py
@brief     Vazdekis luminosities
@copyright GPLv3
@author    Yves Revaz <yves.revaz@epfl.ch>
@section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL
'''

import sys,os
import types,string
import scipy
import scipy.interpolate
from numpy import *

from libSSPluminosity import SSPLuminosities


#####################################################
def read_ascii(file,columns=None,lines=None,dtype=float,skipheader=False,cchar='#'):	
#####################################################     	 
  """[X,Y,Z] = READ('FILE',[1,4,13],lines=[10,1000])	       
  Read columns 1,4 and 13 from 'FILE'  from line 10 to 1000    
  into array X,Y and Z
  
  file is either fd or name file
  				       
  """ 


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





class VazdekisLuminosities(SSPLuminosities):


  def Read(self):
    '''
    read file and create a data table
    '''
    self.data = read_ascii(self.file,cchar='#',skipheader=True)   


  def CreateMatrix(self):
    '''
    from data extract 
    metalicites (zs)
    ages (ages)    
    and ML (vs)
    '''

    zs   = self.data[1,:]
    ages = self.data[2,:]
    mls  = self.data[20,:]
  
    # create borders
    Zs   = [-2.3152,-1.7129,-1.3146,-0.7052,-0.3960,0.0000,0.2223]
    Ages = compress(Zs[1]==zs,ages)
    
    MatLv = zeros((len(Zs),len(Ages)))
    
    for iZ,Z in enumerate(Zs):
    
      zs,ages,mls
    
      c = (zs==Z)
    
      age = compress(c,ages)
      ml  = compress(c,mls)
      Lv = 1/ml
      
      if len(age)<len(Ages):
	n = len(Ages)-len(age)
	age = concatenate((Ages[:n],age))
	Lv  = concatenate((1e-10*ones(n),Lv)) 
      
      MatLv[iZ,:] = Lv
    
    self.MatLv = MatLv
    self.Ages  = Ages
    self.Zs    = Zs
 
