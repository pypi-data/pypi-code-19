import os
import subprocess
import logging

from retrying import retry
from mdadm import get_mdadm_detail

class BlockDeviceErrors(BaseException):
    """ Block Device exceptions """

# We make it failsafe because scsu_id queries the actual device via
# potentially undereliable SAS network
@retry(wait_fixed=2000, stop_max_attempt_number=5)
def get_scsi_device_wwn(path):
    logging.info("Getting disk WWN info from device: %s.", path)

    stdout = subprocess.check_output(['/lib/udev/scsi_id', '--whitelisted', path])

    lines = stdout.splitlines()

    if len(lines) != 1:
        logging.debug("Can't find device WWN in list: %s", lines)
        raise BlockDeviceErrors('SCSI WWN ERROR')

    if len(lines[0]) < 5:
        logging.debug("WWN seems to be in a wrong format: %s", lines[0])
        raise BlockDeviceErrors('SCSI WWN ERROR')

    return lines[0]

def get_scsi_device_map_by_wwn():
    return _get_device_map_by_wwn('scsi')


def get_multipath_device_map_by_wwn():
    return _get_device_map_by_wwn('dm')


def _get_device_map_by_wwn(dev_type):
    if dev_type == 'dm':
        scsi_devs = []
        for dev in os.listdir('/sys/block'):
            uuid_path = '/sys/block/{}/dm/uuid'.format(dev)
            if os.path.exists(uuid_path):
                if 'mpath' in open(uuid_path).read():
                    scsi_devs.append('/dev/{}'.format(dev))

    elif dev_type == 'scsi':
        scsi_devs = ['/dev/{}'.format(x) for x in os.listdir('/sys/block') if
                     os.path.exists('/sys/block/{}/device/scsi_device'.format(x))]
    else:
        scsi_devs = []

    logging.info("Creating device map for dev_type: %s and block_devices: %s", dev_type, scsi_devs)

    dev_map = {}
    for dev_path in scsi_devs:
        wwn = get_scsi_device_wwn(dev_path)
        dev_map[wwn] = dev_path

    return dev_map


def get_block_device_basic_info(path):

    info = {}
    dev_name = os.path.split(path)[1]

    logging.info("Getting block device info for a device: %s", path)

    # If we have received multipath device use first path as a device name
    if os.path.exists('/sys/block/{}/dm/uuid'.format(dev_name)):
        dev_name = os.listdir('/sys/block/{}/slaves'.format(dev_name))[0]

    if os.path.exists('/sys/block/{}/device/scsi_device'.format(dev_name)):
        info['uuid'] = get_scsi_device_wwn('/dev/{}'.format(dev_name))
        info['type'] = 'scsi'
    elif os.path.exists('/sys/block/{}/md/array_state'.format(dev_name)):
        md_detail = get_mdadm_detail('/dev/{}'.format(dev_name))
        info['uuid'] = md_detail['uuid']
        info['type'] = 'md'
    else:
        raise BlockDeviceErrors("unsupported device type")

    return info
