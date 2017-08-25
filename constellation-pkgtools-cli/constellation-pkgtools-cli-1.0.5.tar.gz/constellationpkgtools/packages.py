import os, utils, ConfigParser, fnmatch
import json, urllib2, tarfile, zipfile
import xml.etree.cElementTree as ET

BASE_URI = "https://nuget.myconstellation.io/pkgtools-cli/"
templates = None

def loadCurrentTemplateModule():
	filename = os.path.join(os.path.realpath(os.getcwd()), ".template", "module.py")
	return utils.importModule(filename) if os.path.exists(filename) else None

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

def getTemplateUri(templateId, type = None):
	fetchTemplates()
	cmpnt = filter(lambda x: (x['type'].lower() == type.lower() if type else true) and ((x['id'].lower() == templateId.lower()) if templateId else ('default' in x and x['default'].lower() == 'true')), templates)
	if any(cmpnt):    
		return (BASE_URI + cmpnt[0]['filename']), cmpnt[0]['version']
	else:
		return (None, None)

def installItemFromTemplate(installDirectory, filename, template):
	print "Getting item template '%s' ..." % (template if template else 'default')
	# Getting template uri
	(uri, version) = getTemplateUri(template, 'item')
	if uri:
		# Downloading
		templateFile = utils.downloadfile(uri)
		if templateFile:
			# Extracting
			path = os.path.realpath(utils.normalizePath(installDirectory))
			print "Extracting %s to %s" % (templateFile, path)
			tar = tarfile.open(templateFile, 'r')
			for item in tar:
				tar.extract(item, path)
				print os.path.join(path, item.name), os.path.join(path, filename)
				os.rename(os.path.join(path, item.name), os.path.join(path, filename))
			tar.close()
			# Remove the templace archive
			os.remove(templateFile)
		else:
			print "Fatal error : Unable to download the item template %s" % template
			exit()
	else:
		print "Fatal error : Unable to find the item template '%s' !" % template
		exit()

def createPackageFromTemplate(installDirectory, template):
	print "Installing template '%s' ..." % (template if template else 'default')
	# Getting template uri
	(uri, version) = getTemplateUri(template, 'project')
	if uri:
		# Downloading
		templateFile = utils.downloadfile(uri)
		if templateFile:
			# Extracting
			path = os.path.realpath(utils.normalizePath(installDirectory))
			print "Extracting %s to %s" % (templateFile, path)
			tar = tarfile.open(templateFile, 'r')
			for item in tar:
				tar.extract(item, path)
			tar.close()
			# Remove the templace archive
			os.remove(templateFile)
			# Template install
			templateMod = loadCurrentTemplateModule()
			if templateMod:
				print "Installing template ..."
				templateMod.Install(path)
		else:
			print "Fatal error : Unable to download the project template %s" % template
			exit()
	else:
		print "Fatal error : Unable to find the project template '%s' !" % template
		exit()

def updatePackageFromTemplate():
	definition = loadCurrentTemplateDefinition()
	if not definition:
		print "Error : template definition not found"
	else:
		template = definition.get("Template", "id")
		currentVersion = definition.get("Template", "version")
		# Getting template uri
		(uri, version) = getTemplateUri(template, 'project')
		if(utils.compareVersion(version, currentVersion) > 0):
			print "Update template '%s' version %s ..." % (template, version)
			# Download
			filename = utils.downloadfile(uri)
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
				print "Fatal error : Unable to download the project template %s" % template
				exit()
		else:
			print "No update available !"

def isPackageDirectory():
	return os.path.exists(os.path.join(os.path.realpath(os.getcwd()), "PackageInfo.xml"))

def getCurrentPackageManifest():
	manifest =  os.path.join(os.path.realpath(os.getcwd()), "PackageInfo.xml")
	ET.register_namespace('', "http://schemas.myconstellation.io/Constellation/1.8/PackageManifest")
	return utils.parse_xmlns(manifest).getroot()

def createZipPackage(path, filename):
	zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
	for root, dirs, files in os.walk(path):
		for file in files:
			if not file.startswith(".template"):
				zipf.write(os.path.relpath(os.path.join(root, file), path))
	zipf.close()

