#!/usr/bin/env python3

import os, sys, argparse, logging, uuid, socket
from .ssdp import SSDPServer
from bottle import route, request, response, default_app, view, template

@route('/berryinfo.xml')
def xml_berryinfo():
	xml = """
	<root>
    <specVersion>
        <major>1</major>
        <minor>0</minor>
    </specVersion>
    <device>
        <deviceType>urn:schemas-upnp-org:device:Basic:1</deviceType>
        <friendlyName>Raspberry Pi ({})</friendlyName>
        <manufacturer>Raspberry Pi</manufacturer>
        <manufacturerURL>https://www.raspberrypi.org</manufacturerURL>
        <modelDescription>Raspberry Pi</modelDescription>
        <modelName>Raspberry Pi</modelName>
        <modelNumber>3</modelNumber>
        <modelURL>https://www.raspberrypi.org</modelURL>
        <serialNumber>raspberrypi-{}</serialNumber>
        <UDN>{}</UDN>
        <presentationURL>http://{}:{}</presentationURL>
    </device>
	</root>
	""".format(hostname, hostname.lower(), device_uuid, lan_address, args.port)
	response.content_type = 'application/xml'
	return xml

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

	return template(page, ip=lan_address, hostname=hostname)

def main():

	global args, device_uuid, lan_address, hostname

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

	device_uuid = uuid.uuid4()

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		lan_address = s.getsockname()[0]
		hostname = socket.gethostname()
	except:
		lan_address = '127.0.0.1'
		hostname = 'raspberrypi'
		pass

	ssdp = SSDPServer()
	ssdp.register('local',
	              'uuid:{}::upnp:rootdevice'.format(device_uuid),
	              'upnp:rootdevice',
	              'http://{}:{}/berryinfo.xml'.format(lan_address, args.port))
	try:
		app = default_app()
		ssdp.daemon = True
		ssdp.start()
		app.run(host=args.host, port=args.port, server='tornado')
	except KeyboardInterrupt:
		ssdp.shutdown()
	except:
		log.error("Unable to start server on {}:{}".format(args.host, args.port))

if __name__ == '__main__':
	main()