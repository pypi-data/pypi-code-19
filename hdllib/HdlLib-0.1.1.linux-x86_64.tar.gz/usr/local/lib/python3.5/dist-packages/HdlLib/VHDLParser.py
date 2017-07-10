#!/usr/bin/python


import sys, os, logging, re, math

from HdlLib.Utilities.ErrorHandlers import ParseError
from HdlLib.SysGen.Module import Module
from HdlLib.SysGen.Signal import Signal

#======================================================================
AlstomFunctionsMapping={
	"log2":math.log2,
	"BitWidth":math.log2,
}
#======================================================================
def ParseVHDL(FilePath):
	"""
	Generate a Module instance from a VHDL file.
	"""
	ModuleList = GetSubBlocks(FilePath, 'entity')
	if len(ModuleList)==0:
		logging.warning("No entity found in '{0}'.".format(FilePath))
	return ModuleList


#======================================================================
# Sub-blocks are : entity / process / package 
def GetSubBlocks(FilePath, SubBlockType):
	"""
	Parse VHDL file and return a list of dictonaries for SubBlock elements .
	"""
	if not (SubBlockType in ['entity', 'process', 'package', ]):
		raise HdlLibError("SubBlockType must be either entity, process or package.")
		
	ModuleList=[]
	with open(FilePath, "r") as VHDLFile:
		#--------------------------------------------------------
		# Find sub-block keyword
		WordGenerator=GetWords(VHDLFile, Start=0, End=None)
		Word=None
		while 1:
			while Word!=SubBlockType:
				try: 
					Word, WordOri, LineNb=next(WordGenerator)
					logging.debug("[Seeking '{2}'] Analyze '{0}', Line {1}.".format(Word, LineNb, SubBlockType))
				except StopIteration:
					return ModuleList
			#--------------------------------------------------------
			# If the SubBlockType keyword is found, get the block name
			try: 
				Word, SubBlockName, LineNb=next(WordGenerator)
			except StopIteration:
				raise ParseError("VHDL Parse error : {0} sub-block not properly specified. Cannot find sub-block name. The {0} block should start with '{0} <Name> is'.".format(SubBlockType))
			
			CheckName(SubBlockName, LineNb=LineNb)
			try: 
				IsWord, WordOri, LineNb=next(WordGenerator)
				if IsWord!='is':
					raise ParseError("VHDL Parse error : {0} sub-block not properly specified. Missing the 'is' keyword after {0} name. The {0} block should start with '{0} <Name> is'.".format(SubBlockType))
			except StopIteration:
				raise ParseError("VHDL Parse error : {0} sub-block not properly specified. Cannot find the 'is' keyword after {0} name. The {0} block should start with '{0} <Name> is'.".format(SubBlockType))
			FoundStartLine=LineNb
			logging.info("Found {0} '{1}'.".format(SubBlockType, SubBlockName))
			#--------------------------------------------------------
			# Find the end of the sub-block
			BlockContent=[]
			while not (Word=='end' or Word=='end;') :
				try: 
					Word, WordOri, LineNb=next(WordGenerator)
					logging.debug("[Seeking 'end'] Analyze '{0}', Line {1}.".format(Word, LineNb))
					BlockContent.append( [Word, WordOri, LineNb] )
				except StopIteration:
					raise ParseError("VHDL Parse error : {0} sub-block not properly specified. Cannot find the end of the {0}.".format(SubBlockType))
		
				if Word=='end':
					Word, WordOri, LineNb=next(WordGenerator)
					logging.debug("[Seeking ';'] Analyze '{0}', Line {1}.".format(Word, LineNb))
					if SubBlockType == Word:
						Word, WordOri, LineNb=next(WordGenerator)
						logging.debug("[Seeking ';'] Analyze '{0}', Line {1}.".format(Word, LineNb))
					if WordOri.startswith(SubBlockName):
						if WordOri==SubBlockName: Word, WordOri, LineNb=next(WordGenerator)
						else: Word=WordOri.replace(SubBlockName,"")
						logging.debug("[Seeking ';'] Analyze '{0}', Line {1}.".format(Word, LineNb))
					if not (';' in Word):
						if WordOri==SubBlockName: 
							Word, WordOri, LineNb=next(WordGenerator)
							logging.debug("[Seeking ';'] Analyze '{0}', Line {1}.".format(Word, LineNb))
							if Word.startswith(';'): break
							else: 
								raise ParseError("VHDL Parse error : misses a ';' at the end of {0} {1} definition (line {2}).".format(SubBlockType, SubBlockName, LineNb))
						else:
							raise ParseError("VHDL Parse error : misses a ';' at the end of {0} {1} definition (line {2}).".format(SubBlockType, SubBlockName, LineNb))
					else:
						if Word.startswith(';'): break
						elif WordOri=='{0};'.format(SubBlockName): break
						else:
							raise ParseError("VHDL Parse error : misses a ';' at the end of {0} {1} definition (line {2}).".format(SubBlockType, SubBlockName, LineNb))
				elif Word=='end;':
					break
				
			#--------------------------------------------------------
			# Instanciate a module instance for each entity found
			SigList, i=GetInterface(BlockContent, SubBlockName)
			Mod=Module(XMLElmt=None, FilePath=FilePath)
			Mod.Name=SubBlockName
			for Sig, IsGeneric in SigList:
				if IsGeneric:
					Mod.AddParameterAsSignal(Sig)
				else:
					Mod.AddPortAsSignal(Sig)
			
			#Check the evaluability of ports sizes-------------------
			Vars=AlstomFunctionsMapping.copy()
			Vars.update(Mod.GetConstants())
			for PName, P in Mod.Ports.items():
				P.GetSize(Vars=Vars)
			ModuleList.append(Mod)
			#--------------------------------------------------------
			# Finish the entity parse
			logging.debug("[GetSubBlocks] Seeking 'end' : analyze '{0}', Line {1}.".format(BlockContent[i][1], BlockContent[i][2]))
			if BlockContent[i][0]=='end': break
			if BlockContent[i][0]=='end;': break
			else: raise ParseError("VHDL Parse error : misses the 'end' keyword at the end of the {0} {1} definition (line {2}).".format(SubBlockType, SubBlockName, LineNb))
				
	return ModuleList

#======================================================================
def GetWords(VHDLFile, Start, End):
	"""
	return the words of a text file.
	"""
	Counter=0
	LineNb=0
	for Line in VHDLFile.readlines():
		LineNb+=1
		Line=RemoveComments(Line)
		# print("Line:", Line)
		for Word in Line.split():
			Counter+=1
			if Counter<Start: continue
			if not(End is None): 
				if Counter>End: break
			yield [Word.lower(), Word, LineNb]
		if not(End is None): 
			if Counter>End: break
            			
			
#======================================================================
def RemoveComments(Line, Symbol='--'):
	"""
	Remove comments from a string.
	"""
	if Symbol in Line:
		return Line[:Line.index(Symbol)] 
	else:
		return Line

#======================================================================
def GetInterface(BlockContent, BlockName):
	"""
	Return signal instances from signals found in the generic field of an entity definition.
	BlockContent contains the list of words contained in a port definition.
	"""
	i=0
	SignalList=[]
	while i<len(BlockContent):
		if BlockContent[i][0].startswith('generic'): 
			IsGeneric=True;
			if len(BlockContent[i][0])>7:
				BlockContent[i][0]=BlockContent[i][0][7:]
			else: i+=1
		elif BlockContent[i][0].startswith('port'):  
			IsGeneric=False;
			if len(BlockContent[i][0])>4:
				BlockContent[i][0]=BlockContent[i][0][4:]
			else: i+=1
		#----------------------------
		# Check the end of an entity definition
		elif BlockContent[i][0]=='end': 
			return SignalList, i
		#----------------------------
		else:
			# logging.warning("VHDL entity should contain either 'port' or 'generic' definitions (line {0}).".format(BlockContent[i][2]))
			logging.warning("VHDL entity '{0}' do not contain any 'port' or 'generic' definition (line {1}).".format(BlockName, BlockContent[i][2]))
			return SignalList, i
		#----------------------------
		# Find open/close brackets
		if BlockContent[i][0]=='(': i+=1
		elif BlockContent[i][0].startswith('('): BlockContent[i][0]=BlockContent[i][0][1:]
		else:
			raise ParseError("VHDL Parse error : missing opening bracket (line {0}).".format(BlockContent[i][2]))
		while 1:
			# Test end of generic/port block
			if BlockContent[i][0].startswith(')'): break
			# Get signal definition
			Sig, i=ConsumeEntitySignalDefinition(BlockContent, i, Generic=IsGeneric)
			SignalList.append( (Sig, IsGeneric) )
		#----------------------------
		# Find the closing bracket
		if BlockContent[i][0]==')': i+=1;
		elif BlockContent[i][0].startswith(')'): BlockContent[i][0]=BlockContent[i][0][1:]
		else:
			raise ParseError("VHDL Parse error : cannot find the closing bracket of {0} block in the entity (line {0}).".format('generic' if Generic else 'port', BlockContent[i][2]))
		#----------------------------
		# Find the closing ';'
		if BlockContent[i][0]==';': i+=1;
		elif BlockContent[i][0].startswith(';'): BlockContent[i][0]=BlockContent[i][0][1:]
		else:
			raise ParseError("VHDL Parse error : cannot find the closing bracket of {0} block in the entity (line {0}).".format('generic' if Generic else 'port', BlockContent[i][2]))
			
	raise ParseError("VHDL Parse error : missing the end of the entity (line {0}).".format(BlockContent[i][2]))


#======================================================================
def ConsumeEntitySignalDefinition(BlockContent, i, Generic=False):
	"""
	Return signal instances from signals found in BlockContent.
	BlockContent contains the list of words contained in a port/generic definition.
	"""
	# Find the signal name---------------
	logging.debug("[ConsumeEntitySignalDefinition] Seeking SigName : Analyze '{0}', Line {1}.".format(BlockContent[i][1], BlockContent[i][2]))
	try : SigName, i = ConsumeName(BlockContent, i)
	except ParseError:
		raise ParseError("VHDL Parse error : [parsing {0}] signal name is missing or does not fullfill the VHDL syntax (line {2}). Given : '{1}'.".format('generics' if Generic else 'ports', BlockContent[i][1], BlockContent[i][2]))
	if i>=len(BlockContent):
		raise ParseError("VHDL Parse error : unexpected end of block definition (Line {0}). Please look for a missing ')' or any missplaced keyword or special character.".format(BlockContent[-1][2]))
	if SigName.lower() in ('end', 'entity', 'signal', 'process', 'begin', 'architecture', 'configuration', 'library', 'use', 'is', 'variable', 'constant'):
		raise ParseError("VHDL Parse error : unexpected '{0}' found while looking for Signal name (line {1}).".format(BlockContent[i][1], BlockContent[i][2]))
		
	logging.debug("[ConsumeEntitySignalDefinition] Seeking ':' : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
	# Find the ':'-----------------------
	if BlockContent[i][0]==':': i+=1
	elif BlockContent[i][0].startswith(':'): BlockContent[i][0]=BlockContent[i][0][1:]
	else:
		raise ParseError("VHDL Parse error : while parsing {0},  ':' is missing, at least (line {1}).".format('generics' if Generic else 'ports', BlockContent[i][2]))
	# Get the direction------------------
	Direction=None
	if Generic is False:
		logging.debug("[ConsumeEntitySignalDefinition] Seeking 'in'/'out' : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
		if BlockContent[i][0]=='in': Direction='IN'
		elif BlockContent[i][0]=='out': Direction='OUT'
		elif BlockContent[i][0]=='inout': Direction='INOUT'
		else:
			raise ParseError("VHDL Parse error : wrong direction specified. Should be either 'in', 'ou' or 'inout' (line {1}).".format('generics' if Generic else 'ports', BlockContent[i][2]))
		i+=1
	# Get the type name------------------
	logging.debug("[ConsumeEntitySignalDefinition] Seeking TypeName : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
	try : TypeName, i = ConsumeName(BlockContent, i)
	except ParseError:
		raise ParseError("VHDL Parse error : [while parsing {0}] signal name is missing or does not fullfill the VHDL syntax (line {1}).".format('generics' if Generic else 'ports', BlockContent[i][2]))
	# Test if array is constrained-------
	if BlockContent[i][0]=='(': IsConstrainedArray=True; i+=1
	elif BlockContent[i][0].startswith('('): IsConstrainedArray=True; BlockContent[i][0]=BlockContent[i][0][1:]
	else: # not an array or unconstrained array
		IsConstrainedArray=False
	# Get the array left Bound-----------------
	if IsConstrainedArray is True:
		LeftBound=""
		while(BlockContent[i][0]!='downto' and BlockContent[i][0]!='to'):
			logging.debug("[ConsumeEntitySignalDefinition] Seeking LeftBound : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
			LeftBound+=BlockContent[i][0]
			i+=1
			if i>len(BlockContent):
				raise ParseError("VHDL Parse error : unexpected end of {0} definition (line {1}).".format('generics' if Generic else 'ports', BlockContent[i][2]))
	# Get the downto/to keyword----------------
	if IsConstrainedArray is True:
		logging.debug("[ConsumeEntitySignalDefinition] Seeking 'downto'/'to' : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
		if BlockContent[i][0]=='downto': i+=1; Downto=True
		elif BlockContent[i][0]=='to': i+=1; Downto=False
		else:
			raise ParseError("VHDL Parse error : while parsing {0},  keywords 'downto' or 'to' expected (line {1}).".format('generics' if Generic else 'ports', BlockContent[i][2]))
	# Get the array right Bound----------------
	if IsConstrainedArray is True:
		RightBound=""
		OldNumber = OpenBrackets(0, BlockContent[i][0])
		while OldNumber >= 0:
			logging.debug("[ConsumeEntitySignalDefinition] Seeking RightBound : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
			RightBound+=BlockContent[i][0]
			i+=1
			if i>len(BlockContent):
				raise ParseError("VHDL Parse error : unexpected end of {0} definition (line {1}).".format('generics' if Generic else 'ports', BlockContent[i][2]))
			OldNumber = OpenBrackets(OldNumber, BlockContent[i][0])
		# Get closing bracket------------------------
		Rest, BlockContent[i][0]=BlockContent[i][0].split(')',1)
		if len(BlockContent[i][0])==0: i+=1
		RightBound+=Rest
			
	# Get default value--------------------------
	if BlockContent[i][0]==':=': i+=1; HasDefault=True
	elif BlockContent[i][0].startswith(':='): BlockContent[i][0]=BlockContent[i][0][2:];HasDefault=True
	else: HasDefault=False

	DefaultValue=None
	if HasDefault is True:
		logging.debug("[ConsumeEntitySignalDefinition] Seeking default value : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
		DefaultValue=""
		OldNumber = OpenBrackets(0, BlockContent[i][0])
		while OldNumber >= 0 and not (';' in BlockContent[i][0]):
			logging.debug("[ConsumeEntitySignalDefinition] Seeking default value : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
			DefaultValue+=BlockContent[i][0]
			i+=1
			if i>len(BlockContent):
				raise ParseError("VHDL Parse error : unexpected end of {0} definition (line {1}).".format('generics' if Generic else 'ports', BlockContent[i][2]))
			OldNumber = OpenBrackets(OldNumber, BlockContent[i][0])
		# if both ';' and port/generic ')' is found-----------------
		if (');' in BlockContent[i][0]):
			logging.debug("[ConsumeEntitySignalDefinition] Seeking default value and ');' : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
			Rest, BlockContent[i][0]=BlockContent[i][0].split(');',1)
			BlockContent[i][0]=');'+BlockContent[i][0]
			DefaultValue+=Rest
		# Get end of default withtout ';'------------------------
		elif (';' in BlockContent[i][0]):
			logging.debug("[ConsumeEntitySignalDefinition] Seeking default value and ';' : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
			Rest, BlockContent[i][0]=BlockContent[i][0].split(';',1)
			if len(BlockContent[i][0])==0: i+=1
			DefaultValue+=Rest
		# Get closing bracket------------------------
		else:
			Rest, BlockContent[i][0]=BlockContent[i][0].split(')',1)
			if len(BlockContent[i][0])==0: i+=1
			DefaultValue+=Rest
	# remove optional ';'------------------------
	logging.debug("[ConsumeEntitySignalDefinition] Seeking default value and ';' : Analyze '{0}', Line {1}.".format(BlockContent[i][0], BlockContent[i][2]))
	if BlockContent[i][0]==';': i+=1; 
	elif BlockContent[i][0].startswith(';'): BlockContent[i][0]=BlockContent[i][0][1:]
	
	TypeName_lower=TypeName.lower()
	if TypeName_lower=="std_logic_vector": SigType = "logic"
	elif TypeName_lower=="std_logic":      SigType = "logic"
	elif TypeName_lower=="integer":        SigType = "numeric"
	elif TypeName_lower=="natural":        SigType = "numeric"
	else: SigType = TypeName
	
	SigSize='1'
	if IsConstrainedArray: 
		if Downto is True : SigSize=LeftBound+'-{0}'.format(RightBound)+'+1'
		else: SigSize=RightBound+'-{0}'.format(LeftBound)+'+1'
		
	logging.debug("[ConsumeEntitySignalDefinition] Instanciate Signal object Name='{0}' / Type='{1}' / Default='{2}'.".format(SigName, TypeName, DefaultValue))
	Sig = Signal(
	         Name=SigName, 
	         Type=SigType, 
	         PTypeImport= TypeName if SigType == TypeName else None, 
	         Size=SigSize, 
	         Default=DefaultValue, 
	         Dir=Direction, 
	         Modifier=None, 
	         Index=None, 
	         ParamVars={}
	         )
	
	return Sig, i
		

	
NameRegex = re.compile("(\w)", re.IGNORECASE)
#======================================================================
def CheckName(SigName, LineNb):
	"""
	raise a parseError if a name does no fullfill syntex requirements.
	"""
	if NameRegex.match(SigName) is None:
		raise ParseError("VHDL Parse error : the name '{0}' used does not fullfill syntax requirement which is to use unicode word characters [a-z0-9_] (Line {1}).".format(SigName, LineNb))
		

#======================================================================
def ConsumeType(BlockContent):
	"""
	Parse a signal type and its default value and return words.
	"""
	TypeWords, DefaultWords = [], []
	while not (':=' in BlockContent[i][1] or ';' in BlockContent[i][1]):
		if i>=len(BlockContent): 
			raise ParseError("VHDL Parse error : premature end of signal definition (line {0}).".format(BlockContent[i-1][2]))
		TypeWords.append(BlockContent[i])
		i=+1
	if ':=' in BlockContent[i][1]:
		# Fetch default value 
		TypeDefEnd, BlockContent[i][1] = BlockContent[i][1].split(':=', 1)
		TypeWords.append(TypeDefEnd)
		HasDefault=True
		
	while not (';' in BlockContent[i][1] or ')' in BlockContent[i][1]):
		if i>=len(BlockContent): 
			raise ParseError("VHDL Parse error : premature end of signal definition (line {0}).".format(BlockContent[i-1][2]))
		if HasDefault is True: DefaultWords.append(BlockContent[i][1])
		else: TypeWords.append(TypeDefEnd)
		i=+1
	# Found ';'
	TypeDefEnd, BlockContent[i][1] = BlockContent[i][1].split(';', 1)
	if HasDefault is True: DefaultWords.append(TypeDefEnd)
	else: TypeWords.append(TypeDefEnd)
	return TypeWords, DefaultWords


#======================================================================
def ConsumeName(BlockContent, i):
	"""
	Return the first name found in BlockContent and increment (if needed) the index i.
	"""
	Regex = re.match(r"([A-Za-z0-9_]+)", BlockContent[i][1])
	try: Name = Regex.group(0)
	except: raise ParseError("VHDL Parse error : need a name composed of unicode word characters [A-Za-z0-9_]  (line {0}).".format(BlockContent[i][2]))
	
	if Name[0] in "0123456789_":
		raise ParseError("VHDL Parse error : identifiers should not start with a character in '0123456789_'. Found '{0}' (line {1}).".format(BlockContent[i][1], BlockContent[i][2]))
	if len(Name)==len(BlockContent[i][1]): 
		return Name, i+1
	else: 
		BlockContent[i][1]=BlockContent[i][1][len(Name):]
		BlockContent[i][0]=BlockContent[i][0][len(Name):]
		return Name, i
	
#======================================================================
def ConsumeInteger(BlockContent, i):
	"""
	Return the first integer found in BlockContent and increment (if needed) the index i.
	"""
	Regex = re.match(r"([0-9]+)", BlockContent[i][0])
	try: Integer = Regex.group(0)
	except: raise ParseError("VHDL Parse error : need a integer [0-9]+  (line {0}).".format(BlockContent[i][2]))
	
	if len(Integer)==len(BlockContent[i][0]): 
		return Integer, i+1
	else: 
		BlockContent[i][0]=BlockContent[i][0][len(Integer):]
		return Integer, i
		
#======================================================================
def ConsumeString(BlockContent, i):
	"""
	Return the first VHDL String description found in BlockContent and increment (if needed) the index i.
	"""
	Regex = re.match(r'(x|o?"\w+")', BlockContent[i][0])
	try: String = Regex.group(1)
	except: raise ParseError("VHDL Parse error : need a name composed of unicode word characters [a-z0-9_] with hexadecimal, octal or binary format  (line {0}).".format(BlockContent[i][2]))
	
	if len(String)==len(BlockContent[i][0]): 
		return String, i+1
	else: 
		BlockContent[i][0]=BlockContent[i][0][len(String):]
		return String, i
		
#======================================================================
def ConsumeChar(BlockContent, i):
	"""
	Return the first VHDL String character description found in BlockContent and increment (if needed) the index i.
	"""
	Regex = re.match(r"('\w+')", BlockContent[i][0])
	try: Char = Regex.group(0)
	except: raise ParseError("VHDL Parse error : need a integer [0-9]+  (line {0}).".format(BlockContent[i][2]))
	
	if len(Char)==len(BlockContent[i][0]): 
		return Char, i+1
	else: 
		BlockContent[i][0]=BlockContent[i][0][len(Char):]
		return Char, i
	
#======================================================================
def OpenBrackets(OldNumber, Expression):
	"""
	Count the number of open bracket - the number of close brackets.
	"""
	return OldNumber+ Expression.count('(') - Expression.count(')')
	
#====================================================================	
def DirectoryPath(Path):
	"""
	raise error if path is no a directory
	"""
	if os.path.isdir(Path):
		return os.path.abspath(Path)
	else: 
		raise TypeError
		
#=======================================================================
def SetupParseOptions(SubParsers):
	"""
	Parse argument options and do corresponding actions.
	"""
	ArgParser = SubParsers.add_parser('parseregression', help='Iterate through all VHDL files of a given directory and try parsing all entities. Exit when an error is found.')
	
	#------------------General command arguments-------------------------------------
	# ARGUMENT: source directory
	ArgParser.add_argument('directory', action='store', type=DirectoryPath , help="Sources directory where VHDL files are stored (consider subdirectories as well).")
	# ARGUMENT: Display version
	# ArgParser.add_argument('-v', '--version', action='version', version="SetupTBGen version='{0}'".format(VERSION), help="Displays SetupTBGen version.")
	
	ArgParser.set_defaults(func=ParseRegression_Opt)
	return ArgParser
	
#================================================================
def ParseRegression_Opt(Options):
	"""wrapper for ParseRegression function"""
	return ParseRegression(SourcesPath=Options.directory)

#================================================================
def ParseRegression(SourcesPath):
	"""
	Iterate through all VHDL files of a given 'SourcesPath' directory and try parsing all entities. Exits when an error is found.
	"""
	for (DirPath, DirNames, FileNames) in os.walk(SourcesPath, topdown=True, onerror=None, followlinks=True):
		FileNames=[F for F in FileNames if F.lower().endswith('.vhd')]
		for FilePath in [os.path.join(DirPath, FileName) for FileName in FileNames]:
			# try:
			try: ModList=ParseVHDL(FilePath)
			except ParseError: 
				logging.error("VHDL parsing: regression test failed while parsing '{0}'.".format(FilePath))
				sys.exit(1)
				
	logging.info("Regression test succeeded !")
	
	
	
	
	
	
	
	




