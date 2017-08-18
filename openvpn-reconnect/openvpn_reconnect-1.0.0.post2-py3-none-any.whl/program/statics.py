# encoding:UTF-8

import os


class Statics:
    HOST = None
    INTERFACE = None
    PACKETS = None
    PID_FOLDER = os.path.join('/', 'tmp', '.openvpn_reconnect')
    PID_FILE = os.path.join(PID_FOLDER, 'pid.txt')
    SECONDS = None
