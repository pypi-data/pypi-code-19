import os, ConfigParser
import urllib2

def getServersConfigFilepath():
	return os.path.join(os.path.expanduser("~"), ".ctlnservers")

def getServersConfig():
	config = ConfigParser.ConfigParser()
	config.read(getServersConfigFilepath())
	return config

def saveServersConfig(config):
	with open(getServersConfigFilepath(), 'w') as configfile:
		config.write(configfile)

def testServerConnection(serverName):
	config = getServersConfig()
	serverUri = config.get(serverName, "ServerUri")
	checkAccessReq = None
	try:
		print "Connecting to the Management API on %s ..." % serverUri
		checkAccessReq = urllib2.urlopen(serverUri + '/rest/management/CheckAccess?SentinelName=Management&PackageName=ConstellationPackageToolsCLI&AccessKey=' + config.get(serverName, "AccessKey"))
	except urllib2.HTTPError, e:
		print "HTTP Error:", e.code
	except urllib2.URLError, e:
		print "URL Error:", e.reason
	except BaseException, e:
		print "Error :", e
	if checkAccessReq and checkAccessReq.getcode() == 200:
		print "Server connection OK"
		return True
	else:
		print "Unable to connect to this Constellation Server"
		return False