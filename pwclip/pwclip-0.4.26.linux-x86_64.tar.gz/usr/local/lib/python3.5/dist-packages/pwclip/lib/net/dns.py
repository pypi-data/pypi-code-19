#!/usr/bin/env python3

try:
	from os import uname
except ImportError:
	from os import environ
	uname = ['', environ['COMPUTERNAME']]

from socket import getfqdn, gethostbyaddr, gaierror, herror

from net.addr import isip

def fqdn(name):
	fqdn = getfqdn(name) if name else uname()[1]
	if fqdn:
		return fqdn
	return name

def askdns(host):
	try:
		dnsinfo = gethostbyaddr(host)
	except (gaierror, herror, TypeError) as e:
		return
	if isip(host):
		return dnsinfo[0]
	if len(dnsinfo[2]) == 1:
		return dnsinfo[2][0]
	return dnsinfo[2]

def raflookup(host):
	if host:
		lookup = askdns(host)
		if lookup:
			reverse = askdns(lookup)
			return lookup, reverse
