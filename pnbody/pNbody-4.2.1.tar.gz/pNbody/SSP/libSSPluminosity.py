#!/usr/bin/env python
'''
@package   pNbody
@file      libSSPluminosity.py
@brief     SSP luminosities
@copyright GPLv3
@author    Yves Revaz <yves.revaz@epfl.ch>
@section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL
'''

import scipy
import scipy.interpolate
from numpy import *

import sys,os

from pNbody import *

class SSPLuminosities:

  def __init__(self,file):

    self.file = file
    
    # read file and crate self.data
    self.Read()
    
    # create the matrix
    self.CreateMatrix()


  def Read(self):
    '''
    read file and create a data table
    '''
    pass  


  def CreateMatrix(self):
    '''
    from data extract 
    metalicites (zs)
    ages (ages)    
    and ML (vs)
    '''

    pass
 

  def CreateInterpolator(self):
    """
    from the matrix self.MatLv, create a spline interpolator
    """
    self.spl = scipy.interpolate.RectBivariateSpline(self.Zs,self.Ages,self.MatLv)    


  def ExtrapolateMatrix(self,order=1,zmin=-5,zmax=2,nz=50,s=0):
    """
    extrapolate the matrix self.MatLv in 1d (using spline), along the Z axis
    The function create a new self.MatLv and self.Zs
    """
 
    xx = scipy.linspace(zmin,zmax,nz)
    
    newMatLv = zeros((len(xx),len(self.Ages)))

    for i in arange(len(self.Ages)):       

      Ls = self.MatLv[:,i]
      
      # 1d spline interpolation
      x = self.Zs
      y = Ls
    
      tck   = scipy.interpolate.fitpack.splrep(x,y,k=order,s=s)
      yy    = scipy.interpolate.fitpack.splev(xx,tck)

      newMatLv[:,i] = yy
    
    self.Zs    = xx
    self.MatLv = newMatLv


  def Extrapolate2DMatrix(self,zmin=-10,zmax=2,nz=256,agemin=None,agemax=None,nage=256):
    if agemin == None:
     agemin = min(self.Ages)
    if agemax == None:
     agemax = max(self.Ages)

    self.Zs    = scipy.linspace(zmin,zmax,nz)
    self.Ages  = 10**scipy.linspace(log10(agemin),log10(agemax),nage)
    #self.Ages  = scipy.linspace((agemin),(agemax),nage)
    
    self.MatLv = self.Luminosity(self.Zs,self.Ages)
    


  def GetAgeIndexes(self,Ages):
    """
    Get the indexes of the nearest values of self.Ages from Ages 
    """
    return self.Ages.searchsorted(Ages)
   
  def GetZIndexes(self,Zs):
    """
    Get the indexes of the nearest values of self.Zs from Zs 
    """
    return self.Zs.searchsorted(Zs)


  def Luminosity(self,Zs,Ages):
    '''
    return an interpolated value of Luminosity using self.slp
    from a given Zs and Ages
    '''
    
    MatLvi = self.spl(Zs,Ages)
    return MatLvi


  def Luminosities(self,Zs,Ages):
    '''
    return an interpolated value of Luminosity using self.slp
    from a given Zs and Ages
    '''
    
    i = self.Zs.searchsorted(Zs)
    j = self.Ages.searchsorted(Ages)
    i = i.clip(0,len(self.Zs  )-1)
    j = j.clip(0,len(self.Ages)-1)

    return self.MatLv[i,j]
    











