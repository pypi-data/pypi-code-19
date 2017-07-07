from wissen import binfile
import os
import shutil
import random
import threading

class DocQueue:
	quename = "que"
	def __init__ (self, si):
		self.si = si
		self.data_dir = self.si.fs.getmaster ()
		self._tlock = threading.RLock ()
		self._plock = self.si.plock # process lock
		self.writer = None
		self.current = None
		
	def __detect_max_seq (self):
		rn = random.randrange (100000, 999999)
		while 1:
			if not os.path.isfile (os.path.join (self.data_dir, "%s.%d.lock" % (self.quename, rn))) and not os.path.isfile (os.path.join (self.data_dir, "%s.%d" % (self.quename, rn))):
				return rn
	
	def __call__ (self, method, doc):
		self.add (method, doc)
	
	def open (self):
		with self._plock:
			self.current = self.__detect_max_seq ()
			self.writer = binfile.BinFile (os.path.join (self.data_dir, "%s.%d.lock" % (self.quename, self.current)), "w")
	
	def close (self, remove = 0):
		if not self.writer: return
		
		self.writer.close ()
		self.writer = None
		if remove:
			os.remove (os.path.join (self.data_dir, "%s.%d.lock" % (self.quename, self.current)))
		else:	
			shutil.move (
				os.path.join (self.data_dir, "%s.%d.lock" % (self.quename, self.current)),
				os.path.join (self.data_dir, "%s.%d" % (self.quename, self.current))
			)						
			
	def rollback (self):
		self.close (1)
	
	def commit (self):
		self.close ()
		
	def add (self, method, doc):
		if self.writer is None:
			self.open ()			
		with self._tlock:
			self.writer.writeVInt (method)
			self.writer.writeZBytes (doc)
