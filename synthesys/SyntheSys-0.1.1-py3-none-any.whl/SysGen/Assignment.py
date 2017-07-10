#!/usr/bin/python

###########################################################################
# ADACSYS                                                                 #
#                                                                         #
# Copyright (c), ADACSYS 2008-2014                                        #
# All Rights Reserved.                                                    #
# Licensed Materials - ADACSYS                                            #
#                                                                         #
# No part of this file may be reproduced, stored in a retrieval system,   #
# or transmitted in any form or by any means --- electronic, mechanical,  #
# photocopying, recording, or otherwise --- without prior written         #
# permission of ADACSYS.                                                  #
#                                                                         #
# WARRANTY:                                                               #
# Use all material in this file at your own risk. ADACSYS makes no claims #
# about any material contained in this file.                              #
###########################################################################


import os, sys, datetime, logging

#======================================================================
class AssignmentSignal:
	#-------------------------
	def __init__(self, Sig):
		try: self.Sig=Sig.HDLFormat()
		except: self.Sig=Sig
		self.NonAssignedBits=Sig.GetSize()
		self.IMin=0
		self.IMax=self.NonAssignedBits-1
	#-------------------------
	def GetName(self):
		"""
		return name of signal.
		"""
		return self.Sig.Name
	#-------------------------
	def SetName(self, Name):
		"""
		Change name of signal.
		"""
		self.Sig.Name=Name
		return self.Sig.Name
	#-------------------------
	def Copy(self):
		"""
		return a copy of this object
		"""
		New=AssignmentSignal(self.Sig.Copy())
		New.IMin=self.IMin
		New.IMax=self.IMax
		New.NonAssignedBits=self.NonAssignedBits
		return New
	#-------------------------
	def Reset(self):
		self.NonAssignedBits=self.Sig.GetSize()
		self.IMin=0
		self.IMax=self.NonAssignedBits-1
	#-------------------------
	def HasNonAssignedBits(self):
		return self.NonAssignedBits>0
	#-------------------------
	def AssignTo(self, Other):
		"""
		"""
		Assignments=AssignmentStatement()
		if Other.NonAssignedBits==0:
			logging.warning("'{0}' no more non assigned bits: skipped.".format(Other))
			return None
		elif Other.NonAssignedBits>self.NonAssignedBits: # If Full space for self in Other
			# Connect self=>part(Other) and decrement Available bits 
			BitsToBeAssign=self.NonAssignedBits
			logging.debug("Full space for {0} in {1} - Assign {2} bits".format(self, Other, BitsToBeAssign))
			Assignments.Add(
				Assignee=Other.Sig[Other.IMin:Other.IMin+self.NonAssignedBits], 
				Assignor=self.Sig[self.IMin:self.IMin+self.NonAssignedBits], 
				Cond=None)
			Other.NonAssignedBits-=BitsToBeAssign
			Other.IMin+=BitsToBeAssign
			self.IMin=self.IMax
			self.NonAssignedBits=0
			logging.debug("   > Result: {0} / {1}".format(self, Other))
		elif Other.NonAssignedBits<self.NonAssignedBits: # If Other is smaller than self
#				if (self.IMin>0): # if self already filled another signal: ignore it.
#					return []
			# Not enough space for full D: Connect part(self)=>Other and decrement Available bits
			BitsToBeAssign=Other.NonAssignedBits
			logging.debug("Not enough space for full {0}: Connect part({0})=>{1} and decrement Available bits".format(self, Other))
			Assignments.Add(
				Assignee=Other.Sig[Other.IMin:Other.IMin+Other.NonAssignedBits], 
				Assignor=self.Sig[self.IMin:self.IMin+Other.NonAssignedBits], 
				Cond=None)
			self.NonAssignedBits-=BitsToBeAssign
			self.IMin+=BitsToBeAssign
			Other.IMin=Other.IMax
			Other.NonAssignedBits=0
		else: # Equality
			# Connect Src=>D and decrement Available bits
			BitsToBeAssign=self.NonAssignedBits
			logging.debug("Full space for {0} in {1} - Assign {2} bits".format(self, Other, BitsToBeAssign))
			Assignments.Add(
				Assignee=Other.Sig, 
				Assignor=self.Sig, 
				Cond=None)
			self.NonAssignedBits=Other.NonAssignedBits=0
			self.IMin=self.IMax
			Other.IMin=Other.IMax
		return Assignments
	#-------------------------
	def __repr__(self):
		"""
		Return signal name with its associated object.
		"""
		return "{0}[{2}:{1}]".format(self.Sig.Name, self.IMin, self.IMax)
	#-------------------------
	def __str__(self):
		"""
		Return signal name with its associated object.
		"""
		return "{0}[{2}:{1}]".format(self.Sig.Name, self.IMin, self.IMax)

#======================================================================
class AssignmentStatement:
	#-------------------------
	def __init__(self, Assignee=None, Assignor=None, Cond=None, Desc=""):
		"""
		Initialize hierarchy.
		"""
		self.Description=Desc
		self._Hierarchy=[] # List of pair condition/AssignmentStatement
		self._AssignedSignals=[]
		self._AssignorSignals={}
		if Assignee is None: pass 
		else: self.Add(Assignee=Assignee, Assignor=Assignor, Cond=Cond, Desc=Desc)
	#-------------------------
	def Add(self, Assignee, Assignor=None, Cond=None, Desc=""):
		"""
		Add assignment with its optional condition to hierarchy.
		"""
		if isinstance(Assignee, AssignmentStatement):
			self._AssignedSignals+=Assignee.GetAssignedSignals()
			self._AssignorSignals.update(Assignee._AssignorSignals)
		elif isinstance(Assignee, list):
			Statements=[]
			for A in Assignee:
				self._AssignedSignals+=A.GetAssignedSignals()
				self._AssignorSignals.update(A._AssignorSignals)
				Statement={"Assignee":A, "Assignor":None, "Comments":""}
				if not (Cond is None):
					for D in self._Hierarchy:
						if D["Condition"]==Cond: 
							D["Statements"].append(Statement)
							continue
				Statements.append(Statement)
			if len(Statements)!=0: ADict={"Condition":Cond, "Statements":Statements}
	
	#		logging.info("Assign '{0}' to '{1}'".format(Assignee, Assignor))
			self._Hierarchy.append(ADict)
			return True
		elif isinstance(Assignee, dict): # For case statements
			Statements=[]
			Statements.append({"Assignee":Assignee, "Assignor":None, "Comments":""})
			#CaseDict={"Name": CurrentState.GetName(), "Assignments":FSMAssignment, "Comments":"Assignments for FSM FuturState"}
			ADict={"Condition":None, "Statements":Statements}
	
	#		logging.info("Assign '{0}' to '{1}'".format(Assignee, Assignor))
			self._Hierarchy.append(ADict)
			return True
		elif hasattr(Assignee, 'GenericSize'):
			self._AssignedSignals.append(Assignee)
			self._AssignorSignals[Assignee]=Assignor
		else:
			logging.debug("[AssignmentStatement:Add] Assignee:{0}".format(Assignee))
			logging.error("[AssignmentStatement:Add] Assignee must be an 'AssignmentStatement' or a 'Signal' object not '{0}'.".format(type(Assignee)))
			raise TypeError
			return False
		Statement={"Assignee":Assignee, "Assignor":Assignor, "Comments":""}
		if not (Cond is None):
			for D in self._Hierarchy:
				if D["Condition"]==Cond: 
					D["Statements"].append(Statement)
					return True
		ADict={"Condition":Cond, "Statements":[Statement,]}
		
#		logging.info("Assign '{0}' to '{1}'".format(Assignee, Assignor))
		self._Hierarchy.append(ADict)
		return True
	#-------------------------------------------------
	def __getitem__(self, Index):
		"""
		Called to implement evaluation of AssignmentStatement[key] => return Statements
		Index = integers or Condition objects
		"""
		if isinstance(Index, Condition):
			for C, D in self._Hierarchy.items():
				if C==Index: return D
		elif isinstance(Index, int):
			logging.error("[AssignmentStatement:getitem] Index must be an integer.")
			return None
		elif Index<len(self._Hierarchy):
			logging.error("[AssignmentStatement:getitem] Index too high. Should be less than '{0}'.".format(len(self._Hierarchy)))
			return None
		ADict=self._Hierarchy[Index]
		Statements=ADict["Statements"]
		return Statements
		
	#-------------------------------------------------
	def __iter__(self):
		"""
		Iterator for looping over hierarchy sequence.
		"""
#		logging.error("Signal operator '{0}' not available yet.".format(inspect.stack()[0][3]))
		for ADict in self._Hierarchy:
			yield ADict["Condition"], ADict["Statements"]
	#-------------------------
	def Remove(self, Index=-1):
		"""
		Remove assignment item from hierarchy.
		"""
		if isinstance(Index, Condition):
			for i, D in enumerate(self._Hierarchy):
				if D["Condition"]==Index: 
					self._Hierarchy.pop(i)
					return True
		elif isinstance(Index, int):
			logging.error("[AssignmentStatement:Remove] Index must be an integer.")
			return False
		elif Index<len(self._Hierarchy):
			logging.error("[AssignmentStatement:Remove] Index too high. Should be less than '{0}'.".format(len(self._Hierarchy)))
			return False
		self._Hierarchy.pop(Index) # List of pair condition/AssignmentStatement
		return True
	#-------------------------
	def Pop(self, Index=0):
		"""
		Remove assignment item from hierarchy.
		"""
		if isinstance(Index, int):
			logging.error("[AssignmentStatement:Pop] Index must be an integer.")
			return False
		elif Index<len(self._Hierarchy):
			logging.error("[AssignmentStatement:Pop] Index too high. Must be less than {0}.".format(len(self._Hierarchy)))
			return False
		return self._Hierarchy.pop(Index) # List of pair condition/AssignmentStatement
	#-------------------------
	def GetAssignedSignals(self):
		"""
		Return list of assigned signals.
		"""
		return self._AssignedSignals
	#-------------------------
	def GetAssignorSignal(self, Assignee):
		"""
		Return list of assigned signals.
		"""
		if Assignee in self._AssignorSignals:
			return self._AssignorSignals[Assignee]
	#-------------------------
	def Desc(self):
		"""
		Return Description.
		"""
		return self.Description
	#-------------------------
	def __repr__(self):
		"""
		Return string representation of assignment.
		"""
		return "\n\t<AssignmentStatement>{\n\t"+"\n\t".join(["{0}[{1}]".format(x["Condition"], x["Statements"]) for x in self._Hierarchy])+'}'
	
	#-------------------------
	def __str__(self):
		"""
		Return string representation of assignment.
		"""
		return "<AssignmentStatement>{\n"+"\n".join(["{0}[{1}]".format(x["Condition"], x["Statements"]) for x in self._Hierarchy])+'}'
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

