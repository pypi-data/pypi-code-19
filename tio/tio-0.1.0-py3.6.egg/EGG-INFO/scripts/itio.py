#!/usr/local/opt/python3/bin/python3.6
"""
itio: Interactive Twinleaf I/O 
License: MIT
Author: Thomas Kornack <kornack@twinleaf.com>
"""

import tldevice
device = tldevice.Device("tcp://localhost")
device._interact()
