#!/usr/bin/python


import os, sys, logging, shutil

from SysGen.PackageBuilder import PackageBuilder
import SysGen.HDLEditor as HDL
import re

#=======================================================================
class Signal:#(PackageBuilder):
	"""
	Signal object for HDL/XML signal abstraction.
	"""
	#---------------------------------------------------------------
	def __init__(self, Name="", Type="logic", PTypeImport=None, Size=None, Default=0, Dir=None, Modifier=None, Index=None, ParamVars={}):
		"""
		Gather signal parameters.
		"""
		#logging.debug("New Signal: Name={0}, Type={1}, Size={2}, Default={3}".format(Name, Type, Size, Default))
#		PackageBuilder.__init__(self)
		self.Name      = Name
		self.Direction = Dir
		if Size=="": self.Size=None
		else:        self.Size=Size
		self.FullSize = Size
		self.SubType  = None
		self.SubSize  = None
		self.Type     = Type
		self.TypeImport=PTypeImport
		
		self.Default  = 0 if Default=="" else Default
		self.Modifier = Modifier # Signal instance
#		self.ParamVars     = ParamVars.copy()
		if self.Default: self.Value = self.Default
		else: self.Value=0 
		self.Constraints=None # (Type, Identifier) reset, clock, FPGAPads and Ignore, LED, PCIe, etc (identifier from .co)
		self.IsParam=False # Set to true when signal is a parameter
		self.Index=None
#		if not self.Size: 
#			try: 
#				if self.Value:
#					self.Size=int(math.log(float(self.Value), 2))+1
#				else: self.Size=1
#			except: 
#				self.Size=self.Value
		self._UsedParams={} 
		self._UsedTypes={}  

		self.GatherUsedParams(ParamVars.copy())
		self.ComputeType()
	#---------------------------------------------------------------
	def UpdateAllValues(self, ValueDict):
		"""
		Change values of each port/params and their respective "usedparam" dictionary.
		"""
		for PName in self._UsedParams:
			if PName in ValueDict:
				self._UsedParams[PName]=ValueDict[PName]
		return
	#---------------------------------------------------------------
	def SetFrom(self, XMLElmt, Vars={}):
		"""
		gather all parameters used by this signal.
		"""
		Attr=XMLElmt.attrib
		PName=Attr.get("name").replace('.', '_')
		Default=Attr.get("default")
		self.__init__(Name=PName, Type=Attr.get("type"), PTypeImport=Attr.get("typeimport"), Size=Attr.get("size"), Default=Default, ParamVars=Vars)
	#---------------------------------------------------------------
	def Copy(self, WithName=None):
		Sig=Signal(Name=self.Name, Type=self.Type, PTypeImport=self.TypeImport, Size=self.Size, Default=self.Default, Dir=self.Direction, Modifier=self.Modifier, Index=self.Index, ParamVars=self._UsedParams.copy())
		if not (WithName is None):
			Sig.SetName(WithName)
		
		Sig.Constraints=self.Constraints
		Sig.SetValue(self.Value)
		return Sig
	#---------------------------------------------------------------
	def GatherUsedParams(self, Variables):
		"""
		gather all parameters used by this signal.
		"""
		self._UsedParams={}
#		if self.TypeImport is None: return self._UsedParams
		for Item in [self.Type, self.Size, self.Default,]:
			if Item is None: continue
			elif Item=="": continue
			for Elmt in [i for i in re.split('(\W+)', str(Item)) if re.match("\w+", i) is not None] :
				if Elmt.lower()=="logic":
					pass
				elif Elmt.lower()=="numeric":
					pass
				elif Elmt.lower()=="reset":
					pass
				elif Elmt.lower()=="clock":
					pass
				else:
					try:
						# Si Elmt est un entier : y a pas de parametre
						int(Elmt)
					except: 
						UsedParams={}
						# Sinon: evaluer avec toutes les variables fournie
						for V, VValue in Variables.items():
							VCopy=Variables.copy()
							# Et retirer une à une les variables
							VCopy.pop(V)
							TestDict=VCopy.copy()
							TestDict.update(UsedParams) # Garder les variables déjà identifiées
							try: 
								eval(Elmt, TestDict)
							except: 
								# Jusqu'à ce que l'évaluation échoue
								UsedParams[V]=VValue # 
#								logging.debug("[{0}] Parameter '{1}' used.".format(self.Name, V))
						try: 
							eval(Elmt, UsedParams.copy())
							self._UsedParams.update(UsedParams)
						except: 
#							self._UsedParams[Elmt]=0
							logging.warning("[GatherUsedParams] Parameters used in expression '{0}' for signal {2} not found (not in Variables {1}).".format(Elmt, Variables, self.Name))
#							raise TypeError
#							sys.exit(1)
							continue
#							raise NameError
#							if self.Name=="TaskID":
#								print "Elmt:", Elmt
#								print "Variables:", Variables
#								raw_input()
#						try: 
#						if eval(Elmt, self._UsedParams.copy()) is None: continue
#						except: 
#							logging.error("[{0}] Parameter '{1}' not defined.".format(self.Name, Elmt))
#							continue
#						print "S:", self.Name
#						print "> Elmt:", Elmt
#						self._UsedParams[Elmt]=eval(Elmt, Variables.copy())
								
#		logging.debug("[{1}] UsedParams: {0}.".format(list(self._UsedParams.keys()), self.Name))
		return self._UsedParams
	#---------------------------------------------------------------
	def GetName(self):
		"""
		return name of signal.
		"""
		return self.Name
	#---------------------------------------------------------------
	def SetName(self, Name):
		"""
		Change name of signal.
		"""
		self.Name=Name
		return self.Name
	#---------------------------------------------------------------
	def SetValue(self, Value):
		"""
		Changes the value of signal.
		"""
		if Value==self.Name:
			raise NameError
		if self.Type in ("logic", "numeric"):
			try:    self.Value=int(Value)
			except: self.Value=Value
		else:
			self.Value = Value
		return self.Value
	#---------------------------------------------------------------
	def SetDefault(self, Value):
		"""
		Changes the default value of signal.
		"""
		if self.Type in ("logic", "numeric"):
			try:    self.Default=int(Value)
			except: self.Default=Value
		else:
			self.Default = Value
		return self.Default
	#--------------------------------------------------------------
	def UpdateVars(self, Vars):
		"""
		Update self._UsedParams dictionary attribute.
		"""
		for k in self._UsedParams:
			if k in Vars:
				self._UsedParams[k]=Vars[k]
		return self._UsedParams
	#---------------------------------------------------------------
	def GetValue(self, NoEval=False, Vars={}):
		"""
		return a value attribute.
		"""
		if NoEval:
			return self.Value
		else:
			NewVars=self._UsedParams.copy()
			NewVars.update(Vars)
			return eval(str(self.Value), NewVars)
	#---------------------------------------------------------------
	def GetDefaultValue(self, NoEval=False, Vars={}):
		"""
		return a value attribute.
		"""
		if NoEval:
			return self.Default
		else:
			NewVars=self._UsedParams.copy()
			NewVars.update(Vars)
			return eval(str(self.Default), NewVars)
	#---------------------------------------------------------------
	def GetUsedParam(self):
		"""
		Return the dictionary of USED parameters.
		"""
		return self._UsedParams.copy()
	#---------------------------------------------------------------
	def GetUsedTypes(self):
		"""
		Return the dictionary of USED types.
		"""
		return self._UsedTypes
	#---------------------------------------------------------------
	def __len__(self):
		return self.FullSize
	#---------------------------------------------------------------
	def CollectPkg(self):
		"""
		Nothing to collect: pass.
		"""
		pass
	#---------------------------------------------------------------
	def OrthoName(self):
		"""
		Return Name of orthogonal signal with modifier.
		"""
		# Determine formal ortho port name			
		if self.Modifier!=None: 
			# Rename port according to modifier
			return self.Name+'_'+str(self.Modifier.Value)
		else:
			return self.Name
	#---------------------------------------------------------------
	def __getitem__(self, index):
		"""
		Return copy of signal with size of 1 or subsize.
		"""
		if index is None:
			SCopy=self.Copy()
			SCopy.SetIndex(Index=index)
			return SCopy
		elif isinstance(index, int):
			SCopy=self.Copy()
			SCopy.TypeImport=None
			# EXAMPLE: size="DimX*DimY" type="FlitWidth*logic" typeimport="FLITS"
			if self.SubType is None: # do not has subtype
				if SCopy.Size==1: logging.warning("Indexed signal of size 1: kept size.")
				SCopy.Size=1
				SCopy.GatherUsedParams(self.GetUsedParam())
				return SCopy
			else:
				SCopy.Type=self.SubType
				SCopy.Size=self.SubSize
				if hasattr(self.Default, "__getitem__"):
					SCopy.Default=self.Default[index] 
				if hasattr(self.Value, "__getitem__"):
					SCopy.Value=self.Value[index]
				SCopy.GatherUsedParams(self.GetUsedParam())
				SCopy.SetIndex(Index=index)
				return SCopy
		elif isinstance(index, slice):
			SCopy=self.Copy()
#			if hasattr(self.Default, "__getitem__"):
#				SCopy.Default=self.Default[index.start:index.stop] 
#			if hasattr(self.Value, "__getitem__"):
#				SCopy.Value=self.Value[index.start:index.stop]
			SCopy.SetIndex(Index=index)
			return SCopy
		else:
			raise TypeError("Signal index must be int or slice")
	#---------------------------------------------------------------
	def SetIndex(self, Index=None):
		"""
		Set Index attributes.
		"""
		self.Index=Index
		return self.Index
	#---------------------------------------------------------------
	def GetIndex(self):
		"""
		return Index attributes.
		"""
		return self.Index
	#---------------------------------------------------------------
	def ComputeType(self):
		"""
		Analyze Type content and generate a synthesizable type format from it.
		When necessary, add type and constant and packages to package object.
		"""
		Type=self.Type.strip('(').strip(')')
		if self.TypeImport!=None and self.TypeImport!="":
			# Keep specified type
			if len(self.TypeImport.split('.'))>1: 
				Pkg, NewType = self.TypeImport.split('.')
				SubType, SubSize, T = ParseType(Type)
				if SubSize and not isinstance(self.Default, list) and not (self.Default is None):
					logging.warning("Default value ('{0}') of subtyped signal '{1}' is not a list.".format(self.Default, self.Name)) 
#				self.Package["TypeImport"][NewType] = [SubSize, T, Pkg]
				# Eventually add a constant declaration to package
				UsedConst=[]
				if SubType!=None:
					try: 
						self.FullSize=self.Size*int(SubSize)
					except: 
						# Build signal for constant declaration
						for Elmt in re.split('\+ |\- |\*|\/ |\n |<< |>>', str(SubSize)):
							if not Elmt in ["logic", "numeric"]:
								UsedConst.append(Elmt)
#						for C0 in SubSize.split('*'):
#							for C1 in C0.split('+'):
#								for C2 in C1.split('-'):
#									for C3 in C2.split('/'):
#										self.Package["Constants"][C3]=Signal(C3).HDLFormat(self._UsedParams.copy())
						self.FullSize=str(self.Size)+'*'+str(SubSize)
				self._UsedTypes[NewType] = [SubSize, T, Pkg, UsedConst]
				NewType=NewType.replace('*',"_x_").replace( '+',"_plus_").replace('-',"_minus_").replace('/',"_divby_").replace('(',"").replace(')',"")	
				self.SubType=SubType
				self.SubSize=SubSize
#				raw_input("NewType: {0} | {1}".format(NewType, self._UsedTypes))
				return NewType
			else: 
				SubType, SubSize, T = ParseType(Type)
				if SubSize and not isinstance(self.Default, list) and not (self.Default is None) and not (self.Default.lower() is "open"):
					logging.warning("Default value ('{0}') of subtyped signal '{1}' is not a list.".format(self.Default, self.Name)) 
				self.SubType=SubType
				self.SubSize=SubSize
				return self.TypeImport
		if Type=="numeric":
			return Type	
		elif Type=="logic": 
			try: 
				if int(self.Size)!=1: self.SubSize=1
			except:
				self.SubSize=1
			return Type				
		else:
			SubType, SubSize, T = ParseType(Type) # S=SubSize, T=SubType
			self.SubType=SubType
			self.SubSize=SubSize
			if SubSize!=None: # If type is complex (has an array subtype)
				# Create new type from size * subtype
				NewType="{0}_{1}".format(str(SubSize).upper(), T.upper())
				
				NewType=NewType.replace('*',"_x_").replace( '+',"_plus_").replace('-',"_minus_").replace('/',"_divby_").replace('(',"").replace(')',"")	
				# Create a whole new type
#				self.Package["Types"][NewType]=[NewType, SubSize, T]
				UsedConst=[]
				for Elmt in re.split('\+|\-|\*|/|\n|<<|>>', str(SubSize)):
					if not Elmt in ["logic", "numeric"]:
						UsedConst.append(Elmt)
				
#				print("-----")
#				print("SubSize:", NewType)
#				print("SubSize:", SubSize)
#				print("UsedConst:", UsedConst)
#				input()
				self._UsedTypes[NewType] = [SubSize, T, None, UsedConst] # Size, SubType, Pkg, UsedConst
				# Update FullSize value
				try: 
					self.FullSize=self.Size*int(SubSize)
				except: 
#					for C0 in SubSize.split('*'):
#						for C1 in C0.split('+'):
#							for C2 in C1.split('-'):
#								for C3 in C2.split('/'):
#									self.Package["Constants"][C3]=Signal(C3).HDLFormat(self.GetUsedParam())
					if self.Size is None:
						self.FullSize=str(SubSize)
					else:
						self.FullSize=str(self.Size)+'*'+str(SubSize)
				 
				return NewType	
			else:
				return Type
	#---------------------------------------------------------------
	def GetSize(self):
		"""
		return a int number for size.
		"""
		try: return 1 if self.Size is None else eval(str(self.Size), self._UsedParams.copy())
		except: 
			logging.error("Signal '{0}' : unable to evaluate size '{0}' (given variables: {1})".format(self.Name, self.Size, self._UsedParams))
			sys.exit(1)
	#---------------------------------------------------------------
	def HDLFormat(self, ParamVars={}):
		"""
		return a Signal object (HDLEditor) for HDL instanciation.
		"""
		Variables = self._UsedParams.copy()
		Variables.update(ParamVars)
#		logging.error("[{0}] Variables: '{1}'.".format(self.Name, Variables))
		#--------------------------------------------
		if self.Size!="" and not (self.Size is None):
			try: Size=int(self.Size, 10)
			except: 
				Size=eval(str(self.Size), Variables)
#				{0}if Size is None:
#					logging.error("Size '{0}' evaluated to None.".format(self.Size))
#					raise TypeError
#				try: int(str(Size), 10)
#				except: 
#					if Default==None: Size=2
#					else: 
#						if isinstance(Default, list): Size=
#						Size=int(math.log(float(str(self.Default)), 2))
		else:
			Size=None
		#--------------------------------------------
		if self.Default!="open" and not (self.Default is None):
			if isinstance(self.Default, str):
				Default=[]
				for Elmt in self.Default.split(';'):
					Default.append(eval(str(Elmt), Variables))
				if len(Default)==1:
					Default=Default[0]
			else: Default=self.Default
				
		else: 
#			if "*" in self.Type:
#				Default=[0 for i in range(Size)]
#			else:
#				Default=0
			Default=None
		#--------------------------------------------
		if not (self.SubType is None) and self.Size==1:
			if self.SubSize!="":
				try: SubSize=int(self.SubSize, 10)
				except: 
					SubSize=eval(str(self.SubSize), Variables)
			return HDL.Signal(Item=self.OrthoName(), Direction=self.Direction, Size=SubSize, Type=self.SubType, InitVal=Default, IsArray=False, GenericSize=self.SubSize)
		elif ("*" in self.Type) and ('numeric' in self.Type.lower() or 'logic' in self.Type.lower()): 
			IsArray=True
		elif (self.Type.lower()=="numeric" and Size!=1) and not (Size is None): 
			IsArray=True
		else: IsArray=False
#		print(self.Name,'(', self.Type, '/', self.Size,')', "=>", IsArray)
		#--------------------------------------------
		if self.Size=="None":self.Size=None # TODO: understand why Size become "None"
		if Default=="None":Default=0
		if self.Value=="None":self.Value=0
		HDLSig=HDL.Signal(Item=self.OrthoName(), Direction=self.Direction, Size=Size, Type=self.ComputeType(), InitVal=Default, CurValue=self.Value, IsArray=IsArray, GenericSize=self.Size)
		
		if self.Index is None: return HDLSig
		else: return HDLSig[self.Index]
	#---------------------------------------------------------------
	def Rename(self, NewName):
		"""
		return a copy of the signal with a NewName instead of current one.
		"""
		Sig=Signal(Name=NewName, Type=self.Type, PTypeImport=self.TypeImport, Size=self.Size, Default=self.Default, Dir=self.Direction, Modifier=self.Modifier, Index=self.Index, ParamVars=self._UsedParams.copy())
		Sig.SetValue(self.Value)
		return Sig
	#---------------------------------------------------------------
	def integers(self, Base=10, Variables={}):
		if isinstance(self.Value, list): return [int(str(eval(str(x), Variables)), Base) for x in self.Value]
		elif isinstance(self.Value, str): 
			#if len(self.Value.split(','))>1:
			#	return map(lambda x: int(str(eval(str(x), Variables)), Base), self.Value.split(','))
			#else: return int(str(eval(str(self.Value.split(';')[0]), Variables)), Base)
			return eval(str(self.Value), Variables) # String must respect python syntax
		else: return int(str(eval(str(self.Value), Variables)), Base)
	
	#---------------------------------------------------------------
	def Divide(self, Divider):
		if str(Divider) in self.Type:
			if '*{0}'.format(Divider) in self.Size:
				Type = self.Type.replace('*{0}'.format(Divider), "")
			else:
				Type = self.Type.replace(Divider, "")
			Size = self.Size
		elif str(Divider) in self.Size:
			if '*{0}'.format(Divider) in self.Size:
				Size = self.Size.replace('*{0}'.format(Divider), "")
				Type = self.Type
			else:
				SubSize = self.Type.split("*")
				if len(SubSize)>1:
					Size = self.Size.replace(Divider, self.Type[:self.Type.rindex('*')])
					Type = self.Type[self.Type.rindex('*')+1:]
				else:
					Size = self.Size.replace(Divider, "1")
					Type = self.Type
		else:
			if self.Size==1:
				logging.error("Failed to divide signal '{3}' by '{0}': Keep original (Size:'{1}'/Type:'{2}').".format(Divider, self.Type, self.Size, self.Name))
				raise TypeError
			Type = self.Type
			Size = self.Size
			
		self.TypeImport=None
		self.SubType=None
		S=Signal(Name=self.Name, Type=Type, PTypeImport=self.TypeImport, Size=Size, Default=self.Default, Dir=self.Direction, Modifier=self.Modifier, ParamVars=self._UsedParams.copy())
		if hasattr(self.Default, "__getitem__"):
			S.Default=self.Default[index] 
		else:
			S.Default=self.Default
		if hasattr(self.Value, "__getitem__"):
			S.Value=self.Value[index]
		else:
			S.Value=self.Value
		return S	
	#----------------------------------------------------------------------
	def InverseDirection(self):
		"""
		Change 'IN' into 'OUT' and conversely.
		"""
		if self.Direction=='IN': self.Direction='OUT'
		elif self.Direction=='OUT': self.Direction='IN'
		return self.Direction# Do nothing if INOUT
	#---------------------------------------------------------------
	def __repr__(self):
		return "SyntheSys.SysGen.Signal.Signal(Name={0}, Type={1}, TypeImport={2}, Size={3}, Default={4}, Dir={5}, Modifier={6}, ParamVars={7})".format(repr(self.Name), repr(self.Type), repr(self.TypeImport), repr(self.Size), repr(self.Default), repr(self.Direction), repr(self.Modifier), repr(self._UsedParams))
	#---------------------------------------------------------------
	def __str__(self):
		"""
		Return signal name with its associated parameters.
		"""
		#return "{0}[Dir={1}]{2}bit({3})={4}#MOD({5})#Share({6} - CUSTOMTYPE={7})".format(self.Name, self.Direction, self.Size, self.Type, self.Default, self.Modifier, self.TypeImport)
		HDL_SIG = self.HDLFormat(ParamVars=self._UsedParams.copy())
		if self.IsParam:
			return "{0}={1}".format(HDL_SIG.GetName(), HDL_SIG.GetValue())
		else:
			return HDL_SIG.GetName()
	#---------------------------------------------------------------
	def AVAName(self):
		"""
		Return signal name respecting AVA format.
		"""
		HDL_SIG = self.HDLFormat(ParamVars=self._UsedParams.copy())
		return HDL_SIG.AVAName()
			
#=======================================================================
def SigName(Code, OrderedIndexes=[], ParamVars={}, LocalParams={}):
	"""
	Parse signal name and return normalized name format.
	"""
	if Code.startswith('{') and Code.endswith('}'):
		ToConcatList = [S.strip('{').strip('}') for S in Code.split(',')]
	else:
		ToConcatList = [Code,]
	IndexedSigList = []
	#logging.debug("Code={0}".format(Code))
	for ToConcatSig in ToConcatList:
		try: Inst, Sig = ToConcatSig.split('.') # Separate signal name from instance name
		except: Inst, Sig = "", ToConcatSig
		# split instance name and indexes (when in loop)
		InstID = Inst.split(':')
		if InstID[0]=='': InstID[0]=Inst 
		#logging.debug("InstID={0}".format(InstID))
		
		for i in range(1, len(InstID)):
			try: InstID[i] = OrderedIndexes[i-1]+str(eval(InstID[i], ParamVars))
			except: logging.critical('Failed to get instance name for "{0}" in a loop. Make sur your indexed it (name="instance:var")'.format(InstID))
			
		if len(InstID)>1: InstName = "_".join([InstID[0], "".join(InstID[1:])])
		else: InstName = InstID[0]
		
		# Fetch local constants
		if list(LocalParams.keys()).count(Sig): Sig=LocalParams[Sig]
		# split signal name and indexes
		SigID = Sig.split(':')
		SigName = SigID[0]
		Index=None
		if len(SigID)>1:
			Range = SigID[1].split('~') # TODO: comment please !!!!
			Min=eval(Range[0], ParamVars)
			if len(Range)>1: 
				Max=eval(Range[1], ParamVars)
				Index=[Min, Max]
			else:
				Index=Min
		else:
			Index=None
		for i in range(1, len(SigID)):
			SigID[i] = eval(SigID[i], ParamVars)
		
		IndexedSigList.append([InstName, SigName, Index])
		if SigName=='': sys.exit(1)
	return IndexedSigList
			
#============================================================================
def GetActualName(ActualList, ParamVars={}):
	"""
	Return a value (string format) of actual signal described by a list.
	"""
	ConcatList, Cond, LocalVars = ActualList
	Variables=ParamVars.copy()
	Variables.update(ParamVars)
	if eval(str(Cond), Variables):
		for Inst, SigVal, Index in ConcatList:
			if len(Inst)<1:
				if Index==None:
					return str(SigVal)
				else:
					S=Signal(SigVal)
					S.SetIndex(Index)
					return S.Name
			else:
				if Index==None:
					return str(Inst)+'_'+str(SigVal)
				else:
					S=Signal(str(Inst)+'_'+str(SigVal))
					S.SetIndex(Index)
					return S.Name
					
	else:
		return None



#============================================================================
def ParseType(Type):
	"""
	Return subsize and subtype of type according to XML syntaxe.
	Size returned is None when it's not a subtype.
	"""
	Index = Type.rfind('*')
	if Index!=-1: # If type is complex (has subtype)
		SubType=Type[Index+1:].lower()
		if SubType in ["logic", "numeric"]:
			# Find subtype size			
			SubSize = Type[:Index].strip('(').strip(')')
	#		# Create new type from size * subtype
	#		NewType="{0}_{1}".format(SubSize.upper(), Type[Index+1:].upper())
			return SubType, SubSize, Type[Index+1:]
		# Else it's not a array type, it's a custom type.
		else: return None, None, Type
	else:
		return None, None, Type
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

