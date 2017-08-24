#!/usr/bin/env python

'''
 @package   pNbody
 @file      makesnapshot.py
 @brief     Create a snapshot
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody.
'''

from pNbody import *
from pNbody import ic

from optparse import OptionParser


########################################  
#
# parser
#
######################################## 

def parse_options():

  usage = "usage: %prog [options] file"
  parser = OptionParser(usage=usage)


  parser.add_option("-t",
		   action="store", 
		   dest="ftype",
		   type="string",
		   default = 'simpleformat',		   
		   help="type of the file",	 
		   metavar=" TYPE")    
		   
  parser.add_option("-f",
		   action="store", 
		   dest="file",
		   type="string",
		   default = 'snap.dat',		   
		   help="output file name",	 
		   metavar=" FILE")    
		   
  parser.add_option("-n",
		   action="store", 
		   dest="n",
		   type="int",
		   default = 2**14,		   
		   help="number of particles",	 
		   metavar=" INT")   
		   		   

  (options, args) = parser.parse_args()
  
  files = args     
  
  return files,options


#################################		   
#						   
# main				   
#						   
#################################


files,opt = parse_options()



ftype = opt.ftype
file  = opt.file

# create file and save it
nb = ic.expd(n=opt.n,Hr=3.,Hz=0.3,Rmax=20,Zmax=2,irand=1,name=file,ftype=ftype)
nb.write()

print "%s as been dumped."%file


