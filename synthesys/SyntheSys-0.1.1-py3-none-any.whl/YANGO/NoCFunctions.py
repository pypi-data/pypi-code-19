
import sys, os, logging, re

#======================================================================
def GenHeader(TargetPosition, FlitWidth, DataID=0):
	"""
	Build a packet header according to target position.
	return value is a integer.
	"""
	# Second half of the Header
	if TargetPosition is None:
		logging.warning("Null target position specified for header generation : generated address (0,0).") 
		return 0
	else:
		try: 
			if isinstance(TargetPosition, tuple): x, y = TargetPosition
			elif isinstance(TargetPosition, str): x, y = [int(x) for x in TargetPosition.split(':')]
			else: raise TypeError
		except: 
			logging.error("Wrong format for target position while generating header (unreadable '{0}').".format(TargetPosition))
			return 0
		DataIDTemplate = "{0:"+"0{0}".format(int(int(FlitWidth)/2))+"b}"
		Head = DataIDTemplate.format(DataID)
		TailTemplate = "{0:"+"0{0}".format(int(int(FlitWidth)/4))+"b}"+"{1:"+"0{0}".format(int(int(FlitWidth)/4))+"b}"
		Tail = TailTemplate.format(x, y)
		Header=Head+Tail
		return int(Header, 2)
#======================================================================
	
	
	
	
	
	
	
	
	
	

