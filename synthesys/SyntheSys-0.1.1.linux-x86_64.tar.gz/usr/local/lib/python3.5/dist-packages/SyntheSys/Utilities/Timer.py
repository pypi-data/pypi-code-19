
from timeit import default_timer
from datetime import datetime
#import arrow

#==================================================================
class Timer():
 	#----------------------------------------------------------
	def __init__(self, verbose=False):
		self.verbose = verbose
		self.timer = default_timer
 	#----------------------------------------------------------
	def __enter__(self):
		self.start = self.timer()
		return self
 	#----------------------------------------------------------
	def __exit__(self, *args):
		end = self.timer()
		self.elapsed_secs = end - self.start
		self.elapsed = self.elapsed_secs * 1000 # millisecs
		if self.verbose:
			print('elapsed time: %f ms'%self.elapsed)

#==================================================================
def TimeStamp(Format='%Y-%m-%d_%Hh%Mm%Ss'):
	return datetime.now().strftime(Format)

#def TimeStamp(Format='YYYY-MM-DD_HH-mm-ss'):
#	return arrow.utcnow().format(Format)
#==================================================================


import time
#==================================================================
class ProcessTimer():
 	#----------------------------------------------------------
	def __init__(self, verbose=False):
		self.StartTime = 0
		self.EndTime   = 0
 	#----------------------------------------------------------
	def __enter__(self):
		try: self.StartTime = time.process_time()
		except: self.StartTime = time.clock()
		return self
 	#----------------------------------------------------------
	def __exit__(self, *args):
		try: self.EndTime = time.process_time()
		except: self.EndTime = time.clock()
 	#----------------------------------------------------------
	def ExecTimeString(self):
		Delta = self.EndTime - self.StartTime
		h         = int(Delta/3600)
		m         = int((Delta-h*3600)/60)
		s         = int((Delta-h*3600-m*60))
		millisecs = int((Delta-h*3600-m*60-s)*1000)
		microsec  = int((Delta-h*3600-m*60-s-millisecs/1000)*1000000)
		return '{0}h {1}min {2}s {3}ms {4}µs'.format(h,m,s, millisecs, microsec)
	
	
