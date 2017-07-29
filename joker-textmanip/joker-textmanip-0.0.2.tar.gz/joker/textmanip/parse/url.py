#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import base64
import collections

from joker.cast import namedtuple_to_dict
from six import moves as six_moves


urllib = six_moves.urllib


def validate_ipv4_address(address):
    import socket
    # http://stackoverflow.com/a/4017219/2925169
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False
    return True


def validate_ipv6_address(address):
    import socket
    # http://stackoverflow.com/a/4017219/2925169
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    return True


class URLMutable(object):
    def __init__(self, url):
        p = urllib.parse.urlparse(url)
        self._components = namedtuple_to_dict(p)
        self._query = collections.OrderedDict()
        self._update_query()

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = collections.OrderedDict(value)

    def _update_compoent(self):
        qs = urllib.parse.urlencode(self._query)
        self._components['query'] = qs

    def _update_query(self):
        q = urllib.parse.parse_qsl(self._components['query'])
        self._query = collections.OrderedDict(q)

    def __getitem__(self, key):
        self._update_compoent()
        return self._components[key]

    def __setitem__(self, key, value):
        if key not in self._components:
            raise KeyError('invalid URL component "{}"'.format(key))
        self._components[key] = value
        if key == 'query':
            self._update_query()

    def __str__(self):
        self._update_compoent()
        return urllib.parse.urlunparse(self._components.values())

    def __repr__(self):
        cn = self.__class__.__name__
        return '{}({})'.format(cn, repr(str(self)))

    def embed_link(self, key, guest_url, func=None):
        """
        :param guest_url:
        :param key:
        :param func: process resulting base64 string with this func
        :return: a LinkMutable instance
        """
        # firstly, remove that key in guest_url!
        guest_mutlink = URLMutable(guest_url)
        guest_mutlink.query.pop(key, 0)
        guest = base64.urlsafe_b64encode(str(guest_mutlink).encode('utf-8'))
        guest = guest.decode('utf-8')
        guest = guest.replace('=', '').strip()
        if func:
            guest = func(guest)
        self.query[key] = guest

    def unembed_link(self, key, func=None, remove=True):
        em = self.query.get(key, '')
        if func:
            em = func(em)
        em += '=' * ((4 - len(em) % 4) % 4)
        em = em.encode('ascii')
        try:
            url = base64.urlsafe_b64decode(em).decode('utf-8')
        except:
            return ''
        if remove:
            self.query.pop(key, '')
        return url


LinkMutable = URLMutable
