#!/usr/bin/env python
#
# Based on pyvmomi example code available at:
# https://github.com/vmware/pyvmomi-community-samples
#

import sys
import os
import threading
from time import sleep
import requests
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import VcenterInterfaces
import atexit
import time
try:
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass
# disable  urllib3 warnings
if hasattr(requests.packages.urllib3, 'disable_warnings'):
    requests.packages.urllib3.disable_warnings()


class LeaseProgressUpdater(threading.Thread):
    """
        Lease Progress Updater & keep alive thread
    """

    def __init__(self, http_nfc_lease, update_interval):
        threading.Thread.__init__(self)
        self.daemon = True
        self._running = True
        self.httpNfcLease = http_nfc_lease
        self.updateInterval = update_interval
        self.progressPercent = 0

    def set_progress_pct(self, progress_pct):
        self.progressPercent = progress_pct

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            try:
                self.httpNfcLease.HttpNfcLeaseProgress(self.progressPercent)
                sleep(self.updateInterval)
            except Exception as e:
                print "Unable to connect to vCenter due to: {}".format(e.message)
                sys.exit(5)
                return


def print_http_nfc_lease_info(info):
    """ Prints information about the lease,
    such as the entity covered by the lease,
    and HTTP URLs for up/downloading file backings.
    :param info:
    :type info: vim.HttpNfcLease.Info
    :return:
    """
    print 'Lease timeout: {0.leaseTimeout}\n' \
          'Disk Capacity KB: {0.totalDiskCapacityInKB}'.format(info)
    device_number = 1
    if info.deviceUrl:
        for device_url in info.deviceUrl:
            print 'HttpNfcLeaseDeviceUrl: {1}\n' \
                  'Device URL Import Key: {0.importKey}\n' \
                  'Device URL Key: {0.key}\n' \
                  'Device URL: {0.url}\n' \
                  'Device URL Size: {0.fileSize}\n' \
                  'SSL Thumbprint: {0.sslThumbprint}\n'.format(device_url,
                                                               device_number)
            if not device_url.targetId:
                print "No targetId found for this device"
                print "Device is not eligible for export. This could be a mounted iso or img of some sort"
                print "It will NOT be downloaded\n"

            device_number += 1
    else:
        print 'No devices were found.'


def break_down_cookie(cookie):
    """ Breaks down vSphere SOAP cookie
    :param cookie: vSphere SOAP cookie
    :type cookie: str
    :return: Dictionary with cookie_name: cookie_value
    """
    cookie_a = cookie.split(';')
    cookie_name = cookie_a[0].split('=')[0]
    cookie_text = ' {0}; ${1}'.format(cookie_a[0].split('=')[1],
                                      cookie_a[1].lstrip())
    return {cookie_name: cookie_text}


def download_device(headers, cookies, temp_target_disk,
                    device_url, lease_updater,
                    total_bytes_written, total_bytes_to_write):
    """ Download disk device of HttpNfcLease.info.deviceUrl
    list of devices
    :param headers: Request headers
    :type cookies: dict
    :param cookies: Request cookies (session)
    :type cookies: dict
    :param temp_target_disk: file name to write
    :type temp_target_disk: str
    :param device_url: deviceUrl.url
    :type device_url: str
    :param lease_updater:
    :type lease_updater: LeaseProgressUpdater
    :param total_bytes_written: Bytes written so far
    :type total_bytes_to_write: long
    :param total_bytes_to_write: VM unshared storage
    :type total_bytes_to_write: long
    :return:
    """
    with open(temp_target_disk, 'wb') as handle:
        response = requests.get(device_url, stream=True,
                                headers=headers,
                                cookies=cookies, verify=False)
        # response other than 200
        if not response.ok:
            response.raise_for_status()
        # keeping track of progress
        current_bytes_written = 0
        written_pct = 0
        print "Exporting from vCenter..."
        print ""
        last_time = 0
        for block in response.iter_content(chunk_size=1073741824):
            # filter out keep-alive new chunks
            if block:
                handle.write(block)
                handle.flush()
                os.fsync(handle.fileno())

            prev_pct = written_pct
            # Percent is unreliable as i can't find a way to know the size of the disk compressed
            current_bytes_written += len(block)
            # written_pct_float = (float(current_bytes_written + total_bytes_written) / float(total_bytes_to_write) * 100)
            # written_pct = int(written_pct_float)
            # Only do the bytes to gb conversion every 5 seconds
            if int(time.time()) > last_time + 3:
                dl_in_mb = (total_bytes_written + current_bytes_written) /1024 /1024
                last_time = int(time.time())

            print ("\r {} Mb Downloaded ".format(dl_in_mb)),

        #    if written_pct > prev_pct:
        #       lease_updater.progressPercent = int(written_pct)

    return current_bytes_written


class OvfExporter:
    def __init__(self, host=None, port=None, dir=None, vm_name=None, user=None, password=None):
        """
        Instantiate with common attributes of exportable VMs
        :param deploy_config: vcenter configuration
        :param local_save_directory: directory to save to
        :param name: name of the vmdk to export as
        :param port: port to communicate with vcenter
        """
        self.port = port
        self.name = vm_name
        self.workdir = dir
        self.host = host
        self.user = user
        self.password = password
        self.vcenter_conn = self.vcenter_connect()
        self.vm_obj = self.get_vm_obj()
        self.vm_dl_path = self.validate_save_dir()

    def vcenter_connect(self):
        """
        Attempt to connect to vCenter
        :return:
        """
        try:
            si = SmartConnect(
                host=self.host,
                user=self.user,
                pwd=self.password,
                port=self.port)
            # disconnect vc
            atexit.register(Disconnect, si)
        except vim.fault.InvalidLogin as e:
            print "Unable to connect to vcenter because of: {}".format(e.msg)
            sys.exit(5)
        return si

    def get_vm_obj(self):
        """
        Search for vm in vcenter, return the object if found
        :return:
        """
        uuid = VcenterInterfaces.get_vcenter_vm_uuid_by_name(self.host, self.user, self.password, self.name)
        # connect to vc

        # Getting VM data
        vm_obj = self.vcenter_conn.content.searchIndex.FindByUuid(None, uuid, True, True)
        # VM does exist
        if not vm_obj:
            print 'VM {} does not exist'.format(uuid)
            sys.exit(1)

        # VM must be powered off to export
        if not vm_obj.runtime.powerState == \
                vim.VirtualMachine.PowerState.poweredOff:
            print 'VM {} must be powered off'.format(vm_obj.name)
            sys.exit(1)

        return vm_obj

    def validate_save_dir(self):
        """
        Validate that the save directory exists, if not, create it
        :return: str directory
        """
        # checking if working directory exists
        print 'Working dir: {} '.format(self.workdir)
        if not os.path.isdir(self.workdir):
            print 'Creating working directory {}'.format(self.workdir)
            os.mkdir(self.workdir)
        # actual target directory for VM
        target_directory = os.path.join(self.workdir, self.vm_obj.config.instanceUuid)
        print 'Target dir: {}'.format(target_directory)
        if not os.path.isdir(target_directory):
            print 'Creating target dir {}'.format(target_directory)
            os.mkdir(target_directory)
        return target_directory

    def write_ovf_descriptor(self, ovf_files):
        """
        Query vCenter for ovf descriptor information, and write it to a file
        :param ovf_files:
        :return:
        """
        print 'Getting OVF Manager'
        ovf_manager = self.vcenter_conn.content.ovfManager
        print 'Creating OVF Descriptor'
        ovf_parameters = vim.OvfManager.CreateDescriptorParams()
        ovf_parameters.name = self.name
        ovf_parameters.ovfFiles = ovf_files
        vm_descriptor_result = ovf_manager.CreateDescriptor(obj=self.vm_obj,
                                                            cdp=ovf_parameters)
        if vm_descriptor_result.error:
            raise vm_descriptor_result.error[0].fault
        else:
            vm_descriptor = vm_descriptor_result.ovfDescriptor
            target_ovf_descriptor_path = os.path.join(self.vm_dl_path,
                                                      self.name + '.ovf')
            print 'Writing OVF Descriptor {}'.format(
                target_ovf_descriptor_path)
            with open(target_ovf_descriptor_path, 'wb') as handle:
                handle.write(vm_descriptor)

    def export_ovf(self):
        """
        Exports OVf of currently iterated VM (dictated by api.env.hosts)
        :return: ovf location
        """

        # Breaking down SOAP Cookie &
        # creating Header
        soap_cookie = self.vcenter_conn._stub.cookie
        cookies = break_down_cookie(soap_cookie)
        headers = {'Accept': 'application/x-vnd.vmware-streamVmdk'}  # not required
        # Getting HTTP NFC Lease
        http_nfc_lease = self.vm_obj.ExportVm()

        # starting lease updater
        lease_updater = LeaseProgressUpdater(http_nfc_lease, 30)
        lease_updater.start()
        # Creating list for ovf files which will be value of
        # ovfFiles parameter in vim.OvfManager.CreateDescriptorParams
        ovf_files = list()
        total_bytes_written = 0
        # http_nfc_lease.info.totalDiskCapacityInKB not real
        # download size
        total_bytes_to_write = self.vm_obj.summary.storage.unshared

        while True:
            if http_nfc_lease.state == vim.HttpNfcLease.State.ready:
                print 'HTTP NFC Lease Ready'
                print_http_nfc_lease_info(http_nfc_lease.info)

                for deviceUrl in http_nfc_lease.info.deviceUrl:
                    if not deviceUrl.targetId:
                        continue

                    temp_target_disk = os.path.join(self.vm_dl_path,
                                                    self.name)
                    temp_target_disk += ".vmdk"
                    print '\nDownloading {} to {}'.format(deviceUrl.url,
                                                          temp_target_disk)
                    current_bytes_written = download_device(
                        headers=headers, cookies=cookies,
                        temp_target_disk=temp_target_disk,
                        device_url=deviceUrl.url,
                        lease_updater=lease_updater,
                        total_bytes_written=total_bytes_written,
                        total_bytes_to_write=total_bytes_to_write)
                    # Adding up file written bytes to total
                    total_bytes_written += current_bytes_written
                    print 'Creating OVF file for {}'.format(temp_target_disk)
                    # Adding Disk to OVF Files list
                    ovf_file = vim.OvfManager.OvfFile()
                    ovf_file.deviceId = deviceUrl.key
                    ovf_file.path = deviceUrl.targetId
                    ovf_file.size = current_bytes_written
                    ovf_files.append(ovf_file)
                break
            elif http_nfc_lease.state == vim.HttpNfcLease.State.initializing:
                print 'HTTP NFC Lease Initializing.'
            elif http_nfc_lease.state == vim.HttpNfcLease.State.error:
                raise Exception("HTTP NFC Lease error: {}".format(
                    http_nfc_lease.state.error))
            sleep(2)
            self.write_ovf_descriptor(ovf_files)
            # ending lease
            http_nfc_lease.HttpNfcLeaseProgress(100)
            http_nfc_lease.HttpNfcLeaseComplete()
            # stopping thread
            lease_updater.stop()
        print 'VMDK saved at: {}'.format(temp_target_disk)
        return temp_target_disk

