

import os
from glob import glob

import examscan.tmp

def clear():
	for extension in examscan.tmp.EXTENSIONS:
		for file_path in glob(examscan.tmp.DIR + '/*.' + extension):
			os.remove(file_path)

def main():
	for extension in examscan.tmp.EXTENSIONS:
		print([os.path.basename(file_path) for file_path in glob(examscan.tmp.DIR + '/*.' + extension)])

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Manage tmp directory')
	parser.add_argument('--clear', action='store_true', help='clear tmp directory')
	args = parser.parse_args()
	
	if args.clear:
		clear()
	else:
		main()

