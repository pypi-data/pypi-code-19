
import logging
import inspect

##==================================================================
#def GetCallingMethod():
#	"""
#	Use inspect to fetch calling method of the caller name.
#	"""
##	return inspect.getouterframes(inspect.currentframe())[2][3]
#	caller = inspect.getouterframes(inspect.currentframe())[2][1].f_back
#	func_name = inspect.getframeinfo(caller)[2]
#	caller = caller.f_back
##	from pprint import pprint
#	return caller.f_locals.get(func_name, caller.f_globals.get(func_name))
#	
##==================================================================

#==================================================================
def GetCallingMethod():
	"""
	Use inspect to fetch calling method of the caller name.
	"""
	OuterFrameNb=3
	frame,filename,line_number,function_name,lines,index=inspect.getouterframes(inspect.currentframe())[OuterFrameNb]
	while filename.endswith("DataSignal.py"):
		frame,filename,line_number,function_name,lines,index=inspect.getouterframes(frame)[1]
		
	return frame.f_locals.get(function_name, frame.f_globals.get(function_name))

			
#===================================================================
def GetInstanceName(Module):
	"""
	return Name of module instance
	"""
	import inspect
	frame,filename,line_number,function_name,lines,index=inspect.getouterframes(inspect.currentframe())[2]
	tmp = frame.f_globals.copy()
	tmp.update(frame.f_locals.items())
	for k, var in tmp.items():
		if isinstance(var, Module.__class__):
			if hash(Module) == hash(var):
				Module.__name__=k
				return Module.__name__
	
	
#===================================================================
























