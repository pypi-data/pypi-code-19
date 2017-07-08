from pysphere import VIServer, VIApiException, VIException
import sys


def get_vcenter_vm_uuid_by_name(host, user, password, vm_name):
    """
    Log into vCenter API search for a vm by name, and return it's uuid
    :param host:
    :param user:
    :param password:
    :param vm_name:
    :return:
    """
    vc = VcenterInterface(host, user, password)
    vmi = VmInterface(vc, vm_name)
    return vmi.get_instance_uuid()


class VcenterInterface:
    """
    Communication and representation of vCenter's API
    """
    def __init__(self, host, user, password, exit_if_failed=True):
        try:
            self.server = VIServer()
            self.server.connect(host, user, password)
            self.host = host
            print('Logged into %s as %s' % (host, user))
        except VIApiException as e:
            print('Cannot login to vCenter (%s) as \'%s\' due to: %s' % (host, user, e))
            if exit_if_failed:
                sys.exit(1)


class VmInterface:
    """
    Representation of a VM in vCenter
    """
    def __init__(self, VcenterInterface, vm_name, exit_if_not_found=True):
        try:
            self.vm = VcenterInterface.server.get_vm_by_name(vm_name)
            print('Found virtual machine: %s' % vm_name)
        except VIException as e:
            print ('Could not locate VM \'%s\' on vCenter (%s): %s' % (vm_name, VcenterInterface.host, e))
            if exit_if_not_found:
                sys.exit(1)
        self.server = VcenterInterface.server

    def get_instance_uuid(self):
        return self.vm.properties.config.instanceUuid

