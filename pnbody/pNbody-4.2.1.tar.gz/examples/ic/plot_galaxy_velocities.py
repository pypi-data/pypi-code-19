#!/usr/bin/env python
'''
 @package   pNbody
 @file      plot_galaxy_velocities.py
 @brief     Plot galaxy velocities from the command line
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

import sys

import Ptools as pt
from numpy import *

from pNbody import libmiyamoto


ltypes = ["-","--",":","o"]

files = sys.argv[1:]


fig = pt.figure()
pt.subplot(1,1,1)


i = 0
for file in files:

  stats_d = pt.io.read_dmp(file)



  ###################
  # plot
  ###################


  #r = stats_h['r']
  R = stats_d['R']





  ####################
  # velocity curves
  ####################

  pt.plot(R,stats_d['vc'],'k'+ltypes[i])
  pt.plot(R,stats_d['vm'],'y'+ltypes[i])
  pt.plot(R,stats_d['sr'],'r'+ltypes[i])
  pt.plot(R,stats_d['sp'],'g'+ltypes[i])
  pt.plot(R,stats_d['sz'],'b'+ltypes[i])
  

  i = i + 1


pt.xlabel('Radius')
pt.ylabel('Velocity')

pt.legend(('vc','vm','sr','sp','sz'))


pt.show()

