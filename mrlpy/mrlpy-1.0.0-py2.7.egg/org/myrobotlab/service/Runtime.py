from mrlpy import mcommand
from Test import Test

compatMode = False
compatObj = None 

def createAndStart(name, type):
	return mcommand.callService("runtime", "createAndStart", [name, type])
	
	
def shutdown():
	mcommand.sendCommand("runtime", "shutdown", [])

def getRuntime():
	return mcommand.callService("runtime", "start", ["runtime", "Runtime"])

def start(name, type):
        return mcommand.callService("runtime", "start", [name, type])

def setCompat(mode):
	global compatMode
	compatMode = mode

def setCompatServiceObject(obj):
	global compatObj
	compatObj = obj
