
import os
import shutil
from glob import glob

DATA_DIR = os.path.dirname(__file__)

FILES = ['exam.pdf', 'rooms.xlsx', 'roster.xlsx', 'scan.pdf', 'settings.conf', 'template.html']

if __name__ == '__main__':
	print('Copying demo files to %s' % os.path.abspath('demo'))
	if not os.path.isdir('demo'): os.mkdir('demo')
	for file_name in FILES:
		shutil.copy(os.path.join(DATA_DIR, file_name), os.path.join('demo', file_name))

