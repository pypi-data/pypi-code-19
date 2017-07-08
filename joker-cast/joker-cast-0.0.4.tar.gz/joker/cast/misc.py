#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import socket


def validate_ipv4_address(address):
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
    # http://stackoverflow.com/a/4017219/2925169
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    return True
