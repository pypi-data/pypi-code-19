import sys
import time
import atexit
import signal
import logging
from mrlpy.exceptions import HandshakeTimeout
from mrlpy import mcommand
from mrlpy import mutils

"""Represents the base service class"""


class MService (object):
	name = ""	
	handshakeSuccessful = False
	handshakeTimeout = 1
	handshakeSleepPeriod = 0.25
	createProxyOnFailedHandshake = True
	__log = logging.getLogger(__name__)
	proxyClass = "PythonProxy"


	def __init__(self, name=""):
		'''
		Registers service with mcommand event registers and MRL service registry
		'''

		if name == "":
			try:
				#Get name from args
				self.name = sys.argv[1]
			except IndexError:
				#No first argument
				#Need to auto-generate name
				self.name = mutils.genID()
		else:
			self.name = name
		self.connectWithProxy(True)
		atexit.register(self.release) #Will release service when Python exits
		signal.pause()
	#	while True:
	#		time.sleep(10)

	def setProxyClass(self, proxy):
		self.proxyClass = proxy

	def connectWithProxy(self, tryagain=False):
		'''
		Utility method used for getting initialization info from proxy and running handshake
		'''
		#Can do this since it won't do anything if proxy already active
		mcommand.sendCommand("runtime", "createAndStart", [self.name, self.proxyClass])
		#Useful for determining whether the proxy service has been created yet
		mrlRet = mcommand.callServiceWithJson(self.name, "handshake", [])
		self.__log.debug("mrlRet = " + str(mrlRet))
		#If we get to here, MRL is running because mcommand did not throw an exception
		#TODO: Use mrlRet to determine if we need to create a proxy service
		#Register this service with MRL's messaging system (Actually, with mcommand's event registers, which forward the event here)
		#Proxy service forwards all messages to mcommand
		mcommand.addEventListener(self.name, self.onEvent)
		#BEGIN HANDSHAKE$
		start = time.time()
		lastTime = 0
		while (not self.handshakeSuccessful) and ((time.time() - start) < self.handshakeTimeout):
			time.sleep(self.handshakeSleepPeriod)
			lastTime = time.time()
			#print str(lastTime - start >= self.handshakeTimeout)
			if lastTime - start >= self.handshakeTimeout:
				if self.createProxyOnFailedHandshake and tryagain:
					self.__log.info("Proxy not active. Creating proxy...")
					mcommand.sendCommand("runtime", "createAndStart", [self.name, "PythonProxy"])
					self.connectWithProxy()
				else:   
					raise HandshakeTimeout("Error attempting to sync with MRL proxy service; Proxy name = " + str(self.name))
		#END HANDSHAKE#
	
	def onEvent(self, e):
		'''
		Handles message invocation and parsing
		of params; WARNING: DO NOT OVERRIDE
		THIS METHOD UNLESS YOU KNOW WHAT YOU
		ARE DOING!!!!!!!
		'''
		#Enables sending a return value back; Other half implemented in mcommand and proxy service
		ret = None
		#Invoke method with data
		try:
			params = ','.join(map(str, e.data))
			self.__log.debug("Invoking: " + e.method + '(' + params + ')')
			ret = eval('self.' + e.method + '(' + params + ')')
		except Exception:
			self.__log.debug("Invoking: " + e.method + '()')
			ret = eval('self.' + e.method + '()')
		self.returnData(ret)

	def returnData(self, dat):
		mcommand.sendCommand(self.name, "returnData", [dat])

	def handshake(self):
		'''
		Second half of handshake.

		Called by proxy during the handshake procedure.
		'''

		self.__log.debug("Handshake successful.")
		self.handshakeSuccessful = True
	def release(self):
		'''
		Utility method for releasing the proxy service;
		Also deletes this service
		'''
		mcommand.sendCommand("runtime", "release", [self.name])
		del self
