from infi.dtypes.hctl import HCTL
import os
import glob

def get_hctl_for_sg_device(device_path):
    device_link = os.readlink(os.path.join(os.path.sep, 'sys', 'class', 'scsi_generic', os.path.basename(device_path), 'device'))
    host, channel, target, lun = os.path.basename(device_link).split(':')
    return HCTL(int(host), int(channel), int(target), int(lun))

def get_hctl_for_sd_device_from_scsi_disk(device_path):
    devices = glob.glob(os.path.join(os.path.sep, 'sys', 'class', 'scsi_disk', '*', 'device', 'block:' + os.path.basename(device_path)))
    if not devices:
        devices = glob.glob(os.path.join(os.path.sep, 'sys', 'class', 'scsi_disk', '*', 'device', 'block', os.path.basename(device_path)))
        if not devices:
            raise IOError()     # this is the exception _populate expects if HCTL not found
    host, channel, target, lun = devices[0].split(os.path.sep)[4].split(':')
    return HCTL(int(host), int(channel), int(target), int(lun))

def get_hctl_for_sd_device(device_path):
    if not os.path.exists(os.path.join(os.path.sep, 'sys', 'class', 'block')):
        # older systems (rhel 5) don't have /sys/class/block but do have /sys/class/scsi_disk where
        # we can search for the hctl anyway, maybe a little bit slower
        return get_hctl_for_sd_device_from_scsi_disk(device_path)
    device_link = os.readlink(os.path.join(os.path.sep, 'sys', 'class', 'block', os.path.basename(device_path), 'device'))
    host, channel, target, lun = os.path.basename(device_link).split(':')
    return HCTL(int(host), int(channel), int(target), int(lun))

def get_sg_to_hctl_mappings():
    from glob import glob
    return {device_path: get_hctl_for_sg_device(device_path) for device_path in glob("/dev/sg*")}

def get_sd_to_hctl_mappings():
    from glob import glob
    from os.path import sep
    sd_devices = filter(lambda path: path.split(sep)[-1].isalpha(), glob("/dev/sd*"))
    return {device_path: get_hctl_for_sd_device(device_path) for device_path in sd_devices}

def get_hctl_to_sd_mappings():
    return {hctl: device_path for device_path, hctl in get_sd_to_hctl_mappings().items()}

def get_hctl_to_sg_mappings():
    return {hctl: device_path for device_path, hctl in get_sg_to_hctl_mappings().items()}

def get_sd_from_sg(sg):
    hctl = get_hctl_for_sg_device(sg)
    return get_hctl_to_sd_mappings()[hctl]

def get_sg_from_sd(sd):
    hctl = get_hctl_for_sd_device(sd)
    return get_hctl_to_sg_mappings()[hctl]
