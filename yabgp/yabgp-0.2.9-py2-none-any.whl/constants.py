# Copyright 2015-2017 Cisco Systems, Inc.
# All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# some handy things to know
BGP_MAX_PACKET_SIZE = 4096
BGP_MARKER_SIZE = 16  # size of BGP marker
BGP_HEADER_SIZE = 19  # size of BGP header, including marker
BGP_MIN_OPEN_MSG_SIZE = 29
BGP_MIN_UPDATE_MSG_SIZE = 23
BGP_MIN_NOTIFICATION_MSG_SIZE = 21
BGP_MIN_KEEPALVE_MSG_SIZE = BGP_HEADER_SIZE
BGP_TCP_PORT = 179
BGP_ROUTE_DISTINGUISHER_SIZE = 8

# BGP FSM State
ST_IDLE = 1
ST_CONNECT = 2
ST_ACTIVE = 3
ST_OPENSENT = 4
ST_OPENCONFIRM = 5
ST_ESTABLISHED = 6

# BGP Timer (seconds)
DELAY_OPEN_TIME = 10
ROUTE_REFRESH_TIME = 10
LARGER_HOLD_TIME = 4 * 60
CONNECT_RETRY_TIME = 30
IDLEHOLD_TIME = 30
HOLD_TIME = 120

stateDescr = {
    ST_IDLE: "IDLE",
    ST_CONNECT: "CONNECT",
    ST_ACTIVE: "ACTIVE",
    ST_OPENSENT: "OPENSENT",
    ST_OPENCONFIRM: "OPENCONFIRM",
    ST_ESTABLISHED: "ESTABLISHED"
}

# tcp
TCP_MD5SIG_MAXKEYLEN = 80
SS_PADSIZE_IPV4 = 120
TCP_MD5SIG = 14
SS_PADSIZE_IPV6 = 100
SIN6_FLOWINFO = 0
SIN6_SCOPE_ID = 0

# BGP message types
BGP_OPEN = 1
BGP_UPDATE = 2
BGP_NOTIFICATION = 3
BGP_KEEPALIVE = 4
BGP_ROUTE_REFRESH = 5
BGP_CAPABILITY = 6
BGP_ROUTE_REFRESH_CISCO = 0x80

AFI_SAFI_DICT = {
    (1, 1): 'ipv4',
    (2, 1): 'ipv6',
    (1, 4): 'ipv4_lu',
    (2, 4): 'ipv6_lu',
    (1, 133): 'flowspec',
    (1, 128): 'vpnv4',
    (2, 128): 'vpnv6',
    (25, 70): 'evpn',
    (16388, 71): 'bgpls'
}
AFI_SAFI_STR_DICT = {
    'ipv6': (2, 1),
    'ipv4': (1, 1),
    'ipv4_lu': (1, 4),
    'ipv6_lu': (2, 4),
    'flowspec': (1, 133),
    'vpnv4': (1, 128),
    'vpnv6': (2, 128),
    'evpn': (25, 70),
    'bgpls': (16388, 71)
}

# Notification error codes
ERR_MSG_HDR = 1
ERR_MSG_OPEN = 2
ERR_MSG_UPDATE = 3
ERR_HOLD_TIMER_EXPIRED = 4
ERR_FSM = 5
ERR_CEASE = 6
ERR_CAP = 7
