''' 
 @package   pNbody
 @file      error.py
 @brief     Defines a few error class
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''


class pNbodyError(Exception):
  """
  a simple new error
  """
  pass



class FormatError(Exception):
  """
  format error
  """
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)





