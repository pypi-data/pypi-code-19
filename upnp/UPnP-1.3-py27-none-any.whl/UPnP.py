# -*- coding: utf-8 -*-
#################################################
#                                               #
#   Code by: NinuX                              #
#   Start edit: 01/6/17                         #
#   Last edit: 14/7/17                          #
#                                               #
#  Telegram me: NinuuX                          #
#                                               #
#   UPnP-Lib - UPnP_start.py                    #
#################################################

import gevent
from gevent import socket
from gevent import monkey
from ipgetter import myip
import re, urllib, urllib2, httplib
from urlparse import urlparse
from xml.dom.minidom import parseString

monkey.patch_socket()
remove_whitespace = re.compile(r'>\s*<')


def _m_search_ssdp():
    search_target = "urn:schemas-upnp-org:device:InternetGatewayDevice:1"

    ssdp_request = ''.join(['M-SEARCH * HTTP/1.1\r\n','HOST: 239.255.255.250:1900\r\n','MAN: "ssdp:discover"\r\n','MX: 2\r\n','ST: {0}\r\n'.format(search_target),'\r\n'])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(ssdp_request, ('239.255.255.250', 1900))
    sock.settimeout(2)
    try:
        data = sock.recv(2048)
    except socket.error:
        print "[\033[91mERROR\033[0m] Try to reboot your Router"

    return data

def _retrieve_location_from_ssdp(response):
    parsed = re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n', response)
    location_header = filter(lambda x: x[0].lower() == 'location', parsed)

    if not len(location_header):
        return False

    return urlparse(location_header[0][1])


def _retrieve_igd_profile(url):
    return urllib2.urlopen(url.geturl()).read()


def _node_val(node):
    return node.childNodes[0].data


def _parse_igd_profile(profile_xml):
    dom = parseString(profile_xml)

    service_types = dom.getElementsByTagName('serviceType')
    for service in service_types:
        if _node_val(service).find('WANIPConnection') > 0 or _node_val(service).find('WANPPPConnection') > 0:
            control_url = service.parentNode.getElementsByTagName('controlURL')[0].childNodes[0].data
            upnp_schema = _node_val(service).split(':')[-2]
            return control_url, upnp_schema

    return False


def _get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('239.255.255.250', 1))
    return s.getsockname()[0]


def _create_soap_message(port, description="UPnPPunch", protocol="TCP",upnp_schema='WANIPConnection'):
    current_ip = _get_local_ip()
    soap_message = """<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:AddPortMapping xmlns:u="urn:schemas-upnp-org:service:{upnp_schema}:1"><NewRemoteHost></NewRemoteHost><NewExternalPort>{port}</NewExternalPort><NewProtocol>{protocol}</NewProtocol><NewInternalPort>{port}</NewInternalPort><NewInternalClient>{host_ip}</NewInternalClient><NewEnabled>1</NewEnabled><NewPortMappingDescription>{description}</NewPortMappingDescription><NewLeaseDuration>0</NewLeaseDuration></u:AddPortMapping></s:Body></s:Envelope>""".format(port=port, protocol=protocol, host_ip=current_ip, description=description, upnp_schema=upnp_schema)
    return remove_whitespace.sub('><', soap_message)


def _parse_for_errors(soap_response):
    if soap_response.status == 500:
        err_dom = parseString(soap_response.read())
        err_code = _node_val(err_dom.getElementsByTagName('errorCode')[0])
        err_msg = _node_val(err_dom.getElementsByTagName('errorDescription')[0])
        raise Exception('SOAP request error: {0} - {1}'.format(err_code, err_msg))
        return False
    else:
        return True


def _send_soap_request(location, upnp_schema, control_url, soap_message):
    headers = {'SOAPAction': ('"urn:schemas-upnp-org:service:{schema}:''1#AddPortMapping"'.format(schema=upnp_schema)),'Content-Type': 'text/xml'}
    conn = httplib.HTTPConnection(location.hostname, location.port)
    conn.request('POST', control_url, soap_message, headers)

    response = conn.getresponse()
    conn.close()

    return _parse_for_errors(response)


def show_IP():
    try:
        return myip()
    except:
        print "[\033[91mERROR\033[0m]Something went wrong..\n[\33[94m*\033[0m]lz Try again"


def port2forward(port=4444, desc="Deploy by UPnP-Lib"):
    if port < 1024:
        print "[\033[91mERROR\033[0m] The router does not allow to open port that under 1024\n[\33[94m*\033[0m] Plz enter a higher port!"
        return -1

    location = _retrieve_location_from_ssdp(_m_search_ssdp())
    if not location:
        print "[\033[91mERROR\033[0m] Something went wrong..\n[\33[94m*\033[0m]Plz Try again"
        return False

    parsed = _parse_igd_profile(_retrieve_igd_profile(location))

    if not parsed:
        return False

    control_url, upnp_schema = parsed

    soap_messages = [_create_soap_message(port, desc, proto, upnp_schema) for proto in ['TCP', 'UDP']]

    requests = [gevent.spawn(_send_soap_request, location, upnp_schema, control_url, message) for message in soap_messages]
    gevent.joinall(requests, timeout=4)
    if all(requests):
        print "[\033[1;32mOK\033[0m] %d is forward to %s"%(port, str(_get_local_ip()))
        return True
    else:
        print "[\033[1;32mOK\033[0m] %d is forward to %s"%(port, str(_get_local_ip()))
        return False

#pass to port2open as a prameter the Port and the name you want
