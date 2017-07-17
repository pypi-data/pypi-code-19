import os
import sys
import subprocess
import re

import logging

from retrying import retry

# returns system-wide info
def get_lvm_runtime_info_by_vg():

    out = subprocess.check_output(['pvdisplay', '-c'])
    logging.info("Fetching LVM information from a system.")

    pvs = {}
    for line in out.splitlines():
        parts = line.split(':')

        # If possible get existing record
        record = pvs.get(parts[1], {})

        pv_paths = record.get('pv_path', [])
        pv_paths.append(parts[0])

        record['pv_path'] = pv_paths
        record['vg_name'] = parts[1]
        record['uuid'] = parts[11]
        pvs[parts[1]] = record

    return pvs

def get_mounted_filesystems_by_mountpoint():

    out = subprocess.check_output(['/bin/cat', '/proc/mounts'])
    logging.info("Fetching mounted filesystem info from a system.")

    mounts = {}
    for line in out.splitlines():
        record = {}
        parts = line.split(' ')
        if '/dev' in parts[0]:
            record['dev_path'] = parts[0]
            record['mountpoint'] = parts[1]
            record['fs_type'] = parts[2]
            mounts[parts[1]] = record

    return mounts

def clear_env(clear_env_vars=[]):

    for i in clear_env_vars:
        if i in os.environ:
            del os.environ[i]