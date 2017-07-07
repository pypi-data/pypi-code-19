import requests
import queue
import os
import wissen
from wissen import filesystem
from pprint import pprint
from wissen.lib import pathtool
from aquests.lib import logger
import threading, time
import socket, json

logger = logger.screen_logger ()
mirror_server = None
DUPLICATE_LOCK = "duplicate-%s" % socket.getfqdn ()
DEBUG = True

def normpath (d):
	d = d.replace ("\\", "/")
	if DEBUG:
		d = d.replace ('D:/apps/', 'd:/var/')
	return d

def download (tque):
	global mirror_server
	
	while 1:
		item = tque.get ()	
		if item is None:
			break
		col, entity, group, fn, savepath	= item
		pathtool.mkdir (os.path.split (savepath)[0])
		url = "%s/%s/%s/%s/%s" % (mirror_server, col, entity, group, fn)		
		surl = "/%s/%s/%s/%s" % (col, entity, group, fn)		
		logger ("downloading from %s" % url)
		with open(savepath, 'wb') as handle:
			response = requests.get(url, stream=True)
			cl = int (response.headers ["Content-Length"])						
			rl = 0
			if not response.ok:
				logger ("download failed %s" % url, 'fail')
			if cl:					
				for block in response.iter_content(1024):
					rl += len (block)
					if rl % 1024000 == 0:
						logger ("%d%% downloaded %s" % (rl/cl * 100, surl))
					handle.write(block)
				if cl:	
					logger ("%d%% downloaded %s" % (rl/cl * 100, surl))	

def remove_end_slash (url):
	while url:
		if url [-1] != "/":
			return url
		url = mirror_server [:-1]	
			
			
def mirror (source, target):
	global mirror_server
	
	mirror_server = remove_end_slash (source)
	local_server = remove_end_slash (target)
	
	r = requests.get ("%s/" % mirror_server)
	for col in r.json () ["collections"]:
		
		requests.get ("%s/%s/locks/%s" % (mirror_server, col, DUPLICATE_LOCK))
		r = requests.get ("%s/%s" % (mirror_server, col))
		status = r.json ()
		valid_segments = [seginfo [0] for seginfo in status ['segmentinfos']]
				
		keep_going = True		
		for name, ctime in status ["locks"]:
			if name == "index":
				keep_going = False
				break
		
		if not keep_going:
			requests.delete ("%s/%s/locks/%s" % (mirror_server, col, DUPLICATE_LOCK))
			continue
		
		for d in status ['indexdirs']:
			pathtool.mkdir (normpath (d))
		
		que = []
		new_file = False
		for group in status ["segmentfiles"]:
			segs = status ["segmentfiles"][group]			
			if 'segments' in segs:
				sfn = segs.pop ('segments')[0]
				dfn = normpath (sfn)
				if group == "primary":
					que.append ((col, 'collection', group, "segments", dfn + ".new"))
				else:
					que.insert (0, (col, 'collection', group, "segments", dfn))
						
			for seg, files in segs.items ():
				if group == "primary" and int (seg) not in valid_segments:
					continue					
				for sfn, ssize, smtime in files:
					dfn = normpath (sfn)
					if not os.path.isfile (dfn):
						que.insert (0, (col, 'segments', group, str(seg) + sfn [-4:], dfn))
						new_file = True
					else:	
						dmtime = os.path.getmtime (dfn)
						dsize = os.path.getsize (dfn)
						if dsize != ssize or smtime > dmtime:
							que.insert (0, (col, 'segments', group, str (seg) + sfn [-4:], dfn))
							new_file = True
		
		if new_file:
			tque = queue.Queue ()		
			for item in que:
				tque.put (item)
			for i in range (2):	
				tque.put (None)		
			
			for i in range (2):
				t = threading.Thread (target = download, args = (tque,))
				t.start ()
			
			while threading.activeCount () > 1:				
				time.sleep (1)
			
			segments = os.path.join (normpath (status ['indexdirs'][0]), 'segments.new')
			if os.path.isfile (segments [:-4]):
				os.remove (segments [:-4])
			os.rename (segments, segments[:-4])	
				
			colopt = status ["colopt"]
			dcolopt = normpath (colopt ['path'])
			if not os.path.isfile (dcolopt) or colopt ["mtime"] > os.path.getmtime (dcolopt) or colopt ["size"] != os.path.getsize (dcolopt):			
				r = requests.post ("%s/%s" % (local_server, col), data = json.dumps (colopt ['data']))
			else:
				r = requests.get ("%s/%s/collection/refresh" % (local_server, col))
		requests.delete ("%s/%s/locks/%s" % (mirror_server, col, DUPLICATE_LOCK))
		

if __name__ == "__main__":
	import sys
		
	try:
		source, target = sys.argv [1]
	except IndexError:
		print ('Usage: mirror.py source target')	
		print ('  ex. mirror.py http://192.168.1.100:5000/v1 http://127.0.0.1:5000/v1')	
		sys.exit ()
	
	mirror (source, target)
	