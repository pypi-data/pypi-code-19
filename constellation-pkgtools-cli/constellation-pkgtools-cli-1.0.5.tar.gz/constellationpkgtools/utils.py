import re, os, urllib2, imp, zipfile, hashlib
import xml.etree.cElementTree as ET

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

def getAccessKey(login, password):
	return hashlib.sha1(login + password).hexdigest()