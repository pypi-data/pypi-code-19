#-*- coding: utf-8 -*-
import sys

if sys.version_info[0] == 2:
    import ipaddr as ipaddress
else:
    import ipaddress
import os

from .utils import get_client_ip

# Init, load ip addresses list
MODULE_ROOT = os.path.abspath(os.path.dirname(__file__))

_megafon_url = "http://moblave.com/op_ip.php?op=megafon"
_mts_url = "http://moblave.com/op_ip.php?op=mts"
_beeline_url = "http://moblave.com/op_ip.php?op=beeline"
# FIXME: Load IP's from moblave urls


m = open(os.path.join(MODULE_ROOT, 'data/megafon.txt'))
MEGAFON = m.read().strip().replace("\n", " ")
m.close()

m = open(os.path.join(MODULE_ROOT, 'data/beeline.txt'))
BEELINE = m.read().strip().replace("\n", " ")
m.close()

m = open(os.path.join(MODULE_ROOT, 'data/mts.txt'))
MTS = m.read().strip().replace("\n", " ")
m.close()

m = open(os.path.join(MODULE_ROOT, 'data/azer.txt'))
AZER = m.read().strip().replace("\n", " ")
m.close()

m = open(os.path.join(MODULE_ROOT, 'data/tele2.txt'))
TELE2 = m.read().strip().replace("\n", " ")
m.close()

m = open(os.path.join(MODULE_ROOT, 'data/kiev.txt'))
KIEV = m.read().strip().replace("\n", " ")
m.close()

BEELINE = BEELINE.split(' ')
MEGAFON = MEGAFON.split(' ')
MTS = MTS.split(' ')
AZER = AZER.split(' ')
TELE2 = TELE2.split(' ')
KIEV = KIEV.split(' ')


def is_mobile(request):
    """Check if ip addrees belong to beeline, mts or megafon
    provider
    return:
    0 - Ip address does not belongs to any mobile provider
    1 - megafon
    2 - beeline
    3 - mts
    4 - azercell
    5 - tele2
    """

    def ip_belongs_to_net(ip, nets):
        """Check if ip address belongs to network"""
        for n in nets:
            try:
                net = ipaddress.IPNetwork(n)
            except ValueError:
                pass
            else:
                if ip in net:
                    return True
        return False

    ip = get_client_ip(request)
    if ip:
        if ip_belongs_to_net(ip, MEGAFON):
            return 1
        elif ip_belongs_to_net(ip, BEELINE):
            return 2
        elif ip_belongs_to_net(ip, MTS):
            return 3
        elif ip_belongs_to_net(ip, AZER):
            return 4
        elif ip_belongs_to_net(ip, TELE2):
            return 5
        elif ip_belongs_to_net(ip, KIEV):
            return 6
    return 0
