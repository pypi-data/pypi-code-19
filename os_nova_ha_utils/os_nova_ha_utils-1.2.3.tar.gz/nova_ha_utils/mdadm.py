import os
import re
import logging
import subprocess

#WE PROBABLY DON'T NEED THIS
# device info - describes SCSI device which was previously configured for
# MD RAID
# this function works only for scsi block devices
# attributes:
#    wwid - SCSI wwn of the device
#    path - filesystem path to the device
#    md_uuid - MD RAID uuid
#    md_num_devs - number of devices of RAID this dev belong to
#    md_level - RAID level of RAID this dev belong to
#def get_md_scsi_device_generic_info(path):
#
#    device_info = {}
#
#    stdout = subprocess.check_output(['/lib/udev/scsi_id', '--whitelisted', path])
#
#    lines = stdout.splitlines()
#
#    lines = stdout.splitlines()
#    if len(lines) != 1:
#        logging.warning('bullshit nebo nema')
#
#    if len(lines[0]) < 5:
#        logging.warning('weird uuid')
#
#    device_info['wwn'] = lines[0]
#    #device_info['path'] = path
#
#
#    cmd = '/sbin/mdadm --examine --export {}'.format(path)
#    outlines = subprocess.check_output(cmd,shell=True)
#
#    mdadm_values = {}
#    for line in outlines.splitlines():
#        k,v = line.split('=')
#        mdadm_values[k] = v
#
#
#    device_info['md_uuid'] = mdadm_values['MD_UUID']
#    device_info['md_num_devs']  = mdadm_values['MD_DEVICES']
#    device_info['md_level'] = mdadm_values['MD_LEVEL']
#
#    return device_info


def get_mdadm_detail(dev_path):

    out = subprocess.check_output(['mdadm', '--detail', dev_path, '-Y'])
    logging.info("Fetching MDADM details for dev_path: %s.", dev_path)

    mdadm_values = {}
    for line in out.splitlines():
        k, v = line.split('=')
        mdadm_values[k] = v

    md_detail = {}
    md_detail['uuid'] = mdadm_values['MD_UUID']
    md_detail['name'] = mdadm_values['MD_NAME']
    md_detail['level'] = mdadm_values['MD_LEVEL']
    md_detail['num_devices'] = mdadm_values['MD_DEVICES']
    #md_detail['dev_name'] = mdadm_values['MD_DEVNAME']
    #md_detail['dev_path'] = dev_path

    d = [v for k, v in mdadm_values.items() if re.search('MD_DEVICE.*_DEV', k)]
    md_detail['devices'] = d

    return md_detail


# return system-wide info -
#
# !!  local to the caller !! - careful
# with /dev/path this call can (and should) return dev_path but
# (as it is local runtime) but it has to be removed when storing
# to consul - we want to store "locality-agnostic" info only
def get_md_local_runtime_info_by_uuid():

    md_arrays = {}
    #we should check output and not relly on retval
    #because of permission denied on some files
    out = subprocess.check_output(['find', '/sys/devices', '-name', 'array_state'])
    logging.info("Fetching list of available MD devices from a system.")


    for line in out.splitlines():
        md_state = subprocess.check_output(['cat', line]).splitlines()[0]
        if md_state != 'active' and md_state != 'clean':
            continue

        tmp = os.path.split(line)[0]
        sys_root = os.path.split(tmp)[0]
        sys_dev_name = os.path.split(sys_root)[1]

        dev_path = '/dev/{}'.format(sys_dev_name)

        md_detail = get_mdadm_detail(dev_path)
        md_detail['state'] = md_state
        md_detail['dev_path'] = dev_path

        md_arrays[md_detail['uuid']] = md_detail

    return md_arrays


# FIXME: Would be fine to restore md device to original state after failure.
def mdadm_assemble_by_uuid(md_uuid, md_dev_path):

    #check_output raises exception if ret code non-zero
    logging.info("Trying to assemble raid with uuid: %s and md_dev_path: %s.", md_uuid, md_dev_path)
    subprocess.check_output(['mdadm', '-A', '-u', md_uuid, md_dev_path])

