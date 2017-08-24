''' 
 @package   pNbody
 @file      param.py
 @brief     Deal with parameter files
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

try:
  import Tkinter as tk
  is_tk = True
except ImportError:
  is_tk = False


import string
import os
import sys
from numpy import *

def write_ascii_value(value,tpe,name):
  '''
  from a name and type and value, return
  an ascii representation of the object
  '''
    
  if tpe=='ArrayObs':
    if value != None:
      m = ravel(value)
      string = '[%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f]'%(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],m[8],m[9],m[10],m[11])
    else:
      string = str(value) 
  else:
    string = str(value) 
  	 
  return string   
  


def read_ascii_value(value,tpe,name):
  '''
  from a name and type, return
  an object corresponding to the value given
  '''
    
  if value == "None":
    return None

  if   tpe == 'Int':
    try:
      value = int(value)
    except:
      value = ""
    
  elif tpe == 'Float':
    try:
      value = float(value)
    except:
      value = ""  

  elif tpe == 'String':
    pass
    
  elif tpe == 'Tuple':
    try:
      exec('value = %s'%(value))
    except:
      value = 0
    
  elif tpe == 'List':
    try:
      exec('value = %s'%(value))
    except:
      value = 0

  elif tpe == 'ArrayObs':  
    try:
      exec('value = array(%s)'%(value))
      value.shape = (4,3)
    except:
      value = None
        
  else:
    return None
  
  # check the type
  if type(value)==gettype(tpe) or value==None:  
    return value
  else:
    print "wrong type returning None :",value,tpe,name
    return None  
      

def gettype(thetype):

  import types

  if   thetype == 'Int':
    return types.IntType
    
  elif thetype == 'Float':
    return types.FloatType    

  elif thetype == 'String':
    return types.StringType 

  elif thetype == 'Tuple':
    return types.TupleType 
    
  elif thetype == 'List':
    return types.ListType 
    
  elif thetype == 'List':
    return types.ListType     

  elif thetype == 'ArrayObs':
    return type(ones(1))   

  else:
    return None


class Params:
  """
    params = [['imwidth','image width','i',512],
              ['imheight','image height','i',384],	   
	      ['winwidth','window width','f',50.],	   
	      ['winheight','window height','f',37.5]]	
  """


  def __init__(self,filename,master):
  
    self.master = master
    self.params = []
    self.filename = filename   
    
    self.read()


  ###########################
  def set(self,name,value):
  ###########################
    '''
    set the value of a parameter
    '''  
  
    for param in self.params:
      if param[0]==name:   
        param[3] = value
	   


  ###########################
  def get(self,name):
  ###########################
    '''
    return the value of a parameter
    '''

    for param in self.params:  
      if param[0]==name:	       
    	return param[3]

  ###########################
  def get_type(self,name):
  ###########################
    '''
    return the type of a parameter
    '''

    for param in self.params:  
      if param[0]==name:	       
    	return param[2]
	
  ###########################
  def get_string(self,name):
  ###########################
    '''
    return the value of a parameter in a string
    '''

    for param in self.params:  
      if param[0]==name:	
	return write_ascii_value(param[3],param[2],param[0])



  ###########################
  def lists(self):
  ###########################
    '''
    print the list of the content of the class
    '''
    
    print 100*"-"
    print "%30s   %30s   %15s (%s)" %("name","meaning","value","type")
    print 100*"-"
  
    for param in self.params:
       
      name    = param[0]				    
      nikname = param[1]				    
      type    = param[2]				    
      value   = param[3]				    

      print "%30s : %30s = %15s (%s)" %(name,nikname,value,type)

  ###########################
  def get_dic(self):
  ###########################
    '''
    return values of parameters in a dictionary
    '''
  
    dict = {}
    
    for param in self.params:
       
      name    = param[0]				    
      value   = param[3]				    

      dict[name] = value
    
    return dict  

      
  ###########################
  def save(self,filename=None):
  ###########################
    ''' ['cd', 'cd', 'Float', 0.0] '''    
	
    if filename == None:
      filename = self.filename	

#    if not os.path.exists(filename):
#      print "%s does not exists"%(filename)
#      sys.exit() 
      
    f = open(filename,'w')
    
    for param in self.params:
      f.write("%s\n" %(param[0]))
      f.write("%s\n" %(param[1]))
      f.write("%s\n" %(param[2]))  
      f.write("%s\n" %(self.get_string(param[0])))
      f.write("\n")  
    f.close()   
    
  ###########################
  def read(self,filename=None):
  ###########################      
    
    self.params = []

    if filename == None:
      filename = self.filename	
           
    if not os.path.exists(filename):
      print "%s does not exists"%(filename)
      sys.exit() 
          
    f = open(filename,'r')
    
    while 1:  
      newparam = []
      line = f.readline()
      if  line == '': break
      
      
      newparam.append(string.strip(line)) 
      
      line = f.readline()
      newparam.append(string.strip(line)) 

      line = f.readline()
      newparam.append(string.strip(line)) 
      
      line = f.readline()
      newparam.append(string.strip(line)) 

      line = f.readline() 

      self.params.append(newparam)	
      
             
    f.close()
    
    # asign good value
    
    for param in self.params:
      var = read_ascii_value(param[3],param[2],param[0])
      param[3]=var 
      
    
      
        
      
      

  ###########################
  def edit(self):
  ###########################
        
    Form = ParamForm(self,self.master)




###########################
class ParamForm:
###########################

  def __init__(self,params,master=None):

    if is_tk:

      self.root=tk.Toplevel()
      self.master = master

      box = tk.Frame(self.root)
      box.grid(column=0,row=0,sticky=tk.E+tk.N+tk.S+tk.W)
    

      self.content = {} 
      # create all entries
      n = 0

      for param in params.params:				      
        name = param[0] 					      
        self.content[name] = entryCl(box,n,param,params)   
        n = n + 1

    
      but = tk.Frame(self.root)
      but.grid(column=0,row=1,sticky=tk.E+tk.N+tk.S+tk.W)

      tk.Button(but, text='Cancel', command=self.onCancel).pack(side=tk.RIGHT) 
      tk.Button(but, text='Ok', command=self.onSubmit).pack(side=tk.RIGHT) 
      tk.Button(but, text='Send', command=self.onSend).pack(side=tk.RIGHT) 

    else:
      print "Class ParamForm : tk is not present"
   
     

  def onSubmit(self):

    lst = self.content.keys()
    for entry in lst:
      self.content[entry].get()

    self.master.send_param()
    self.master.redisplay()
    self.root.destroy()

  def onSend(self):

    lst = self.content.keys()
    for entry in lst:
      self.content[entry].get()

    self.master.send_param()
    self.master.redisplay()


  def onCancel(self):
    self.root.destroy()



###########################
class entryCl:
###########################

  def __init__(self,master,n,param,params):

    self.param = param
    self.params= params

    name = "%s(%s)"%(param[1],param[2])

    value = write_ascii_value(param[3],param[2],param[0])

    
    tk.Label(master, text=name).grid(column=0,row=n,sticky=tk.N+tk.S+tk.E)
    self.entry = tk.Entry(master, width=20)
    self.entry.insert(tk.INSERT,value)
    self.entry.grid(column=1,row=n,sticky=tk.E+tk.N+tk.S+tk.W)

  def get(self):
  
    # asign value
    var = read_ascii_value(self.entry.get(),self.param[2],self.param[0])
    self.params.set(self.param[0],var) # here, as self.params is not a copy, the values are changed in the main program

