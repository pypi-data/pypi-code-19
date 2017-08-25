#!/usr/bin/python
"""Constellation Package Tools CLI.

Usage:
  ctln create <name> [<project_template_name>]
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
  ctln server check <name>
  ctln server remove <name>
  ctln template list
  ctln (-h | --help)
  ctln (-v | --version)

Options:
  -h --help             Show this screen.
  -v --version          Show version.
  --output=<directory>  The output directory.
  --filename=<name>     The file name.
  --server=<name>       The Constellation Server Name.
  --url=<url>           The Constellation Server URI.
  --accesskey=<key>     The Constellation Access Key.
  --username=<user>     The Constellation Username.

"""

VERSION = "1.0.5"

from docopt import docopt
import xml.etree.cElementTree as ET
import requests, getpass, tempfile, shutil
import datetime, os, subprocess
import utils, packages, serverConfig

def main():
	arguments = docopt(__doc__, version='Constellation Package Tools CLI %s' % VERSION)
	if arguments["create"]:
		path = os.path.join(os.path.realpath(os.getcwd()), arguments["<name>"])
		if packages.isPackageDirectory():
			print "Error: Current working directory is a Constellation-based project."
		elif os.path.exists(path):
			print "Error : the directory already exist"
		else:
			packages.createPackageFromTemplate(path, arguments['<project_template_name>'])
			manifestFile = os.path.join(path, "PackageInfo.xml")
			utils.replaceInFile(manifestFile, "##MyPackage##", arguments["<name>"])
			utils.replaceInFile(manifestFile, "##Author##", "")
			utils.replaceInFile(manifestFile, "##URL##", "")
			utils.replaceInFile(manifestFile, "##Year##", str(datetime.datetime.now().year))
			print "Package created"
	elif arguments["update"]:
		if not packages.isPackageDirectory():
			print "Error: Current working directory is not a Constellation-based project."
		else:
			definition = packages.loadCurrentTemplateDefinition()
			if definition and definition.has_option("Template", "cliversion") and utils.compareVersion(definition.get("Template", "cliversion"), VERSION) > 0:
				print "Your Constellation Package Tools CLI version is obsolete to update this package. Please upgrade this tools before!"
			else:
				packages.updatePackageFromTemplate()
	elif arguments["run"]:
		if not packages.isPackageDirectory():
			print "Error: Current working directory is not a Constellation-based project."
		elif arguments["--server"] and not serverConfig.getServersConfig().has_section(arguments["--server"]):
			print "Unknown server name" 
		else:
			manifestAttributes = packages.getCurrentPackageManifest().attrib
			commandLineArgs = [ os.path.realpath(manifestAttributes["ExecutableFilename"] if "ExecutableFilename" in manifestAttributes else manifestAttributes["Name"] + ".exe") ]
			if arguments["--server"]:
				config = serverConfig.getServersConfig()
				commandLineArgs.extend([ config.get(arguments["--server"], "ServerUri"), "Developer", manifestAttributes["Name"], config.get(arguments["--server"], "AccessKey") ])
			monoPath = utils.which("mono")
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
		if not packages.isPackageDirectory():
			print "Error: Current working directory is not a Constellation-based project."
		elif arguments["<server_name>"] and not serverConfig.getServersConfig().has_section(arguments["<server_name>"]):
			print "Unknown server name"
		else:
			filename = (packages.getCurrentPackageManifest().attrib["Name"] + ".zip") if not arguments["--filename"] else arguments["--filename"]
			outputDir = tempfile.gettempdir() if not arguments["--output"] else arguments["--output"]
			filepath = os.path.join(outputDir, filename)
			print "Creating the Constellation package ..."
			packages.createZipPackage(os.path.realpath(os.getcwd()), filepath)
			if arguments["--output"]:
				print "The package '%s' has been published to '%s'" % (filename, filepath)
			else:
				config = serverConfig.getServersConfig()
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
		if not packages.isPackageDirectory():
			print "Error: Current working directory is not a Constellation-based project."
			exit()
		configFile =  os.path.join(os.path.realpath(os.getcwd()), "PythonPackageHost.exe.config")
		ET.register_namespace('', "urn:Constellation.PythonProxy")
		ET.register_namespace('', "urn:schemas-microsoft-com:asm.v1")
		root =  utils.parse_xmlns(configFile)
		namespace = "{urn:Constellation.PythonProxy}"
		if arguments["list"]:
			for child in root.findall("{0}pythonProxy/{0}scripts/{0}script".format(namespace)):
				fullPath = os.path.realpath(child.attrib['filename'].replace("\\", os.sep))
				print " * %s (%s)" % (os.path.basename(fullPath), fullPath)
		elif arguments["add"] or arguments["new"]:
			definition = packages.loadCurrentTemplateDefinition()
			if not definition:
				print "Error : template definition not found"
			else:
				packagePath = os.path.realpath(os.getcwd())
				filename = arguments["<filename>"] if arguments["new"] else os.path.basename(arguments["<filepath>"])
				if arguments["add"] and arguments["--filename"]:
					filename = arguments["--filename"]
				if not filename.endswith(".py"):
					filename = filename + ".py"
				if arguments["new"]:
					# New item from template
					packages.installItemFromTemplate(os.path.join(packagePath, "Scripts"), filename, arguments["<item_template_name>"])
				else:
					# Add existing item
					sourceFile = arguments["<filepath>"]
					destFile = os.path.join(packagePath, "Scripts", filename)
					if not os.path.exists(sourceFile):
						print "File not found!"
						exit()
					elif os.path.exists(destFile):
						print "The file '%s' already exist" % destFile
						exit()
					else:
						# Copy
						shutil.copy(sourceFile, destFile)
				# Adding filename to config
				scriptsElement = root.find("{0}pythonProxy/{0}scripts".format(namespace))
				element = root.find("{0}pythonProxy/{0}scripts/{0}script[@filename='Scripts\\{1}']".format(namespace, filename))
				if scriptsElement == None:
					print "Error : Invalid XML config file (pythonProxy section not found)"
				elif element == None:
					scriptsElement.append(ET.Element('script', {'filename': "Scripts\\" + filename}))
					utils.saveXml(root, configFile)
				# Done
				print "Script '%s' added" % filename
		elif arguments["remove"]:
			filename = arguments["<filename>"]
			if not filename.endswith(".py"):
				filename = filename + ".py"
			element = root.find("{0}pythonProxy/{0}scripts/{0}script[@filename='Scripts\\{1}']".format(namespace, filename))
			if element <> None:
				scriptsElement = root.find("{0}pythonProxy/{0}scripts".format(namespace))
				scriptsElement.remove(element)
				print "Updating package configuration"
				utils.saveXml(root, configFile)
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
					utils.saveXml(root, configFile)
				else:
					print "File not found in the package configuration"
	elif arguments["server"]:
		config = serverConfig.getServersConfig()
		if arguments["add"] or arguments["set"]:
			accessKey = utils.getAccessKey(arguments["--username"], getpass.getpass('Password:')) if arguments["--username"] else arguments["--accesskey"]
			if not config.has_section(arguments["<name>"]):
				config.add_section(arguments["<name>"])
			config.set(arguments["<name>"], 'ServerUri', arguments["--url"])
			config.set(arguments["<name>"], 'AccessKey', accessKey)
			serverConfig.saveServersConfig(config)
			print "Server updated" if arguments["set"] else "Server added"
			serverConfig.testServerConnection(arguments["<name>"])
		elif arguments["remove"] or arguments["check"]:
			if config.has_section(arguments["<name>"]):
				if arguments["remove"]:
					config.remove_section(arguments["<name>"])
					serverConfig.saveServersConfig(config)
					print "Done"
				elif arguments["check"]:
					serverConfig.testServerConnection(arguments["<name>"])
			else:
				print "Unknown server name"
		elif arguments["list"]:
			for section in config.sections():
				print "* %s on %s (AccessKey=%s)" % (section, config.get(section, "ServerUri"), config.get(section, "AccessKey"))
			if len(config.sections()) == 0:
				print "Server list empty!"
	elif arguments["template"] and arguments["list"]:
		packages.fetchTemplates()
		for value in packages.templates:
			print " * [%s] %s (id:'%s' version:%s)" % (value["type"].upper(), value["name"], value["id"], value["version"])

if __name__ == '__main__':
	main()