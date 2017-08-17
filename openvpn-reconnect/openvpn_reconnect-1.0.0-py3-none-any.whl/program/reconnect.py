# encoding:UTF-8

import os
import subprocess


def ping(host: str, interface: str = None, packets: int = 5) -> int:
    """
    Use the ping utility to attempt to reach the host.
    :param host: The host we want to check.
    :param interface: The interface by which we want to send the packets. If we do not indicate any, it will be sent by the one that the program considers the most appropriate.
    :param packets: The number of packets to send.
    :return: The return code from the system ping utility. It's 0 if at least one packet is received.
    """
    command = ['ping', '-c', str(packets), host]
    if interface:
        command.insert(-1, '-I')
        command.insert(-1, interface)
    ret = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, universal_newlines=True)
    return ret.returncode


def restart_openvpn():
    if es_sudo():
        command = ['service', 'openvpn', 'restart']
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, universal_newlines=True)


def es_sudo():
    return os.geteuid() == 0
