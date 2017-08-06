# coding=utf-8
"""
this is the configurations for importing to main python file,
this file specifies the path the parameters when running on different machines
"""

import socket, sys


def init(traceType="cloudphysics"):
    NUM_OF_THREADS = 8
    if traceType.lower() == "cloudphysics":
        if "Z240" in socket.gethostname():
            TRACE_DIR = "/home/jason/ALL_DATA/cloudphysics_txt_64K/"
        elif "euler" in socket.gethostname():
            TRACE_DIR = "/var/dept/scratch/jyan254/DATA/cphy_64K/"
            NUM_OF_THREADS = 40
        elif "node" in socket.gethostname():
            TRACE_DIR = "/home/jason/ALL_DATA/cloudphysics_fixed_blockSize/cloudphysics_parda_64KB_aligned_rw/txt/"
            NUM_OF_THREADS = 48
    elif traceType.lower() == 'msr':
        if "Z240" in socket.gethostname():
            TRACE_DIR = "/home/jason/ALL_DATA/msr_txt_64K"
        elif "euler" in socket.gethostname():
            TRACE_DIR = "/var/dept/scratch/jyan254/DATA/msr"
            NUM_OF_THREADS = 40
        elif "node" in socket.gethostname():
            TRACE_DIR = "/home/jason/ALL_DATA/msr_fixed_blockSize/msr_parda_64KB_aligned_rw/txt"
            NUM_OF_THREADS = 48
    else:
        print("do not recognize trace type {}".format(traceType), file=sys.stderr)
    return TRACE_DIR, NUM_OF_THREADS
