#!/usr/bin/env python3

import os, sys, argparse, logging, uuid, socket
from .ssdp import SSDPServer
from bottle import route, request, response, default_app, view, template

@route('/berryinfo.xml')
def xml_berryinfo():
	response.content_type = 'text/xml'
	return "Testing"

@route('/')
def index():
	page = '''
	<!doctype html>
	<head>
	<title>berryinfo: Welcome</title>
	</head>
	<body>
		<h1>Welcome to your Raspberry Pi</h1>
		<p>
			<strong>IP:&nbsp;</strong>{{ip}}<br />
			<strong>Hostname&nbsp</strong>{{hostname}}
		</p>
	</body>
	</html>
	'''

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		lan_address = s.getsockname()[0]
		hostname = socket.gethostname()
	except:
		lan_address = '127.0.0.1'
		hostname = 'raspberrypi'
		pass

	return template(page, ip=lan_address, hostname=hostname)

def main():

	parser = argparse.ArgumentParser()

	# General configuration
	parser.add_argument("--host", "-i", default=os.getenv('IP', '127.0.0.1'), help="IP to listen on")
	parser.add_argument("--port", "-p", default=os.getenv('PORT', 5000), help="port to listen on")

	# Verbose mode
	parser.add_argument("--verbose", "-v", help="increase output verbosity", action="store_true")
	args = parser.parse_args()

	if args.verbose:
		logging.basicConfig(level=logging.DEBUG)
	else:
		logging.basicConfig(level=logging.INFO)
	log = logging.getLogger(__name__)

	ssdp = SSDPServer()
	ssdp.register('local',
	              'uuid:{}::upnp:rootdevice'.format(uuid.uuid4()),
	              'upnp:rootdevice',
	              'http://{}:5000/berryinfo.xml'.format('127.0.0.1'))
	try:
		app = default_app()
		ssdp.start()
		app.run(host=args.host, port=args.port, server='tornado')
	except:
		log.error("Unable to start server on {}:{}".format(args.host, args.port))

if __name__ == '__main__':
	main()