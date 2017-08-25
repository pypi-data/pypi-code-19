#!/usr/bin/env python3
from re import search

from socket import getfqdn

from netaddr import IPNetwork, IPAddress

def addrmask(address, netmask):
	ip = IPNetwork(str(address)+'/'+str(netmask))
	return str(ip.network), str(ip.prefixlen)

def netips(network):
	ips = []
	for ip in IPNetwork(network):
		ips.append(str(ip))
	if ips != []:
		return ips

def iternet(netaddr, mode=None, verbose=None):
	for ip in netips(netaddr):
		host = getfqdn(ip)
		if mode == 'both':
			ipdns = ip, None
			if host != ip:
				ipdns = ip, host
		elif mode == 'block':
			if host != ip:
				ipdns = ip, host
			else:
				continue
		elif mode == 'avail':
			if host == ip:
				ipdns = ip, None
			else:
				continue
		yield ipdns

def gateway(network=None, ipv4=True, ipv6=False):
	nets = []
	if network:
		ip = IPNetwork(network)
		nets.append(ip.network)
	else:
		for iface in ifaces():
			if iface == 'lo':
				continue
			addrs = ifaddrs(iface, ipv4=ipv4, ipv6=ipv6)
			if not addrs:
				continue
			for ipv in addrs:
				net = '%s/%s' %(addrs[ipv]['addr'], addrs[ipv]['netmask'])
				ip = IPNetwork(net)
				if ip.network:
					nets.append(str(ip.network))
	gates = []
	for net in nets:
		net, last = str(net).split('.')[:-1], str(net).split('.')[-1]
		last = int(last)+1
		if not network or not '/' in network:
			last = 1
		net.append(last)
		gates.append('.'.join(str(n) for n in net))
	return gates


def isip(pattern):
	# return True if "pattern" is RFC conform IP otherwise False
	iplike = r'^(?!0+\.0+\.0+\.0+|255\.255\.255\.255)' \
        r'(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)' \
        r'\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
	if search(iplike, pattern):
		return True
	return False
