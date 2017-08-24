''' 
 @package   pNbody
 @file      talkgdisp.py
 @brief     init file
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''

import os,sys
import socket
import string


###########################

class TalkServer:

###########################

  '''
  talk server class
  '''


  def __init__(self,address=None,module=None,cl=None):

    self.HOST = address['HOST']
    self.PORT = address['PORT'] 
    self.module = module   
    self.cl	= cl
    
    
    
  ###########################  
  def isalive(self):  	  
  ###########################
  
    # init the socket
  	  
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    PORTS = range(40000,40016)
    
    
    for PORT in PORTS:
      sock.connect_ex((self.HOST, PORT))       
      try:
        sock.send("isalive")	  
        rawanswer = sock.recv(128)  	       
        sock.close()  
        if rawanswer == 'isalive%&yes':
          self.PORT = PORT
	  #print "cdteld is running on port",PORT
          return 'yes'
      except:
        pass  
	
    print "socket error : verify that a server is running on host %s"%(self.HOST)	
    sys.exit()    
    

  ###########################  
  def talk(self,request,param):  	  
  ###########################	  

    # init the socket
  	  
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect_ex((self.HOST, self.PORT))
    
    ######################
    # send the command
    ######################
    
    while 1:
	
      try:
        sock.send(request+"&"+param)  
	break
      except (socket.error): 
        sock.close()
        self.isalive()
    
    ######################
    # recieve the answer
    ######################    
    
    try:  
      rawanswer = sock.recv(128)		  
      sock.close()
    except (socket.error):  
      sock.close()
      print "socket error : unable to recieve the answer"
      rawanser = -1
      
    ##################################
    # extract answer and check validiy
    ##################################      

    pos = string.find(rawanswer, '%&')
    
    # check 
    request_answ = rawanswer[:pos]
    print request_answ
    if request_answ != request+"&"+param:
      print "error :",request_answ
      return '-1'
    else:
      return(rawanswer[pos+2:])
   
