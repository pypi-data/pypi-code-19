# Copyright (c) 2015-2016 Avere Systems, Inc.  All Rights Reserved.             
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#!/usr/bin/env python2.7
import sys
import logging
import sys
import time
import threading
import vFXT
from vFXT import ServiceInstance, ServiceBase # pylint: disable=unused-import
import oca

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class Service(ServiceBase):
    '''OpenNebula Service backend'''
    ON_STATUS="RUNNING"
    OFF_STATUS="LCM_INIT"
    # XXX TODO
    NTP_SERVERS=[]
    DNS_SERVERS=[]
    MACHINE_DEFAULTS={}
    MACHINE_TYPES=MACHINE_DEFAULTS.keys()
    CONNECTION_HOST='one.lab.avere.net:2633'

    def __init__(self, username, password, **options):
        '''Constructor

            Arguments:
                username (str)
                password (str)
        '''
        self.user   = username
        self.passwd = password
        self.proxy  = options.get('proxy') or None
        self.local  = threading.local()

        if options.get('no_connection_test', None):
            return

        self.connection_test()

    def connection_test(self):
        '''Connection test

            Raises: vFXTConfigurationException
        '''
        conn = self.connection()
        log.debug("Using OpenNebula version {}".format(conn.version()))

    def connection(self):
        '''Connection factory, returns a new connection or thread local copy
        '''
        if not hasattr(self.local, 'connection'):
            log.debug("Creating new connection object")
            cred = '{}:{}'.format(self.user, self.passwd)
            url  = 'http://{}/RPC2'.format(self.CONNECTION_HOST)
            self.local.connection = oca.Client(cred, url, proxy=self.proxy)
        # XXX timeout?
        return self.local.connection

    @classmethod
    def get_instance_data(cls, source_address=None):
        '''Detect the instance data
            Arguments:
                source_address (str, optional): source address for data request

            This only works when running on a OpenNebula instance.
        '''
        raise Exception("Not implemented")

    @classmethod
    def on_instance_init(cls, source_address=None, no_connection_test=False):
        '''Init an OpenNebula service object from on instance metadata

            Arguments:
                source_address (str, optional): source address for data request
                no_connection_test (bool, optional): skip connection tests, defaults to False
            This is only meant to be called on instance.  Otherwise will
            raise a vFXTConfigurationException exception.
        '''
        raise Exception("Not implemented")

    def find_instances(self, filterdict=None):
        '''Returns all or filtered list of instances

            Arguments:
                filterdct (dict, optional): search query

            Examples:
                {'range_start': first_id, 'range_end': last_id, 'vm_state': 3, 'filter': -2}

                where vm_state is:
                    -2 Any state, including DONE
                    -1 Any state, except DONE (Defualt)
                    0 INIT
                    1 PENDING
                    2 HOLD
                    3 ACTIVE
                    4 STOPPED
                    5 SUSPENDED
                    6 DONE
                    7 FAILED

                where filter is
                    -3: Connected user's resources 
                    -2: All resources 
                    -1: Connected user's and his group's resources 
                     > = 0: UID User's Resources
        '''
        conn = self.connection()
        pool = oca.VirtualMachinePool(conn)

        filterdict = filterdict or {}
        filterdict['vm_state'] = filterdict.get('vm_state') or -1
        filterdict['filter'] = filterdict.get('filter') or -2
        pool.info(**(filterdict or {}))
        return pool

    def get_instances(self, instance_ids):
        '''Returns a list of instances with the given instance ID list

            Arguments:
                instance_ids ([str]): list of instance id strings

            Returns:
                [objs]: list of backend instance objects
        '''
        return self.find_instances({'range_start': min(instance_ids), 'range_end': max(instance_ids)})

    def get_instance(self, instance_id):
        '''Get a specific instance by instance ID

            Arguments:
                instance_id (str)

            Returns:
                obj or None
        '''
        r = self.find_instances({'range_start': instance_id, 'range_end': instance_id})
        if r:
            return r[0]
        return None

    def wait_for_status(self, instance, status, retries=120): # maybe refactor into base class?
        '''Pool on a given instance for status

            Arguments:
                instance (obj): backend instance object
                status (str): status string to watch for
                retries (int=120): number of retries

            Raises: vFXTServiceTimeout
        '''
        s = '...' # in case our instance is not yet alive
        while status != s:
            if retries % 10 ==0: # rate limit
                log.debug("Waiting for status: {} != {}".format(s, status))
            time.sleep(self.POLLTIME)
            try:
                instance = self.refresh(instance)
                s = self.status(instance)
            except Exception as e:
                log.debug('Ignored: {}'.format(e))
                time.sleep(2)
            retries -= 1
            if retries == 0:
                raise vFXT.vFXTServiceTimeout("failed waiting for {} on {}".format(status, self.name(instance)))

    def wait_for_service_checks(self, instance, retries=600):
        pass

    def stop(self, instance, wait=600):
        '''Stop an instance

            Arguments:
                instance: backend instance
                wait (int): wait time
        '''
        if not self.can_stop(instance):
            raise vFXTConfigurationException("Node configuration prevents them from being stopped")
        log.info("Stopping instance {}".format(self.name(instance)))
        instance.poweroff()
        self.wait_for_status(instance, self.OFF_STATUS, retries=wait)

    def start(self, instance, wait=600):
        '''Start an instance

            Arguments:
                instance: backend instance
                wait (int): wait time
        '''
        log.info("Starting instance {}".format(self.name(instance)))
        instance.resume()
        self.wait_for_status(instance, self.ON_STATUS, retries=wait)

    def restart(self, instance):
        '''Restart an instance

            Arguments:
                instance: backend instance
        '''
        if not self.can_stop(instance):
            raise vFXTConfigurationException("Node configuration prevents them from being restarted")
        log.info("Restarting instance {}".format(self.name(instance)))
        # XXX revisit... how to watch the slow state transitions of OpenNebula
        self.stop(instance)
        self.start(instance)

    def destroy(self, instance):
        '''Destroy an instance

            Arguments:
                instance: backend instance
        '''
        log.info("Destroying instance {}".format(self.name(instance)))
        instance.shutdown()
        self.wait_for_status(instance, self.OFF_STATUS)
        instance.delete()
        instance.finalize()
        # XXX test

    def is_on(self, instance): # XXX refactor into base class
        '''Return True if the instance is currently on

            Arguments:
                instance: backend instance
        '''
        return self.status(instance) != self.OFF_STATUS

    def is_off(self, instance): # XXX refactor into base class
        '''Return True if the instance is currently off

            Arguments:
                instance: backend instance
        '''
        return self.status(instance) == self.OFF_STATUS

    def name(self, instance):
        '''Returns the instance name (may be different from instance id)

            Arguments:
                instance: backend instance
        '''
        return instance.name

    def instance_id(self, instance):
        '''Returns the instance id (may be different from instance name)

            Arguments:
                instance: backend instance
        '''
        return instance.id

    def ip(self, instance):
        '''Return the primary IP address of the instance

            Arguments:
                instance: backend instance
        '''
        data = self.get_instance_xml_data(instance)
        return data['ip']

    def fqdn(self, instance):
        '''Provide the fully qualified domain name of the instance

            Arguments:
                instance: backend instance
        '''
        data = self.get_instance_xml_data(instance)
        return data['hostname']

    def status(self, instance):
        '''Return the instance status

            Arguments:
                instance: backend instance
        '''
        state = lcm_state = 'UNKNOWN'
        try:
            lcm_state = instance.str_lcm_state
            state     = instance.str_state
        except Exception as e:
            log.debug("Error getting status: {}".format(e))
        log.debug('state: {}, lcm_state: {}'.format(state, lcm_state))
        # XXX revisit, str_state and str_lcm_state are ambigious, and
        # poweroff() hits a bug in oca
        return lcm_state

    def refresh(self, instance):
        '''Refresh the instance from the OpenNebula backend

            Arguments:
                instance: backend instance
        '''
        instance.info()
        return instance

    def can_stop(self, instance):
        ''' Some instance configurations cannot be stopped. Check if this is one.

            Arguments:
                instance: backend instance
        '''
        return True

    def create_instance(self, machine_type, name, **options):
        '''
    Disk template:
NAME = "Debian Squeeze i386"
PATH = ~/debian-squeeze-i386.qcow2
PUBLIC = NO
PERSISTENT = NO
TYPE = OS
DESCRIPTION = "Initial Debian Squeeze installation."

images[14].__dict__
{'uid': 0, 'regtime': 1454087453, 'uname': 'oneadmin', 'gname': 'oneadmin', 'datastore': 'Images', 'cloning_ops': 0, 'id': 45, 'size': 40000, 'xml': <Element 'IMAGE' at 0x10da881d0>, 'source': '/var/lib/one/datastores/107/58f8048c3885b39b4cdc220a4c48eada', 'state': 1, 'gid': 0, 'template': <oca.pool.Template object at 0x10db7a7d0>, 'type': 2, 'vm_ids': [], 'fstype': 'qcow2', 'cloning_id': -1, 'path': '', 'disk_type': 0, 'name': 'CentOS 7 LG x86_64', 'persistent': 1, 'clone_ids': [], 'client': <oca.Client object at 0x10d9d9f50>, 'running_vms': 0, 'datastore_id': 107}  

>>> data = {}
>>> service._get_xml_data(images[14].xml, data)
>>> data
{'uid': '0', 'group_u': '0', 'image': None, 'regtime': '1454087453', 'uname': 'oneadmin', 'group_a': '0', 'gname': 'oneadmin', 'datastore': 'Images', 'cloning_ops': '0', 'id': '45', 'group_m': '0', 'size': '40000', 'owner_u': '1', 'state': '1', 'vms': None, 'source': '/var/lib/one/datastores/107/58f8048c3885b39b4cdc220a4c48eada', 'owner_m': '1', 'gid': '0', 'template': None, 'type': '2', 'owner_a': '0', 'target_snapshot': '-1', 'other_u': '0', 'driver': 'qcow2', 'fstype': 'qcow2', 'clones': None, 'other_a': '0', 'snapshots': None, 'cloning_id': '-1', 'path': None, 'disk_type': '0', 'other_m': '0', 'permissions': None, 'name': 'CentOS 7 LG x86_64', 'dev_prefix': 'sd', 'persistent': '1', 'running_vms': '0', 'datastore_id': '107'}           

http://docs.opennebula.org/4.14/integration/system_interfaces/api.html
http://docs.opennebula.org/4.14/user/references/template.html

vm template:
NAME   = jason-test-vm
MEMORY = 128 
CPU    = 1
VCPU   = 1

OS = [ 
    ARCH = x86_64,
    BOOT = "hd"
]

DISK = [
  IMAGE_ID  = 68,
  CLONE = "yes",
  PERSISTANT = "no"
]

#DISK = [
#    DRIVER  = "raw",
#    SIZE    = 1048576,
#    TYPE    = "fs"
#]

NIC = [
  NETWORK_ID = 5,
  MODEL = "virtio"
]
GRAPHICS = [
    TYPE    = "vnc",
    LISTEN  = "0.0.0.0"
]

RAW = [ TYPE = "kvm" ]

FEATURES = [
    PAE = "yes",
    ACPI = "yes",
    APIC = "no"
]

with open('/tmp/template') as f:
    template = f.read()
vm_id = oca.VirtualMachine.allocate(conn, template)

hosts = service.list_hosts()
hosts[0].id # vantage5kvm.cc.arriad.com
vm = service.get_instance(vm_id)
vm.deploy(hosts[0].id) # errors OpenNebulaException: [VirtualMachineDeploy] Error getting datastore [0].

        '''
        raise Exception("Not implemented")
    def create_node(self, node_name, cfg, node_opts, instance_options):
        raise Exception("Not implemented")
    def create_cluster(self, cluster, **options):
        raise Exception("Not implemented")
    def post_destroy_cluster(self, cluster):
        raise Exception("Not implemented")
    def add_cluster_nodes(self, cluster, count, **options):
        raise Exception("Not implemented")
    def load_cluster_information(self, cluster, **options):
        raise Exception("Not implemented")

    def shelve(self, instance):
        raise Exception("Not implemented")
    def can_shelve(self, instance):
        return False
    def unshelve(self, instance, count_override=None, size_override=None, type_override=None):
        raise Exception("Not implemented")

    # storage/buckets
    def create_bucket(self, name):
        raise Exception("Not implemented")
    def delete_bucket(self, name):
        raise Exception("Not implemented")
    def authorize_bucket(self, cluster, name, retries=3):
        raise Exception("Not implemented")
    # networking
    def get_default_router(self):
        raise Exception("Not implemented")
    def get_dns_servers(self):
        raise Exception("Not implemented")
    def get_ntp_servers(self):
        raise Exception("Not implemented")
    def get_available_addresses(self, count=1, contiguous=False, addr_range=None, in_use=None):
        raise Exception("Not implemented")
    def add_instance_address(self, ServiceInstance, address, **options):
        raise Exception("Not implemented")
    def in_use_addresses(self, cidr_block):
        raise Exception("Not implemented")
    def instance_in_use_addresses(self, instance, category='all'):
        raise Exception("Not implemented")
    def add_instance_address(self, address, **options):
        raise Exception("Not implemented")
    def remove_instance_address(self, address):
        raise Exception("Not implemented")

    def export(self):
        '''Export the service object in an easy to serialize format
            Returns:
                {}: serializable dictionary
        '''
        return {
            'username':self.user,
            'password':self.passwd,
            'proxy':self.proxy,
        }

    @classmethod
    def _get_xml_data(cls,element, data):
        key = element.tag.lower()
        data[key] = element.text
        for child in element.getchildren():
            cls._get_xml_data(child, data)

    def get_instance_xml_data(self, instance):
        data = {}
        self._get_xml_data(instance.xml, data)
        return data

    def list_images(self, filter_flag=-2, start=-1, end=-1):
        '''List images

            Where filter is
                -3: Connected user's resources 
                -2: All resources
                -1: Connected user's and his group's resources 
                 > = 0: UID User's Resources
        '''
        conn = self.connection()
        pool = oca.ImagePool(conn)
        pool.info(filter_flag, start, end)
        return pool

    def list_templates(self):
        conn = self.connection()
        pool = oca.VmTemplatePool(conn)
        pool.info(-2)
        return pool

    def list_hosts(self):
        conn = self.connection()
        pool = oca.HostPool(conn)
        pool.info()
        return pool


def main(user, password, proxy=None):
    service = Service(user, password, proxy=proxy) # pylint: disable=unused-variable

    #vm_pool = oca.VirtualMachinePool(c)
    #log.info(vm_pool.info())
    #for vm in vm_pool:
    #    log.info("{} (memory: {} MB)".format(vm.name, vm.template.memory))

    import code
    d=globals(); d.update(locals())
    code.interact(local=d)

if __name__ == '__main__':
    if len(sys.argv)>2:
        main(*sys.argv[1:])
    else:
        log.error("Usage: {}: addr[:port] username password".format(sys.argv[0]))

