from os import stat, remove

def fileage(trgfile):
	timefile = '/tmp/thetime'
	trgtime = stat(trgfile).st_mtime
	with open(timefile, 'w+'):
		thetime = stat(timefile).st_mtime
	remove(timefile)
	return int(str(((thetime-trgtime))).split('.')[0])

