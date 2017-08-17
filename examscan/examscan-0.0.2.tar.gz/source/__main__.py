
''' A simple starting point for examscan. '''

import examscan

def main():
	''' Describe how to start examscan. '''
	
	print('examscan %s' % examscan.__version__)
	print('Get started by using:')
	print(' > python -m examscan.doc                 # To open documentation.')
	print(' > python -m examscan.demo                # To copy demo examples here.')
	print(' > python -m examscan.tag [options]       # To tag an exam.')
	print(' > python -m examscan.scan [options]      # To analyse some scans.')

if __name__ == '__main__':
	main()

