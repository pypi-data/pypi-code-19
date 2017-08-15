#!/usr/bin/python

''' Created on May 17, 2017

This module represents the low-level command API
for a running MRL instance.
				############					 
				ERROR CODES
		0: Success
		1: Incorrect usage from command line
		2: Unable to connect to MRL instance

  sendCommandQuick() and sendCommand()
		return all codes except 1


@author: AutonomicPerfectionist
'''
import websocket
import logging
import signal
try:
	import thread
except ImportError:
	import _thread #For python3 compatibility
import time
import os
import sys
import threading
import json
import requests

from mrlpy.meventdispatch import MEventDispatch
from mrlpy.mevent import MEvent
from mrlpy.mrlmessage import MrlMessage
from mrlpy import mproxygen


useEnvVariables = True
MRL_URL = "localhost"

'''
Port of MRL; MUST be a string
'''
MRL_PORT = '8888'

eventDispatch = MEventDispatch()
socket = None
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)



def connect(bypassRegisters = False, forceReconnect = False):
	'''
	Connects to MRL instance
	Returns True if successful, False otherwise
	'''
	global socket
	global MRL_URL
	global MRL_PORT
	global useEnvVariables

	if useEnvVariables:
		MRL_URL = os.getenv('MRL_URL', MRL_URL)
		MRL_PORT = os.getenv('MRL_PORT', MRL_PORT)

	if socket != None and forceReconnect:
		close()

	if socket == None or socket.sock == None or forceReconnect:
		if bypassRegisters:
			try:
				socket = websocket.create_connection("ws://" + MRL_URL + ':' + MRL_PORT + '/api/messages')
			except Exception:
				log.error("MRL is not online for URL " + MRL_URL + ":" + MRL_PORT)
				return False

		else:
			socket = websocket.WebSocketApp("ws://" + MRL_URL + ':' + MRL_PORT + '/api/messages',
					   on_message = on_message,
					   on_error = on_error,
					   on_close = on_close)
			socket.on_open = on_open
			wst = threading.Thread(target=socket.run_forever)
			wst.daemon=True
			wst.start()
			conn_timeout = 5
			if socket == None or socket.sock == None:
				return False
			try:
				while not socket.sock.connected and conn_timeout:
					time.sleep(1)
					conn_timeout -= 1
			except Exception:
				return False
	return True


def sendCommand(name, method, dat):
	'''
	Sends a command to MRL
	
	Initializes socket so that the connection is held;
	Equivalent to sendCommandQuick() if socket has  
	already been initialized   
	'''

	global MRL_URL
	global MRL_PORT
	global socket
	#if socket == None:
	#	socket = websocket.WebSocketApp("ws://" + MRL_URL + ':' + MRL_PORT + '/api/messages',
	#					  on_message = on_message,
	#					  on_error = on_error,
	#					  on_close = on_close)
	#	socket.on_open = on_open
	#	wst = threading.Thread(target=socket.run_forever)
	#	wst.daemon=True
	#	wst.start()
	#	conn_timeout = 5
	#	if socket == None or socket.sock == None:
	#		return 2
	#	try:
	#		while not socket.sock.connected and conn_timeout:
	#			sleep(1)
	#			conn_timeout -= 1
	#	except Exception:
	#		return 2
	if connect():
		#return sendCommandQuick(name, method, dat)
		return send(name, method, dat)
	else:
		return 2

   
def sendCommandQuick(name, method, dat):
	'''
	Sends a command to MRL
	
	Sends a command, and if socket is not
	initialized, will create a quick
	connection that bypasses event registers
	'''


	global MRL_URL
	global MRL_PORT
	global socket
	#if socket == None:
	#	try :
	#		socket = websocket.create_connection("ws://" + MRL_URL + ':' + MRL_PORT + '/api/messages')
	#	except Exception:
	#		log.error("MRL is not online for URL " + MRL_URL + ":" + MRL_PORT)
	#		return 2
	if connect(bypassRegisters=True):
		#req = '{"name": ' + name + ', "method": ' + method + ', "data": ' + str(dat) + '}'
		#ret = socket.send(req)
		return send(name, method, dat)
	else:
		return 2

def isSequence(arg):
	'''
	Returns True if arg is a sequence and False if string, dict, or otherwise
	'''
	return (not hasattr(arg, "strip") and
			(not hasattr(arg, "values")) and
			(hasattr(arg, "__getitem__") or
			hasattr(arg, "__iter__")))

def parseRet(ret):
	'''
	Will look at ret (return value from callServiceWithJson)
	and convert it to Python types
	'''
	if isSequence(ret):
		tmpRet = []
		for val in ret:
			tmpRet.append(parseRet(val))
		return tmpRet
	else:
		
		#Not a sequence, so can be string, int, json, dict, etc.
		if isinstance(ret, basestring):
			return ret
		else:
			try:
				if 'serviceType' in ret:
					return mproxygen.genProxy(ret)
				else:
					return ret
			except TypeError:
				#ret is not string or dictionary
				return ret


def callServiceWithJson(name, method, dat):
	'''
	Calls a service's method with data as params.
	
	Returns json
	'''

	global MRL_URL
	global MRL_PORT
	#try :
	#TODO: convert dat to json and MAKE SURE strings include quotes
	datFormed = list(map((lambda x: '\'' + x + '\'' if isinstance(x, basestring) else x), dat))
	params = json.dumps(datFormed)
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
	r = requests.post("http://" + MRL_URL + ':' + MRL_PORT + "/api/service/" + name + '/' + method, data=params, headers=headers)
	#   print "MRL is not online for url " + MRL_URL + ":" + MRL_PORT
	#	return 2
	try:
		return r.json()
	except Exception:
		return r.text
	
def callService(name, method, dat):
	'''
	Calls a service's methods with data as params.
	
	Returns what the method returns, and creates a proxy service if service returned.
	'''


	retFromMRL = callServiceWithJson(name, method, dat)
	#if isinstance(retFromMRL, basestring):
	#	return retFromMRL
	#else:
	#	try:
	#		if 'serviceType' in retFromMRL:
	#			return mproxygen.genProxy(retFromMRL)
	#		else:
	#			return retFromMRL
	#	except TypeError:
	#		#retFromMRL is not string or dictionary
	#		return retFromMRL
	return parseRet(retFromMRL)

def callServiceWithVarArgs(*args):
	'''
	Same as callService() except data doesn't have to be in a list
	
	Returns what callService() returns
	'''

	name = args[0]
	method = args[1]
	dat = list(args)[2:]
	return callService(name, method, dat)


def send(name, method, dat):
	'''
	Send string to MRL (INTERNAL USE ONLY!)
	'''

	global socket
	try:
		req = '{"name": ' + name + ', "method": ' + method + ', "data": ' + str(dat) + '}'
		ret = socket.send(req)
		return ret

	except Exception:
		log.error("MRL is not online for URL " + MRL_URL + ":" + MRL_PORT)
		return 2


def getURL():
	global MRL_URL
	return MRL_URL


def setURL(url):
	'''
	Self-explanatory; Use INSTEAD of directly setting URL
	'''
	global MRL_URL
	global useEnvVariables
	MRL_URL = url
	useEnvVariables = False

def getPort():
	global MRL_PORT
	return MRL_PORT


def setPort(port):
	'''
	Self-explanatory; Use INSTEAD of directly setting port
	'''
	global MRL_PORT
	global useEnvVariables
	MRL_PORT = str(port)
	useEnvVariables = False


###################################
#	START EVENT REGISTERS		#
###################################



def on_error(ws, error):
	'''
	Error event register; called	
	by socket on errors 
	'''
	log.error(error)



def on_close(ws):
	'''
	Called by socket on closing
	'''
	log.info("### Closed socket ###")


def on_open(ws):
	'''
	Called by socket when opening
	'''
	log.info("### Opened socket ###")



def close():
	'''
	Utility function for forcefully closing the connection
	'''

	global socket
	socket.close()


def addEventListener(name, l):
	'''
	Add a listener to topic (name); Normally
	used for registering a service's name to the
	event registers
	'''
	#print "Adding event listener: name=" + name + ", l=" + str(l)
	eventDispatch.add_event_listener(name, l)


def removeEventListener(name, l):
	'''
	Removes listener l from topic name
	'''
	eventDispatch.remove_event_listener(name, l)


def hasEventListener(name, l):
	'''
	Returns true if l is a listener for topic name, false otherwise.
	'''

	return eventDispatch.has_listener(name, l)


def on_message(ws, msg):
	'''
	Primary event register. Everything goes through here
	
	Parses message. If a heartbeat, updates heartbeat register.
	Else, create mrlMessage and dispatch.
	'''

	try:
		msgJson = json.loads(msg)
	except ValueError:
		log.warn("Heartbeat received. WARNING: NOT IMPLEMENTED YET")
		return
	try:
		mrlMessage = MrlMessage(msgJson['name'], msgJson['method'], msgJson['data'])
	except Exception:
		mrlMessage = MrlMessage(msgJson['name'], msgJson['method'], None)

	eventDispatch.dispatch_event(mrlMessage)



################################
#	  END EVENT REGISTERS	 #
################################

def __keyboardExit(signal, frame):
	log.info("KeyboardInterrupt... Shutting down")
	sys.exit(0)


def __del__(self):
	'''
	Releases all proxy services on delete.
	'''

	for type, serv in eventDispatch._events.iteritems():
		self.sendCommand("runtime", "release", [serv.name])

#Statements to run during import

#Silences KeyboardInterrupt stacktrace and logs the interrupt, then exits
signal.signal(signal.SIGINT, __keyboardExit)

if __name__ == "__main__":
	MRL_URL = os.getenv('MRL_URL', 'localhost')
	MRL_PORT = os.getenv('MRL_PORT', '8888')
	logging.basicConfig()
	if len(sys.argv) < 3 :
		print("Usage: mcommand <name> <method> <dat>")
		exit(1)
	#websocket.enableTrace(True)
	ret = sendCommandQuick(sys.argv[1], sys.argv[2], sys.argv[3:])
	
	if ret == 2:
		print("Connection failed.")
		exit(2)		
	print("MRL command sent successfully.")
	close()
	exit(0)

