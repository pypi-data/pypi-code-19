#!/usr/bin/python
"""Constellation Package Tools CLI.

Usage:
  ctln create <name> [--template=<id>]
  ctln update
  ctln run [--server=<name>]
  ctln publish --output=<directory> [--filename=<name>]
  ctln publish <server_name> [--filename=<name>]
  ctln pyscript list
  ctln pyscript add <filepath> [--filename=<name>]
  ctln pyscript new <filename> [<item_template_name>]
  ctln pyscript remove <filename>
  ctln pyscript rename <old_name> <new_name>
  ctln server list
  ctln server (add | set) <name> --url=<url> --accesskey=<key>
  ctln server (add | set) <name> --url=<url> --username=<user>
  ctln server remove <name>
  ctln server test <name>
  ctln template list
  ctln (-h | --help)
  ctln (-v | --version)

Options:
  -h --help             Show this screen.
  -v --version          Show version.
  --output=<directory>  The output directory.
  --filename=<name>     The file name.
  --template=<id>       The template id [default: python-base].
  --url=<url>           The Constellation Server URI.
  --accesskey=<key>     The Constellation Access Key.
  --username=<user>     The Constellation Username.
  --server=<name>       The Constellation Server Name.

"""

from docopt import docopt
import urllib2, requests, json
import xml.etree.cElementTree as ET
import ConfigParser, re, getpass, hashlib, fnmatch
import tarfile, zipfile, tempfile, shutil
import datetime, os, sys, imp, subprocess

VERSION = "1.0.17236"
BASE_URI = "http://skynet-server.ajsinfo.loc/PythonCLI/"

templates = None

def compareVersion(version1, version2):
	def normalize(v):
		return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
	return cmp(normalize(version1), normalize(version2))

def normalizePath(path):
	if not path.endswith(os.sep):
		path = path + os.sep
	return path

def downloadfile(url, fileOpenMode = 'wb'):
	try:
		print "Downloading " + url
		remotefile = urllib2.urlopen(url)
		try:
			filename=remotefile.info()['Content-Disposition']
		except KeyError:
			filename=os.path.basename(urllib2.urlparse.urlsplit(url).path)
		with open(filename, fileOpenMode) as local_file:
			local_file.write(remotefile.read())
		return filename
	except urllib2.HTTPError, e:
		print "Unable to download the file '%s'. HTTP Error: %s" % (url, e.code)
	except urllib2.URLError, e:
		print "Unable to download the file '%s'. URL Error: %s" % (url, e.reason)
	return None

def replaceInFile(file, oldValue, newValue):
	with open(file, 'r+') as f:
		content = f.read()
		f.seek(0)
		f.truncate()
		f.write(content.replace(oldValue, newValue))

def parse_xmlns(file):
	events = "start", "start-ns"
	root = None
	ns_map = []
	for event, elem in ET.iterparse(file, events):
		if event == "start-ns":
			ns_map.append(elem)
		elif event == "start":
			if root is None:
				root = elem
			for prefix, uri in ns_map:
				elem.set("xmlns:" + prefix, uri)
			ns_map = []
	return ET.ElementTree(root)

def fixup_element_prefixes(elem, uri_map, memo):
	def fixup(name):
		try:
			return memo[name]
		except KeyError:
			if name[0] != "{":
				return
			uri, tag = name[1:].split("}")
			if uri in uri_map:
				new_name = tag
				if uri_map[uri] and uri_map[uri] <> '':
					new_name = uri_map[uri] + ":" + tag
				memo[name] = new_name
				return new_name
	# fix element name
	name = fixup(elem.tag)
	if name:
		elem.tag = name
	# fix attribute names
	for key, value in elem.items():
		name = fixup(key)
		if name:
			elem.set(name, value)
			del elem.attrib[key]

def fixup_xmlns(elem, maps=None):
	if maps is None:
		maps = [{}]
	# check for local overrides
	xmlns = {}
	for key, value in elem.items():
		if key[:6] == "xmlns:":
			xmlns[value] = key[6:]
	if xmlns:
		uri_map = maps[-1].copy()
		uri_map.update(xmlns)
	else:
		uri_map = maps[-1]
	# fixup this element
	fixup_element_prefixes(elem, uri_map, {})
	# process elements
	maps.append(uri_map)
	for elem in elem:
		fixup_xmlns(elem, maps)
	maps.pop()

def write_xmlns(elem, file):
	if not ET.iselement(elem):
		elem = elem.getroot()
	fixup_xmlns(elem)

def saveXml(root, configFile):
	write_xmlns(root, configFile)
	root.write(configFile)
	replaceInFile(configFile, 'xmlns:="', 'xmlns="')

def which(program):
	import os
	def is_exe(fpath):
		return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
	fpath, fname = os.path.split(program)
	if fpath:
		if is_exe(program):
			return program
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			path = path.strip('"')
			exe_file = os.path.join(path, program)
			if is_exe(exe_file):
				return exe_file
	return None

def importModule(uri):
	mod = None
	path, fname = os.path.split(uri)
	mname, ext = os.path.splitext(fname)
	if os.path.exists(os.path.join(path,mname)+'.pyc'):
		try:
			return imp.load_compiled(mname, uri)
		except:
			pass
	if os.path.exists(os.path.join(path,mname)+'.py'):
		try:
			return imp.load_source(mname, uri)
		except:
			pass
	return mod

def createZipPackage(path, ziph):
	for root, dirs, files in os.walk(path):
		for file in files:
			if not file.startswith(".template"):
				ziph.write(os.path.relpath(os.path.join(root, file), path))

def getAccessKey(login, password):
	return hashlib.sha1(login + password).hexdigest()

def loadCurrentTemplateModule():
	filename = os.path.join(os.path.realpath(os.getcwd()), ".template", "module.py")
	return importModule(filename) if os.path.exists(filename) else None

def loadCurrentTemplateDefinition():
	filename = os.path.join(os.path.realpath(os.getcwd()), ".template", "template.def")
	if os.path.exists(filename):
		config = ConfigParser.ConfigParser()
		config.read(filename)
		return config
	else:
		return None

def fetchTemplates():
	global templates
	if not templates:
		print "Fetching templates repository ..."
		templates = json.loads(urllib2.urlopen(BASE_URI + "Templates.json").read())

def getTemplateUri(templateId):
	fetchTemplates()
	cmpnt = filter(lambda x: x['id'].lower() == templateId.lower(), templates)
	if any(cmpnt):    
		return (BASE_URI + cmpnt[0]['filename']), cmpnt[0]['version']
	else:
		return None

def installTemplate(template, installDirectory):
	print "Installing template '%s' ..." % template
	# Getting template uri
	(uri, version) = getTemplateUri(template)
	if uri:
		# Downloading
		filename = downloadfile(uri)
		if filename:
			# Extracting
			path = os.path.realpath(normalizePath(installDirectory))
			print "Extracting %s to %s" % (filename, path)
			tar = tarfile.open(filename, 'r')
			for item in tar:
				tar.extract(item, path)
			# Remove the templace archive
			os.remove(filename)
			# Template install
			templateMod = loadCurrentTemplateModule()
			if templateMod:
				print "Installing template ..."
				templateMod.Install(path)
		else:
			print "Fatal error : Unable to download the template %s" % template
			exit()
	else:
		print "Fatal error : Unable to find the template uri !"
		exit()

def updatePackage():
	definition = loadCurrentTemplateDefinition()
	if not definition:
		print "Error : template definition not found"
	elif definition.has_option("Template", "cliversion") and compareVersion(definition.get("Template", "cliversion"), VERSION) > 0:
		print "Your Constellation Package Tools CLI version is obsolete to update this package. Please upgrade this tools before!"
	else:
		template = definition.get("Template", "id")
		currentVersion = definition.get("Template", "version")
		# Getting template uri
		(uri, version) = getTemplateUri(template)
		if(compareVersion(version, currentVersion) > 0):
			print "Update template '%s' version %s ..." % (template, version)
			# Download
			filename = downloadfile(uri)
			if filename:
				update_exclude = definition.get("Template", "update-exclude").replace("\\", os.sep).split(",")
				update_include = definition.get("Template", "update-include").replace("\\", os.sep).split(",")
				update_remove = definition.get("Template", "update-remove").replace("\\", os.sep).split(",")
				# Extracting
				path = os.path.realpath(os.getcwd())
				tar = tarfile.open(filename, 'r')
				for item in tar:
					if not any(fnmatch.fnmatch(item.name, pattern) for pattern in update_exclude) or any(fnmatch.fnmatch(item.name, pattern) for pattern in update_include):
						print "Extracting %s" % item.name
						tar.extract(item, path)
					else:
						print "Skipping %s" % item.name
				# Remove older file
				for root, dirs, files in os.walk(path):
					for file in files:
						filepath = os.path.join(root, file)
						if any(fnmatch.fnmatch(os.path.relpath(filepath, path), pattern) for pattern in update_remove):
							print "Removing %s" % filepath
							os.remove(filepath)
				# Remove the template archive
				os.remove(filename)
				# Template upgrade
				templateMod = loadCurrentTemplateModule()
				if templateMod:
					print "Upgrading template ..."
					templateMod.Upgrade(path, currentVersion, version)
				# Done
				print "Update done!"
			else:
				print "Fatal error : Unable to download the template %s" % template
				exit()
		else:
			print "No update available !"

def isPackageDirectory():
	return os.path.exists(os.path.join(os.path.realpath(os.getcwd()), "PackageInfo.xml"))

def getCurrentPackageManifest():
	manifest =  os.path.join(os.path.realpath(os.getcwd()), "PackageInfo.xml")
	ET.register_namespace('', "http://schemas.myconstellation.io/Constellation/1.8/PackageManifest")
	return parse_xmlns(manifest).getroot()

def getServersConfigFilepath():
	return os.path.join(os.path.expanduser("~"), ".ctlnservers")

def getServersConfig():
	config = ConfigParser.ConfigParser()
	config.read(getServersConfigFilepath())
	return config

def testServerConnection(serverName):
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

def main():
	arguments = docopt(__doc__, version='Constellation Package Tools CLI %s' % VERSION)
	if arguments["create"]:
		path = os.path.join(os.path.realpath(os.getcwd()), arguments["<name>"])
		if isPackageDirectory():
			print "Error: Current working directory is a Constellation-based project."
		elif os.path.exists(path):
			print "Error : the directory already exist"
		else:
			installTemplate(arguments['--template'], path)
			manifestFile = os.path.join(path, "PackageInfo.xml")
			replaceInFile(manifestFile, "##MyPackage##", arguments["<name>"])
			replaceInFile(manifestFile, "##Author##", "")
			replaceInFile(manifestFile, "##URL##", "")
			replaceInFile(manifestFile, "##Year##", str(datetime.datetime.now().year))
			print "Package created"
	elif arguments["update"]:
		if not isPackageDirectory():
			print "Error: Current working directory is not a Constellation-based project."
		else:
			updatePackage()
	elif arguments["run"]:
		if not isPackageDirectory():
			print "Error: Current working directory is not a Constellation-based project."
		elif arguments["--server"] and not getServersConfig().has_section(arguments["--server"]):
			print "Unknown server name" 
		else:
			manifestAttributes = getCurrentPackageManifest().attrib
			commandLineArgs = [ os.path.realpath(manifestAttributes["ExecutableFilename"] if "ExecutableFilename" in manifestAttributes else manifestAttributes["Name"] + ".exe") ]
			if arguments["--server"]:
				serverConfig = getServersConfig()
				commandLineArgs.extend([ serverConfig.get(arguments["--server"], "ServerUri"), "Developer", manifestAttributes["Name"], serverConfig.get(arguments["--server"], "AccessKey") ])
			monoPath = which("mono")
			if monoPath <> None:
				commandLineArgs.insert(0, monoPath)
			print "Starting package ..."
			try:
				subprocess.call(commandLineArgs)
			except KeyboardInterrupt:
				print "Package exited!"
			except BaseException, e:
				print "Error: ", e
	elif arguments["publish"]:
		if not isPackageDirectory():
			print "Error: Current working directory is not a Constellation-based project."
		elif arguments["<server_name>"] and not getServersConfig().has_section(arguments["<server_name>"]):
			print "Unknown server name"
		else:
			filename = (getCurrentPackageManifest().attrib["Name"] + ".zip") if not arguments["--filename"] else arguments["--filename"]
			outputDir = tempfile.gettempdir() if not arguments["--output"] else arguments["--output"]
			filepath = os.path.join(outputDir, filename)
			print "Creating the Constellation package ..."
			zipf = zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED)
			createZipPackage(os.path.realpath(os.getcwd()), zipf)
			zipf.close()
			if arguments["--output"]:
				print "The package '%s' has been published to '%s'" % (filename, filepath)
			else:
				config = getServersConfig()
				serverUri = config.get(arguments["<server_name>"], "ServerUri")
				print "Uploading Constellation Package ..."
				postUri = serverUri + '/rest/management/UploadPackage?SentinelName=Management&PackageName=ConstellationPackageToolsCLI&AccessKey=' + config.get(arguments["<server_name>"], "AccessKey")   
				serverResponse = requests.post(postUri, files={'file': open(filepath, 'rb')})
				os.remove(filepath)
				if serverResponse.status_code <> 200:
					print "Unable to publish the package. Server response :", serverResponse.text
				else:
					print "The package '%s' has been published to '%s'" % (filename, serverUri)
	elif arguments["pyscript"]:
		if not isPackageDirectory():
			print "Error: Current working directory is not a Constellation-based project."
			exit()
		configFile =  os.path.join(os.path.realpath(os.getcwd()), "PythonPackageHost.exe.config")
		ET.register_namespace('', "urn:Constellation.PythonProxy")
		ET.register_namespace('', "urn:schemas-microsoft-com:asm.v1")
		root =  parse_xmlns(config)
		namespace = "{urn:Constellation.PythonProxy}"
		if arguments["list"]:
			for child in root.findall("{0}pythonProxy/{0}scripts/{0}script".format(namespace)):
				fullPath = os.path.realpath(child.attrib['filename'].replace("\\", os.sep))
				print " * %s (%s)" % (os.path.basename(fullPath), fullPath)
		elif arguments["add"] or arguments["new"]:
			definition = loadCurrentTemplateDefinition()
			if not definition:
				print "Error : template definition not found"
			else:
				packagePath = os.path.realpath(os.getcwd())
				sourceFile = os.path.join(packagePath, ".template", (arguments["<item_template_name>"] if arguments["<item_template_name>"] else "base") + ".py") if arguments["new"] else arguments["<filepath>"]
				if not os.path.exists(sourceFile):
					print ("Item template" if arguments["new"] else "File") + " not found!"
				else:
					filename = arguments["<filename>"] if arguments["new"] else os.path.basename(sourceFile)
					if arguments["add"] and arguments["--filename"]:
						filename = arguments["--filename"]
					if not filename.endswith(".py"):
						filename = filename + ".py"
					# Check & Copy
					destFile = os.path.join(packagePath, "Scripts", filename)
					if os.path.exists(destFile):
						print "The file '%s' already exist" % destFile
					else:
						shutil.copy(sourceFile, destFile)
						# Add to config
						scriptsElement = root.find("{0}pythonProxy/{0}scripts".format(namespace))
						if scriptsElement <> None:
							scriptsElement.append(ET.Element('script', {'filename': "Scripts\\" + filename}))
							saveXml(root, configFile)
						else:
							print "Error : Invalid XML config file (pythonProxy section not found)"
						# Done
						print "Scripts '%s' added" % filename
		elif arguments["remove"]:
			filename = arguments["<filename>"]
			if not filename.endswith(".py"):
				filename = filename + ".py"
			element = root.find("{0}pythonProxy/{0}scripts/{0}script[@filename='Scripts\\{1}']".format(namespace, filename))
			if element <> None:
				scriptsElement = root.find("{0}pythonProxy/{0}scripts".format(namespace))
				scriptsElement.remove(element)
				print "Updating package configuration"
				saveXml(root, configFile)
			else:
				print "File not found in the package configuration"
			filePath = os.path.join(os.path.realpath(os.getcwd()), "Scripts", filename)
			if os.path.exists(filePath):
				print "Removing %s" % filePath
				os.remove(filePath)
		elif arguments["rename"]:
			oldFilename = arguments["<old_name>"]
			newFilename = arguments["<new_name>"]
			if not oldFilename.endswith(".py"):
				oldFilename = oldFilename + ".py"
			if not newFilename.endswith(".py"):
				newFilename = newFilename + ".py"
			oldFilePath = os.path.join(os.path.realpath(os.getcwd()), "Scripts", oldFilename)
			newFilePath = os.path.join(os.path.realpath(os.getcwd()), "Scripts", newFilename)
			if not os.path.exists(oldFilePath):
				print "File %s not found!" % oldFilename
			elif os.path.exists(newFilePath):
				print "File %s already exist" % newFilename
			else:
				print "Renaming %s to %s" % (oldFilePath, newFilePath)
				shutil.move(oldFilePath, newFilePath)
				element = root.find("{0}pythonProxy/{0}scripts/{0}script[@filename='Scripts\\{1}']".format(namespace, oldFilename))
				if element <> None:
					element.set("filename", "Scripts\\" + newFilename)
					print "Updating package configuration"
					saveXml(root, configFile)
				else:
					print "File not found in the package configuration"
	elif arguments["server"]:
		config = getServersConfig()
		if arguments["add"] or arguments["set"]:
			accessKey = getAccessKey(arguments["--username"], getpass.getpass('Password:')) if arguments["--username"] else arguments["--accesskey"]
			if not config.has_section(arguments["<name>"]):
				config.add_section(arguments["<name>"])
			config.set(arguments["<name>"], 'ServerUri', arguments["--url"])
			config.set(arguments["<name>"], 'AccessKey', accessKey)
			with open(getServersConfigFilepath(), 'w') as configfile:
				config.write(configfile)
			print "Server updated" if arguments["set"] else "Server added"
			testServerConnection(arguments["<name>"])
		elif arguments["remove"] or arguments["test"]:
			if config.has_section(arguments["<name>"]):
				if arguments["remove"]:
					config.remove_section(arguments["<name>"])
					with open(getServersConfigFilepath(), 'w') as configfile:
						config.write(configfile)
					print "Done"
				elif arguments["test"]:
					testServerConnection(arguments["<name>"])
			else:
				print "Unknown server name"
		elif arguments["list"]:
			for section in config.sections():
				print "* %s on %s (AccessKey=%s)" % (section, config.get(section, "ServerUri"), config.get(section, "AccessKey"))
			if len(config.sections()) == 0:
				print "Server list empty!"
	elif arguments["template"] and arguments["list"]:
		fetchTemplates()
		for value in templates:
			print " * %s (id:'%s' version:%s)" % (value["name"], value["id"], value["version"])

if __name__ == '__main__':
	main()