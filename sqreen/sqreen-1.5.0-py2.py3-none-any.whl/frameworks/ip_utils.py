# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Utils functions to retrieve the client user ip
"""

PRIVATE_IP_PREFIX = (
    '0.',  # externally non-routable
    '10.',  # class A private block
    '169.254.',  # link-local block
    '172.16.', '172.17.', '172.18.', '172.19.',
    '172.20.', '172.21.', '172.22.', '172.23.',
    '172.24.', '172.25.', '172.26.', '172.27.',
    '172.28.', '172.29.', '172.30.', '172.31.',  # class B private blocks
    '192.0.2.',  # reserved for documentation and example code
    '192.168.',  # class C private block
    '255.255.255.',  # IPv4 broadcast address
) + (
    '2001:db8:',  # reserved for documentation and example code
    'fc00:',  # IPv6 private block
    'fe80:',  # link-local unicast
    'ff00:',  # IPv6 multicast
)

LOOPBACK_PREFIX = (
    '127.',  # IPv4 loopback device
    '::1',  # IPv6 loopback device
)


NON_PUBLIC_IP_PREFIX = PRIVATE_IP_PREFIX + LOOPBACK_PREFIX


def get_real_user_ip(remote_addr, x_forwarded_for):
    """ Try to compute the real user ip from various headers
    """
    forwarded_ips = [ip.strip() for ip in x_forwarded_for.split(',')]

    # Check every ip from the right to the left, if it's not a known non public
    # ip adress, check the following one. If all proxies have a private ip adress
    # the first address will be either the public IP of the client or a proxy with
    # a public IP
    for ip in forwarded_ips:

        # Ignore invalid ips
        if ip == '':
            continue

        if not ip.startswith(NON_PUBLIC_IP_PREFIX):
            return ip

    return remote_addr
