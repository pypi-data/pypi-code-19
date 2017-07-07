from wissen import _wissen
from ...util import util
import os

class SegmentNotOpened (Exception): pass

class Segment:
	def __init__ (self, home = None, seg = -1, mode = 'r', plock = None):
		self.numDoc = 0
		
		self.opened = 0
		self.mode = mode
		self.plock = plock		
		self.mutex_id = -1
		
		self.fn_del_modtime = -1
		if seg > -1:
			self.open (home, seg)
		else:
			self.home = home
			self.seg = seg
	
	def has_deleted (self):
		return self.rd is not None
		
	def get_open_flag (self):	
		if self.mode in ("r", "m"):
			fopen_flag = os.O_RDONLY
		else:
			fopen_flag = os.O_WRONLY | os.O_CREAT	
		
		if os.name == "nt":
			fopen_flag |= os.O_BINARY
			
		return fopen_flag
			
	def open (self, home, seg):
		self.home = home
		self.seg = seg
		
		bfn = os.path.join (self.home, str (seg) + ".")		
		fopen_flag = self.get_open_flag ()
					
		fn_tis = bfn + "tis"
		fn_tii = bfn + "tii"
		fn_fdi = bfn + "fdi"
		fn_fda = bfn + "fda"
		fn_tfq = bfn + "tfq"
		fn_prx = bfn + "prx"
		fn_smp = bfn + "smp"
		
		for path in (fn_tis, fn_tii, fn_fdi, fn_fda, fn_tfq, fn_smp):
			self.check_file (path)
		
		self.fs_tis = os.open (fn_tis, fopen_flag)
		self.fs_tii = os.open (fn_tii, fopen_flag)
		self.fs_fdi = os.open (fn_fdi, fopen_flag)
		self.fs_fda = os.open (fn_fda, fopen_flag)
		self.fs_tfq = os.open (fn_tfq, fopen_flag)
		self.fs_prx = os.open (fn_prx, fopen_flag)
		self.fs_smp = os.open (fn_smp, fopen_flag)
		
		bmode = self.mode.encode ("utf8")
		self.ti = _wissen.TermInfo (self.fs_tii, self.fs_tis, bmode)
		self.ti.initialize ()
		
		self.tf = _wissen.Posting (self.fs_tfq, self.fs_prx, bmode)
		self.tf.initialize ()
		
		self.fd = _wissen.Document (self.fs_fdi, self.fs_fda, bmode)		
		self.fd.initialize ()
		
		self.sm = _wissen.SortMap (self.fs_smp, bmode)
		self.sm.initialize ()
		
		self.rd = None
		self.load_deleted ()
				
		self.numDoc = self.si.getSegmentNumDoc (self.seg)
		self.opened = 1		
	
	def get_delfile_modtime (self):
		if self.plock: self.plock.acquire ()		
		try:
			mtime = os.stat (os.path.join (self.home, "%s.del" % self.seg)).st_mtime
		except (IOError, OSError):
			mtime = -1
		if self.plock: self.plock.release ()
		return mtime
	
	def reload_deleted (self):
		# in plock acquired
		new_modtime = self.get_delfile_modtime ()
		if new_modtime == self.fn_del_modtime:				
			return False
			
		if self.rd:
			self.rd.close ()
			self.rd = None
		
		if new_modtime == -1: # .del was deleted
			return True
			
		self.load_deleted ()
		return True
						
	def load_deleted (self):
		fn_del = os.path.join (self.home, "%s.del" % self.seg)
		if not os.path.isfile (fn_del): return			
		if (os.stat (fn_del).st_size > 0):
			if not self.rd:
				self.rd = _wissen.BitVector ()
			
			if self.plock: self.plock.acquire ()			
			try:
				self.rd.fromFile (fn_del)
				#f = open (fn_del, "rb")
				#self.rd.fromFile (f)
				#f.close ()				
				self.fn_del_modtime = self.get_delfile_modtime ()
			finally:
				if self.plock: self.plock.release ()	
	
	def commit_deleted (self):
		if self.plock: self.plock.acquire ()	
		try:
			self.create_bitvector ()
			self.rd.toFile (os.path.join (self.home, "%s.del" % self.seg))
			#f = open (, "wb")
			#self.rd.toFile (f)
			#f.close ()
			self.fn_del_modtime = self.get_delfile_modtime ()
		finally:
			if self.plock: self.plock.release ()
	
	def check_segment (self):
		pass
		
	def create_bitvector (self):
		if self.rd: return
		self.rd = _wissen.BitVector ()
		self.rd.create (self.si.getSegmentNumDoc (self.seg))
	
	def check_file (self, path):
		if self.mode in ("r", "m"):
			assert (os.stat (path).st_size > 0)		
		elif self.mode in ("w",):
			if os.path.isfile (path):
				os.remove (path)
		
	def close (self):		
		if not self.opened: 
			return
		
		if self.mode == "w":
			self.fd.commit ()
			self.sm.commit ()
			self.ti.commit ()
			self.tf.commit ()
			
		self.ti.close ()
		self.tf.close ()	
		self.fd.close ()
		self.sm.close ()		
		
		os.close (self.fs_tis)
		os.close (self.fs_tii)
		os.close (self.fs_fdi)
		os.close (self.fs_fda)
		os.close (self.fs_tfq)
		os.close (self.fs_prx)
		os.close (self.fs_smp)
		
		if self.rd:
			self.rd.close ()
			self.rd = None
			
		self.opened = 0


class DocumentSegment (Segment):
	def open (self, home, seg):
		self.home = home
		self.seg = seg
		
		bfn = os.path.join (self.home, str (seg) + ".")		
		fopen_flag = self.get_open_flag ()
					
		fn_fdi = bfn + "fdi"
		fn_fda = bfn + "fda"
		
		for path in (fn_fdi, fn_fda):
			self.check_file (path)
			
		self.fs_fdi = os.open (fn_fdi, fopen_flag)
		self.fs_fda = os.open (fn_fda, fopen_flag)
		
		self.fd = _wissen.Document (self.fs_fdi, self.fs_fda, self.mode.encode ("utf8"))		
		self.fd.initialize ()
				
		self.opened = 1		
	
	def add_content (self, content, summary = ""):
		self.fd.write (util.serialize (content), summary)
		
	def close (self):
		if not self.opened: 
			return
			
		if self.mode == "w":
			self.fd.commit ()
		self.fd.close ()
		os.close (self.fs_fdi)
		os.close (self.fs_fda)
		
		self.opened = 0
		