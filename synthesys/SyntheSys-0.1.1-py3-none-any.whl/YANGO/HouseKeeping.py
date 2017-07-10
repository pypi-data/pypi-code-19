
##################################################################
# Description:
#   Functions used to edit files.
#
##################################################################

import os, sys, glob, re, ntpath, posixpath, fileinput
from distutils.dir_util import copy_tree, create_tree
import shutil
import urllib.request, urllib.parse, urllib.error
import unicodedata
import logging


#======================================================================	
class BundleObject:
	#--------------------------------------------------------------
	def __init__(self, BundleDir):
		self.BundleDir = BundleDir
	#--------------------------------------------------------------
	def Get(self, FileName):
		FilePath = GetFile(self.BundleDir, FileName)
		if os.path.exists(FilePath):
			return FilePath
		else:   
			logging.error("Bundle cannot find '{0}' file.".format(FileName))
			return None
	#--------------------------------------------------------------
	def Clean(self):
		if(os.path.exists(self.BundleDir)): 
			shutil.rmtree(self.BundleDir) # Clean theme folder.
	#--------------------------------------------------------------
	def __str__(self):
		return "(BUNDLE:'"+self.BundleDir+"')"

#======================================================================

#------------------------------------------------------------------------------------------------------
def CheckTypes(*a_args, **a_kwargs):
	"""
	Any number of expected types are received as parameters.
	"""
	def Decorator(Function):
		"""
		Return 'ModifiedFunction'.
		"""
		def ModifiedFunction(*args, **kwargs):
			"""
			Control types received as parameters.
			"""
			# It must be as many parameters received as expected.
			if len(a_args) != len(args):
				raise TypeError("Received arguments: '{0}', expected: '{1}'.".format(len(args), len(a_args)))
			# Browse not named parameters list.
			for i, arg in enumerate(args):
				if a_args[i] is not type(args[i]):
					raise TypeError("Argument '{0}' is of wrong type. Expected '{1}'".format(i, a_args[i]))
			# Browse named parameters list.
			for Key in kwargs:
				if Key not in a_kwargs:
					raise TypeError("Argument '{0}' n'a aucun type precise".format(repr(Key)))
				if a_kwargs[Key] is not type(kwargs[Key]):
					raise TypeError("Argument '{0}' has incorrect type. expected '{1}'".format(repr(Key), a_kwargs[Key]))
			return Function(*args, **kwargs)
		return ModifiedFunction
	return Decorator

#------------------------------------------------------------------------------------------------------
def GetStimColumns(StimFileName):
	"Browse stimFile until an uncommented and number filled row, return the list of these numbers."
	StimList=[]
	if StimFileName is not None:
		with open(StimFileName, 'r') as STIMFILE:
			for line in STIMFILE.readlines():
				logging.debug("Parse line: "+line[:-1])
				ColumnList = RemoveComment(line, "//").split()
				logging.debug(("*"*3)+"ColumnList = "+str(ColumnList))
				if (len(ColumnList) > 0):
					for Nb in ColumnList:
						try: 	
							Number=int(Nb.split('#')[1], int(Nb.split('#')[0]))
						except:
							try:    Number=int(Nb, 10) # Base 10 by default
							except:	Number=None # Not a string representation of a number
						finally:
							logging.debug(("*"*6)+"Number = "+str(Number))
							StimList.append(Number)
					if len(StimList):
						if StimList.count(None): return []
						else: return StimList
	return []

#-----------------------------------------------------------------------------------------------------------
def IsProjectPath(ProjectPath):	
	SubDirList = [os.path.join(ProjectPath, "src"),
	              os.path.join(ProjectPath, "TB"),
	              os.path.join(ProjectPath, "common"),]
	for SubDir in SubDirList:
		if not os.path.exists(SubDir): return False
	return True

#-----------------------------------------------------------------------------------------------------------
def IsLib(FolderPath):
	return False

#-----------------------------------------------------------------------------------------------------------
def IsPkg(FolderPath):
	return False

#-----------------------------------------------------------------------------------------------------------
def IsIP(FolderPath):
	return False

#-----------------------------------------------------------------------------------------------------------
def IsHDLSrc(FilePath):
	if re.match(r".*\.(vhd|v)$", FilePath): return True
	print(("# Specified file ('{0}') has not a 'vhd' or 'v' extension => skipped.".format(os.path.basename(FilePath))))
	return False

#-----------------------------------------------------------------------------------------------------------
def IsVerilog(FilePath):
	if re.match(r".*\.v$", FilePath): return True
	return False

#-----------------------------------------------------------------------------------------------------------
def IsVHDL(FilePath):
	if re.match(r".*\.vhd$", FilePath): return True
	return False

#-----------------------------------------------------------------------------------------------------------
def get_file_path_from_dnd_dropped_uri(uri):
	# get the path to file
	path = ""
	if uri.startswith('file:\\\\\\'): # windows
		path = uri[8:] # 8 is len('file:///')
	elif uri.startswith('file://'): # nautilus, rox
		path = uri[7:] # 7 is len('file://')
	elif uri.startswith('file:'): # xffm
		path = uri[5:] # 5 is len('file:')

	path = urllib.request.url2pathname(path) # escape special chars
	path = path.strip('\r\n\x00') # remove \r\n and NULL

	return path

#-----------------------------------------------------------------------------------------------------------
def GetAvailableArch(Directory):
	"Browse the architecture file to find all the available architectures of this AVA-Soft installation"
	ArchiList = []
	filepath = os.path.join(Directory, "architectures")
	#========================================
	with open(filepath, "r") as ARCHI_FILE:
		for line in ARCHI_FILE.readlines():
			matched_item = re.match("\s*(?P<archi>[-_\w]+)\s+.*", line)
			if(matched_item):
				ArchiList.append(matched_item.group("archi"))
	#print "$ Debug : ArchiList:", ArchiList, "in folder: ", os.path.basename(Directory) 
	return ArchiList

#-----------------------------------------------------------------------------------------------------------
def get_entity_list(filepath):
	"Return the entity list within the specified VHDL source file"
	entity_list = []
	with open(filepath, "r") as VHDfile:
		for line in VHDfile.readlines():
			matched_item = re.match("\s*entity\s+(?P<entity_name>[-_\w]+)\s+is.*", line)
			if(matched_item):
				entity_list.append(matched_item.group("entity_name"))
	return entity_list

#-----------------------------------------------------------------------------------------------------------
def get_selectedlines(treeview):
	selmodel, selrows = treeview.get_selection().get_selected_rows()
	if(selrows != []):
		return selrows[0]
	else:
		return None
	
#-----------------------------------------------------------------------------------------------------------
def get_text_from_selected(liststore, rowslist):
	if(rowslist != None):
		text_list = []
		for row in rowslist:
			# Get toggled iter, and value at column 0
			iter_ = liststore.get_iter((int(row),)) # Path is the line number
			text  = liststore.get_value(iter_, 0)
			text_list.append(text)
		return text_list
	else:
		return None

#-----------------------------------------------------------------------------------------------------------
def GetFilesFromDir(directory, extension_ptrn = ".*"):
	"Return the list of all the file paths from the specified directory (recursively)"
	files_list = []
	if (directory == ""):
		raise NameError("No directory name specified")

	else:# look for the file name recursively into the top_dir
		for root, dirs, files in os.walk(directory):
			#print "root:", root
			#print "files:", files
			if(len(files) != 0):# if file is found
				for FileName in files:
					if(re.match("^[.\w_-]+.{0}$".format(extension_ptrn), FileName)):
						file_path = os.path.abspath(os.path.join(root, FileName))
						files_list.append(file_path)
		return files_list
	
#-----------------------------------------------------------------------------------------------------------
def get_files_from_srcfile(srcfile_path, extension_ptrn = ".*"):
	"Return the list of all the file paths specified in the source file"
	files_list = []
	with open(srcfile_path, "r+") as srcfile:
		for line in srcfile.readlines():
			if(line.count("//[unselected]") ):
				line = line[line.find("//[unselected]")+14:]
				line = RemoveComment(line, "//")
				selected = False
			else:
				line = RemoveComment(line, "//")
				selected = True
			if( re.match("^[\s()./\w_:-]+{0}$".format(extension_ptrn), line) ):
				if( re.match("[^$\s]+", line) ):
					files_list.append( (os.path.abspath(line), selected) )
					#print os.path.abspath(line)
	return files_list

#-----------------------------------------------------------------------------------------------------------
def GetListFromFile(FilePath, selstatus = False):
	"Return the list of all the signals specified in the source file"
	sig_list = []
	with open(FilePath, "r+") as srcfile:
		for line in srcfile.readlines():
			if(line.count("//[unselected]") ):
				line = line[line.find("//[unselected]")+14:]
				line = RemoveComment(line, "//")
				#print line,"<== Found an unselected signal:"
				selected = False
			else:
				line = RemoveComment(line, "//")
				selected = True
			if( re.match("^[-_\s)(./\w:]+$", line) ):
				if( re.match("[^$\s]+", line)):
					if(selstatus):
						sig_list.append( (line, selected) )
					else:
						sig_list.append(line)
	return sig_list

#-----------------------------------------------------------------------------------------------------------
def RemoveComment(line, CommentSymbol):
	"Remove comments in the line"
	index = line.find(CommentSymbol) # - len(comment_char) -1
	#print "comment at index:", index
	return line[:index]
				
#-----------------------------------------------------------------------------------------------------------
def comment_line(text, filepath):
	"Comment the line where the text occurence is found"
	error = True
	for line in fileinput.input(filepath, inplace=True):
		#sys.stdout is redirected to the file
		if(line.count(text)):
			error = False
			sys.stdout.write("//[unselected]") # Write the comment caracters

		sys.stdout.write(line)# Copy the file line as they appear
	if(error):
		raise NameError("Unable to find the text to comment")
				
#-----------------------------------------------------------------------------------------------------------
def uncomment_line(text, filepath):
	"Uncomment the line where the text occurence is found"
	error = True
	for line in fileinput.input(filepath, inplace=True):
		#sys.stdout is redirected to the file
		if(line.count(text)):
			try: 
				error = False
				line = line.replace("//[unselected]", "", 1)
			except: pass
		sys.stdout.write(line)# Copy the file line as they appear
	if(error):
		raise NameError("Unable to find the text to uncomment")		
#-----------------------------------------------------------------------------------------------------------
def get_tree_dict(config_file_path):
	tree_dict = {}
	saved_path = os.path.abspath("./")
	os.chdir(os.path.dirname(config_file_path))
	config_file = open(os.path.basename(config_file_path), "r")
	for line in config_file.readlines():
		matched_re = re.match("^\s*(?P<name>[-_\w)(]+)\s*=.(?P<path>[./\w_-]+)", line)
		if(matched_re):
			tree_dict[matched_re.group("name")] = os.path.abspath(matched_re.group("path"))
	os.chdir(saved_path)
	return tree_dict

#-----------------------------------------------------------------------------------------------------------
def GetArchList(ProjectPath, TB):
	"Browse the arborescence to find all the available boards in the specified directory"
	BoardList = []
	#========================================
	for folder in os.listdir( os.path.join(ProjectPath, "TB", TB) ):
		matched_re = re.match(r'\.(?P<Arch>[-_\w)(]+)', folder)
		if(matched_re):
			BoardList.append(matched_re.group("Arch"))
	return BoardList

#-----------------------------------------------------------------------------------------------------------
def GetTBList(directory):
	"Browse the arborescence to find all the availabble boards in the specified directory"
	tb_list = []
	#========================================
	for folder in os.listdir( os.path.abspath( os.path.join(directory, "TB") ) ):
		#print "GetTBList / Folder:", folder
		matched_re = re.search(".svn", folder)
		if(matched_re):
			pass
		else:
			tb_list.append(folder)
	#print "$ Debug : tb_list:", tb_list, "in folder: ", os.path.basename(directory) 
	return tb_list

#-----------------------------------------------------------------------------------------------------------
def get_version_list(task, target):
	"Browse the arborescence to find all the versions of the core used with the choosen target according to the simulation or implement choice"
	version_list = []
	#========================================
	if(task == "simulation"):
		directory = os.path.normpath("../../../hdw/pcie/behavioral/hw_{0}".format(target))
	elif(task == "implement"):
		directory = os.path.normpath("../../../hdw/pcie/implement/hw_{0}".format(target))
	else:
		return []
	#========================================
	for folder in os.listdir( directory ):
		version_list.append(folder)
	return version_list


#-----------------------------------------------------------------------------------------------------------
#-------------------------------------- Utilities ----------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
def file_line_replace(FileName, pattern_re_str, replacement_str):
	found = False
	if not os.path.exists(FileName):
		print(("File <{0}> cannot be found".format(FileName)))
	else:
		for line in fileinput.input(FileName, inplace=True):
			re_matched = re.search(pattern_re_str, line)
			if( re_matched != None ):
				line =line.replace(re_matched.group(0), replacement_str)
				found = True
			#sys.stdout is redirected to the file
			sys.stdout.write(line)
	return found

#-----------------------------------------------------------------------------------------------------------
def GetFile(RootDir, FileName):
	"Return the path of a given file name in the specified directory (recursively)"
	if  (FileName == ""):
		raise NameError("no file name specified")
	else:# look for the file name recursively into the RootDir
		for root, dirs, files in os.walk(RootDir):
			#print "root:", root
			#print "files:", files
			if(files.count(FileName) != 0):# if file is found
				FilePath = os.path.abspath(os.path.join(root, FileName))
				return FilePath
		raise NameError("Can't find file: "+FileName+" in "+RootDir) # If the program reach this point, it's an error
		return None

#-----------------------------------------------------------------------------------------------------------
def get_text(FileName):
	"Return the text contained in the specified file"
	src_file = open(FileName, "r")
	text = ""
	for line in src_file.readlines():
		text += line
	return text

#-----------------------------------------------------------------------------------------------------------
def file_pattern_replace(FileName, pattern_re_begin, pattern_re_end, replacement_str):
	found = False
	pattern_re_begin.replace(" ","\s")
	if not os.path.exists(FileName):
		print(("File <{0}> cannot be found".format(FileName)))
	else:
		replace = False
		for line in fileinput.input(FileName, inplace=True):
			if(replace == False):
				re_matched = re.search(pattern_re_begin, line, flags=re.MULTILINE) # Cherche le debut du text a remplacer
				if( re_matched != None ): # s'il a trouve la premiere ligne du texte a remplacer
					begin_matched = re_matched.group(0)
					found = True
					replace = True # indique qu'il procede au remplacement
					sys.stdout.write(replacement_str) # Ecrit le texte de remplacement
			else:
				re_matched = re.search(pattern_re_end, line, flags=re.MULTILINE) # Cherche la fin du text a remplacer
				if( re_matched != None ): # s'il a trouve la premiere ligne du texte a remplacer
					end_matched = re_matched.group(0)
					replace = False # indique qu'il a fini le remplacement
				
			#sys.stdout is redirected to the file
			if(replace == False): # copie le fichier tel qu'il est 
				sys.stdout.write(line)
	return found

#-----------------------------------------------------------------------------------------------------------
def file_text_replace(FileName, OldText, NewText):
	found = False
	text  = ""
	if not os.path.exists(FileName):
		raise NameError("File <{0}> cannot be found".format(FileName))
	else:
		for line in fileinput.input(FileName, inplace=True):
			if( line.count(OldText) ):
				found = True
				text = "\nFound: <" + line
				line = line.replace(OldText, NewText)
				text += ("> replaced by <"+line+">")
			sys.stdout.write(line)
	#print text
	return found
				

#-----------------------------------------------------------------------------------------------------------
def file_add_line(FileName, line_nb, string_to_add):
	if not os.path.exists(FileName):
		print(("File <{0}> cannot be found".format(FileName)))
	else:
		cnt = 0
		for line in fileinput.input(FileName, inplace=True):
			if( cnt == line_nb ): # If the line number match
				sys.stdout.write(string_to_add) # Write the string to add

			#sys.stdout is redirected to the file
			sys.stdout.write(line)# Copy the file line as they appear
			cnt += 1
		print(("\t\tLine(s) added to the file <{0}> at position {1}".format(os.path.basename(FileName), line_nb)))


#-----------------------------------------------------------------------------------------------------------
def get_last_line(regex, file_path):
	"Return the line number in the specified file that matched the regular expression"
	line_nb = None
	cnt = 0
	my_file = open(file_path, "r")
	for line in my_file.readlines():
		cnt += 1
		re_matched = re.search(regex, line)
		if( re_matched != None ):
			line_nb = cnt
	return line_nb

#-----------------------------------------------------------------------------------------------------------
def GetMatchedRe(Regex, FilePath):
	"Return the line that matched the regular expression in the specified file"
	with open(file_path, "r") as MYFILE:
		for line in MYFILE.readlines():
			re_matched = re.search(regex, line)
			if( re_matched != None ):
				return re_matched
	return None

#-----------------------------------------------------------------------------------------------------------
def check_path(path, filename_list):
	for FileName in filename_list:
		if(get_file(path, FileName) == None): return FileName
	return True

#======================================================================
def Normalize(text):
	"""
	Return a normalized format for the input text.
	"""
	return unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore')


