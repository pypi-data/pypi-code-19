import wissen
from wissen import binfile
from aquests.lib import logger
import os, codecs, glob, json

resource_dir = None

def add_document (indexer, doc):
	document = wissen.document ()
	document.set_content (doc ['document'])
	if 'snippet' in doc:
		document.set_auto_snippet (doc ['snippet'])
	for name, opt in doc ['fields'].items ():
		if name == "_id":			
			data = str (opt)
			lang = 'un'
			ftype = wissen.STRING
		else:	
			data = opt.get ('data')
			lang = opt.get ('lang', 'un')
			ftype = opt.get ('type')
			if not ftype:
				raise TypeError ('Type of field is required')
		document.add_field (name, data, ftype, lang)
	indexer.add_document (document)

def getdir (*d):
	global resource_dir	
	return os.path.join (resource_dir, *d)
	
def index (path):	
	global log
	
	alias = os.path.split (path) [-1]
	with codecs.open (path, "r", "utf8") as f:
		colopt = json.loads (f.read ())
	
	colopt ['data_dir'] = [getdir ('models', os.path.normpath(d)) for d in colopt ['data_dir']]
	queue_dir = colopt ['data_dir']
	if type (queue_dir) is list:
		queue_dir = queue_dir [0]
	
	queues = [(q, os.path.getmtime (q)) for q in glob.glob (os.path.join (queue_dir, 'que.*')) if not q.endswith (".lock")]
	if not queues:
		log ("[info] nothing to for %s in %s" % (os.path.split (path) [-1], os.path.dirname (path)))
		return
		
	queues.sort (key = lambda x: x [-1])
	deleteables = []
	
	analyzer = wissen.standard_analyzer (3000, 1, **colopt ['analyzer'])
	col = wissen.collection (
	  indexdir = colopt ['data_dir'],
	  mode = wissen.APPEND,
	  analyzer = analyzer
	)
	for qfile, mtime in queues:		
		bf = binfile.BinFile (qfile, "r")
		while 1:
			try: cmd = bf.readVInt ()				
			except OSError:
				bf.close ()
				break
			doc = json.loads (bf.readZBytes ().decode ("utf8"))
			if cmd in (1, 2):
				qs = doc.get ("query")
				if not qs:
					qs = '_id:"%s"' % doc ['fields']['_id']
				deleteables.append (qs)
	
	if deleteables:
		colopt ['searcher']['remove_segment'] = 0
		searcher = col.get_searcher (**colopt ['searcher'])
		for qs in deleteables:
			searcher.delete (qs)
		searcher.close ()
	
	indexer = col.get_indexer (**colopt ['indexer'])
	for qfile, mtime in queues:		
		bf = binfile.BinFile (qfile, "r")
		while 1:
			try: cmd = bf.readVInt ()				
			except OSError:
				bf.close ()
				break
			if cmd == 2:	 # just delete
				continue
			doc = json.loads (bf.readZBytes ().decode ("utf8"))
			add_document (indexer, doc)
	indexer.close (optimize = len (deleteables))
	
	for qfile, mtime in queues:
		os.remove (qfile)
			
if __name__ == "__main__":
	log = logger.screen_logger ()
	wissen.configure (1, log)
	
	try:
		resource_dir = sys.argv [1]
	except IndexError:
		print ('Usage: mirror.py resource_dir')	
		print ('  ex. mirror.py /var/tmp/wisen')	
		sys.exit ()
		
	conf_dir = os.path.join (resource_dir, "models", "_config")
	for alias in os.listdir (conf_dir):
		log ("[info] starting index for %s" % alias)
		index (os.path.join (conf_dir, alias))
		log ("[info] index done for %s" % alias)
		