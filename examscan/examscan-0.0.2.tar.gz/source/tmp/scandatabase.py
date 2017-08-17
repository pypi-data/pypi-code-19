

import os
import glob
import uuid
import shutil
import filecmp
import hashlib
from itertools import groupby

import examscan.tmp

def md5_hash(file_path):
	with open(file_path, 'rb') as input_file:
		return hashlib.md5(input_file.read()).hexdigest()

class ScanDatabase(object):
	def __init__(self, directory=None):
		self.directory = examscan.tmp.DIR if directory is None else directory
		self.load()
	
	def load(self):
		if not os.path.exists(self.directory): os.makedirs(self.directory)
		
		self.file_paths_dict = dict((x, list(y)) for x, y in groupby(sorted(glob.glob(self.directory + '/*.scan')), key=lambda fp: os.path.basename(fp)[:32]))
	
	def add(self, file_path):
		file_name = os.path.basename(file_path)
		file_path_hash = md5_hash(file_path)
		new_file_name = '%s-%s-%s.scan' % (file_path_hash, str(uuid.uuid4())[:8], file_name)
		new_file_path = os.path.join(self.directory, new_file_name)
		
		if file_path_hash in self.file_paths_dict:
			for potential_match in self.file_paths_dict[file_path_hash]:
				if filecmp.cmp(file_path, potential_match):
					return potential_match
			
			self.file_paths_dict[file_path_hash].append(new_file_name)
		else:
			self.file_paths_dict[file_path_hash] = [new_file_name]
		
		shutil.copy(file_path, new_file_path)
		return new_file_path

