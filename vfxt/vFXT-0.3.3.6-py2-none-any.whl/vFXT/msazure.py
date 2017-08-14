# Copyright (c) 2015-2016 Avere Systems, Inc.  All Rights Reserved.
'''Abstraction for doing things on the instances via MS Azure

Cookbook/examples:

service = vFXT.msazure.Service(
    subscription_id=subscription_id,
    client_id=client_id,
    client_secret=client_secret,
    tenant_id=tenant_id,
    resource_group=resource_group,
    location=location,
    network=azure_network,
    subnet=azure_subnet,
    # for disks
    storage_account=storage_account,
    premium_storage_account=premium_storage_account,
    # instance creds to pass along
    instance_client_id=instance_client_id,
    instance_client_secret=instance_client_secret,
    instance_service_principal_id=instance_service_principal_id,
)

# Connection factory
connection = msazure.connection()

instances = msazure.find_instances()
instances = msazure.get_instances([])

instance = msazure.get_instance('instance id')
msazure.start(instance)
msazure.stop(instance)
msazure.restart(instance)
msazure.destroy(instance)

msazure.shelve(instance)
msazure.unshelve(instance)

instance = msazure.refresh(instance)

print msazure.name(instance)
print msazure.ip(instance)
print msazure.fqdn(instance)
print msazure.status(instance)

if msazure.is_on(instance): pass
if msazure.is_off(instance): pass
if msazure.is_shelved(instance): pass

msazure.wait_for_status(instance, msazure.ON_STATUS, msazure.WAIT_FOR_SUCCESS)

msazure.create_instance(machine_type, name, boot_disk_image, other_disks=None, **options)
msazure.create_cluster(self, cluster, **options)

# msazure.create_bucket(name)
# msazure.delete_bucket(name)

msazure.load_cluster_information(cluster)

ip_count = 12
ip_addresses, mask = msazure.get_available_addresses(count=ip_count, contiguous=True)
msazure.get_dns_servers()
msazure.get_ntp_servers()
msazure.get_default_router()

serializeme = msazure.export()
newmsazure = vFXT.msazure.Service(**serializeme)

'''
import time
import threading
import Queue
import logging
import urlparse
import urllib2
import socket
import json
import uuid
import re
from itertools import cycle

import requests
logging.getLogger('requests').setLevel(logging.CRITICAL)
requests.packages.urllib3.disable_warnings()

import vFXT.azureutils

from vFXT.cidr import Cidr
from vFXT.serviceInstance import ServiceInstance
from vFXT.service import *

log = logging.getLogger(__name__)

class Service(ServiceBase):
    '''Azure service backend'''
    ON_STATUS=['ProvisioningState/succeeded','PowerState/running']
    OFF_STATUS=['ProvisioningState/succeeded','PowerState/deallocated']
    STOP_STATUS=['ProvisioningState/succeeded','PowerState/stopped']
    #DESTROYED_STATUS=['ProvisioningState/succeeded']
    NTP_SERVERS=['time.windows.com']
    DNS_SERVERS=['168.63.129.16']
    MACHINE_DEFAULTS={
        'Standard_A4':      {'data_disk_size':128,'data_disk_count':0, 'node_count':0},
        'Standard_A7':      {'data_disk_size':128,'data_disk_count':0, 'node_count':0},
        'Standard_A8':      {'data_disk_size':128,'data_disk_count':0, 'node_count':0},
        'Standard_A9':      {'data_disk_size':128,'data_disk_count':0, 'node_count':0},
        'Standard_A10':     {'data_disk_size':128,'data_disk_count':0, 'node_count':0},
        'Standard_A11':     {'data_disk_size':128,'data_disk_count':0, 'node_count':0},
        'Standard_D4':      {'data_disk_size':256,'data_disk_count':0, 'node_count':0},
        'Standard_D4_v2':   {'data_disk_size':256,'data_disk_count':0, 'node_count':0},
        'Standard_D5_v2':   {'data_disk_size':256,'data_disk_count':0, 'node_count':0},
        'Standard_D13':     {'data_disk_size':512,'data_disk_count':1, 'node_count':3},
        'Standard_D13_v2':  {'data_disk_size':512,'data_disk_count':1, 'node_count':3},
        'Standard_D14':     {'data_disk_size':512,'data_disk_count':1, 'node_count':3},
        'Standard_D14_v2':  {'data_disk_size':512,'data_disk_count':1, 'node_count':3},
        'Standard_DS1':     {'data_disk_size':256,'data_disk_count':0, 'node_count':0},
        'Standard_DS4':     {'data_disk_size':256,'data_disk_count':0, 'node_count':0},
        'Standard_DS4_v2':     {'data_disk_size':256,'data_disk_count':0, 'node_count':0},
        'Standard_DS5_v2':     {'data_disk_size':256,'data_disk_count':0, 'node_count':0},
        'Standard_DS13':    {'data_disk_size':1024,'data_disk_count':1, 'node_count':3},
        'Standard_DS13_v2':    {'data_disk_size':1024,'data_disk_count':1, 'node_count':3},
        'Standard_DS14':    {'data_disk_size':1024,'data_disk_count':1, 'node_count':3},
        'Standard_DS14_v2':    {'data_disk_size':1024,'data_disk_count':1, 'node_count':3},
        'Standard_DS15_v2':    {'data_disk_size':1024,'data_disk_count':1, 'node_count':3},
        'Standard_G3':      {'data_disk_size':512,'data_disk_count':2, 'node_count':3},
        'Standard_G4':      {'data_disk_size':512,'data_disk_count':2, 'node_count':3},
        'Standard_G5':      {'data_disk_size':512,'data_disk_count':2, 'node_count':3},
        'Standard_GS3':     {'data_disk_size':512,'data_disk_count':2, 'node_count':3},
        'Standard_GS4':     {'data_disk_size':512,'data_disk_count':2, 'node_count':3},
        'Standard_GS5':     {'data_disk_size':512,'data_disk_count':2, 'node_count':3},
    }
    VALID_DATA_DISK_SIZES=[128, 512, 1024]
    MAX_DATA_DISK_COUNT=32
    MACHINE_TYPES=MACHINE_DEFAULTS.keys()
    DEFAULTS_URL='https://averedist.blob.core.windows.net/dist/vfxtdefaults.json'
    DEFAULT_STORAGE_ACCOUNT_TYPE='Standard_LRS'
    AZURE_INSTANCE_HOST='169.254.169.254'
    INSTANCENAME_RE=re.compile('[a-z][-a-z0-9]*')
    SYSTEM_CONTAINER='system'
    VHDS_CONTAINER='vhds'
    ENDPOINT_TEST_HOSTS = ['management.azure.com']
    ROLE_PERMISSIONS=[{
        'notActions': [],
        'actions': [
            'Microsoft.Compute/virtualMachines/read',
            'Microsoft.Network/networkInterfaces/read',
            'Microsoft.Network/routeTables/read',
            'Microsoft.Network/routeTables/routes/*',
            'Microsoft.Resources/subscriptions/resourceGroups/read']
    }]
    WAIT_FOR_SUCCESS=500 # override ServiceBase.WAIT_FOR_SUCCESS
    WAIT_FOR_STOP=800 # override ServiceBase.WAIT_FOR_STOP

    def __init__(self, subscription_id=None, client_id=None, client_secret=None,
                       tenant_id=None, resource_group=None, storage_account=None,
                       **options):
        '''Constructor

            Arguments:
                subscription_id (str): Azure subscription identifier
                client_id (str): AD application client ID
                client_secret (str): Client secret
                tenant_id (str): AD application tenant identifier
                resource_group (str): Resource group
                storage_account (str): Azure Storage account

                premium_storage_account (str, optional): Premium Azure Storage account (defaults to storage_account)
                location (str, optional): Azure location
                network (str, optional): Azure virtual network
                subnet ([str], optional): list of Azure virtual network subnets
                instance_client_id (str, optional): client ID for instances
                instance_client_secret (str, optional): client secret for instances
                instance_service_principal_id (str, optional): service principal ID for instances

                network_security_group (str, optional): network security group name
                private_range (str, optional): private address range (cidr)
                proxy_uri (str, optional): URI of proxy resource (e.g. http://user:pass@172.16.16.20:8080)
                no_connection_test (bool, optional): skip connection test
        '''


        self.subscription_id = subscription_id
        self.client_id       = client_id
        self.client_secret   = client_secret
        self.tenant_id       = tenant_id
        self.resource_group  = resource_group
        self.storage_account = storage_account

        self.location        = options.get('location') or None
        self.network         = options.get('network') or None
        self.subnets         = options.get('subnet') or []
        self.subnets         = [self.subnets] if isinstance(self.subnets, basestring) else self.subnets
        self.private_range   = options.get('private_range') or None

        self.proxy_uri       = options.get('proxy_uri') or None
        if self.proxy_uri: # parse proxy uri into host and port (and user, password)
            self.set_proxy(self.proxy_uri)

            proxy_handler = urllib2.ProxyHandler({'http':self.proxy_uri, 'https':self.proxy_uri})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)
        else:
            self.proxy = None

        # if we have a premium storage account for data disks
        self.premium_storage_account = options.get('premium_storage_account') or self.storage_account
        # instance client id and secret
        self.instance_client_id            = options.get('instance_client_id') or self.client_id
        self.instance_client_secret        = options.get('instance_client_secret') or self.client_secret
        self.instance_service_principal_id = options.get('instance_service_principal_id')

        self.network_security_group        = options.get('network_security_group') or None

        self.local = threading.local()

        log.debug("Using azureutils version {}".format(vFXT.azureutils.__version__))
        log.debug("Using requests version {}".format(requests.__version__))

        if not options.get('no_connection_test', None):
            self.connection_test()

        log.debug("Fetching defaults from {}".format(self.DEFAULTS_URL))
        load_defaults(self)

        # Can we authenticate the instance client-id/secret
        if self.instance_client_id and self.instance_client_secret:
            log.debug("Verifying instance client-id and client-secret")
            try:
                self._list_subscriptions(self.tenant_id, self.instance_client_id, self.instance_client_secret)
            except Exception as e:
                log.debug(e)
                raise vFXTConfigurationException("Failed to verify instance client-id and client-secret: {}".format(e))
        # TODO: can we verify the instance service principal ID?

    def connection_test(self):
        '''Connection test

            Raises: vFXTConfigurationException
        '''
        log.debug("Performing connection test")

        conn = None
        # quota check is a good api test
        try:
            if not self.proxy: # proxy environments may block outgoing name resolution
                self.dns_check()

            conn = self.connection()

            if self.location:
                for q in conn.networks.getUsage(location=self.location):
                    if q['currentValue']/q['limit'] > 0.9:
                        log.warn("QUOTA ALERT: Using {} of {} {}".format(q['currentValue'], q['limit'], q['name']['localizedValue']))
                for q in conn.vm.getUsage(location=self.location):
                    if q['currentValue']/q['limit'] > 0.9:
                        log.warn("QUOTA ALERT: Using {} of {} {}".format(q['currentValue'], q['limit'], q['name']['localizedValue']))
            for q in conn.storageaccounts.getUsage():
                if q['currentValue']/q['limit'] > 0.9:
                    log.warn("QUOTA ALERT: Using {} of {} {}".format(q['currentValue'], q['limit'], q['name']['localizedValue']))
        except Exception as e:
            raise vFXTServiceConnectionFailure("Failed to establish connection to service: {}".format(e))

        # XXX we assume a route table is present in the subnet for us to configure
        try:
            if self.subnets: # if we have subnets, check for a route table association
                subnet = conn.networks.getSubnet(network=self.network, subnet=self.subnets[0])
                if not 'routeTable' in subnet['properties']:
                    raise vFXTConfigurationException("No route table associated with the subnet")
            else: # otherwise, we can only check for a route table
                log.warn("No subnet configuration provided.  Checking for presence of route tables")
                # listRouteTables returns a generator... we just check for at least one
                if not next(conn.networks.listRouteTables()):
                    raise vFXTConfigurationException("No route tables found.  Please create a route table and associate it with a subnet")
        except vFXTConfigurationException:
            raise
        except (StopIteration, AssertionError) as e:
            log.debug(e)
            raise vFXTConfigurationException("No route tables found in {}.  Unable to set network configuration options.".format(self.subnets[0]))
        except Exception as e:
            log.debug(e)
            raise vFXTConfigurationException("Failed to validate subnet configuration: {}".format(e))

        return True

    def connection(self):
        '''Connection factory, returns a new connection or thread local copy
        '''

        if not hasattr(self.local, 'connection'):
            conn = vFXT.azureutils.AzureApi(
                    subscription=self.subscription_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    tenant=self.tenant_id,
                    resource_group=self.resource_group,
                    storage_account=self.storage_account,
                    proxy_uri=self.proxy_uri,
                    timeout=CONNECTION_TIMEOUT,
            )
            self.local.connection = conn
        return self.local.connection

    @classmethod
    def _get_instance_id(cls):
        '''Query the minimal metadata service for the instance name
        '''
        url = 'http://{}/metadata/v1/InstanceInfo'.format(cls.AZURE_INSTANCE_HOST)
        return json.loads(urllib2.urlopen(url).read())['ID'][1:]

    @classmethod
    def get_instance_data(cls, **options):
        '''Detect the instance data

            Arguments:
                source_address (str, optional): source address for data request
                proxy_uri (str, optional): URI of proxy resource
                subscription_id (str): Azure subscription identifier
                client_id (str): AD application client ID
                client_secret (str): Client secret
                tenant_id (str): AD application tenant identifier
                resource_group (str): Resource group

            This only works when running on an Azure instance.

            This is a service specific data structure.

            Well known keys that can be expected across services:
            machine_type (str): machine/instance type
            account_id (str): account identifier
            service_id (str): unique identifier for this host
            ssh_keys ([str]): ssh keys
            cluster_cfg (str): cluster configuration
        '''
        source_address  = options.get('source_address') or None #pylint: disable=unused-variable
        proxy_uri       = options.get('proxy_uri') or None
        client_id       = options.get('client_id') or None
        client_secret   = options.get('client_secret') or None
        subscription_id = options.get('subscription_id') or None
        tenant_id       = options.get('tenant_id') or None
        resource_group  = options.get('resource_group') or None

        s = socket.socket()
        s.settimeout(1) # fast timeout
        try:
            s.connect((cls.AZURE_INSTANCE_HOST, 80))
        except:
            raise vFXTConfigurationException("Not on an Azure instance")
        finally:
            s.close()

        # need to call this here to short circuit azureutils since
        # we don't go through Service() and connection_test()
        if not proxy_uri:
            cls.dns_check()

        instance_id = cls._get_instance_id()

        # Cannot use a full service object yet since we don't yet know the resource
        # groups etc
        conn = vFXT.azureutils.AzureApi(subscription=subscription_id, client_id=client_id,
                client_secret=client_secret, tenant=tenant_id, proxy_uri=proxy_uri, timeout=CONNECTION_TIMEOUT)

        # find our instance
        instance = None
        if resource_group:
            instance = conn.vm.get(resource_group=resource_group, name=instance_id)
        else:
            for rg in conn.listResourceGroups():
                try:
                    instance = conn.vm.get(resource_group=rg['name'], name=instance_id)
                    break
                except: pass
        if not instance:
            raise vFXTConfigurationException("Unable to find an Azure instance for the current host")

        boot_disk = instance['properties']['storageProfile']['osDisk']['vhd']['uri']
        instance['storage_account'] = urlparse.urlparse(boot_disk).hostname.split('.')[0]
        if instance['properties']['storageProfile']['dataDisks']:
            data_disk = instance['properties']['storageProfile']['dataDisks'][0]['vhd']['uri']
            instance['premium_storage_account'] = urlparse.urlparse(data_disk).hostname.split('.')[0]
        else:
            instance['premium_storage_account'] = instance['storage_account']

        instance['machine_type'] = instance['properties']['hardwareProfile']['vmSize']
        instance['account_id'] = subscription_id
        instance['service_id'] = instance_id
        instance['ssh_keys'] = []
        instance['cluster_cfg'] = ''

        return instance

    @classmethod
    def on_instance_init(cls, **options):
        '''Init an Azure service object from instance metadata
            Arguments:
                subscription_id (str): Azure subscription identifier
                client_id (str): AD application client ID
                client_secret (str): Client secret
                tenant_id (str): AD application tenant identifier

                resource_group (str, optional): Resource group
                source_address (str, optional): source address for data request
                proxy_uri (str, optional): URI of proxy resource
                no_connection_test (bool, optional): skip connection tests, defaults to False

            This is only meant to be called on instance.  Otherwise will
            raise a vFXTConfigurationException exception.
        '''
        source_address  = options.get('source_address') or None
        proxy_uri       = options.get('proxy_uri') or None
        client_id       = options.get('client_id') or None
        client_secret   = options.get('client_secret') or None
        subscription_id = options.get('subscription_id') or None
        tenant_id       = options.get('tenant_id') or None
        resource_group  = options.get('resource_group') or None
        no_connection_test = options.get('no_connection_test') or False

        instance = cls.get_instance_data(source_address=source_address, proxy_uri=proxy_uri,
                          no_connection_test=no_connection_test, client_id=client_id,
                          client_secret=client_secret, subscription_id=subscription_id,
                          tenant_id=tenant_id, resource_group=resource_group,
        )

        try:
            service = Service(source_address=source_address, proxy_uri=proxy_uri,
                              no_connection_test=no_connection_test, client_id=client_id,
                              client_secret=client_secret, subscription_id=subscription_id,
                              tenant_id=tenant_id,
                              location=instance['location'],
                              resource_group=resource_group or instance['id'].split('/')[4],
                              storage_account=instance['storage_account'],
                              premium_storage_account=instance['premium_storage_account'],
            )
            service.local.instance_data = instance

            # detect our network/subnet by the instance NIC
            nic_name  = instance['properties']['networkProfile']['networkInterfaces'][0]['id'].split('/')[-1]
            nic       = service.connection().networks.getNIC(name=nic_name)
            subnet_id = nic['properties']['ipConfigurations'][0]['properties']['subnet']['id']
            service.subnets = [subnet_id.split('/')[-1]]
            service.network = subnet_id.split('/')[-3]
            if 'networkSecurityGroup' in nic['properties']:
                service.network_security_group = nic['properties']['networkSecurityGroup']['id'].split('/')[-1]

            return service
        except (vFXTServiceFailure, vFXTServiceConnectionFailure) as e:
            raise
        except Exception as e:
            raise vFXTConfigurationException(e)

    def find_instances(self, search=None):
        '''Returns all or filtered list of instances

            Arguments:
                search (str, optional): search name by string/regex

            Returns:
                [objs]: list of backend instance objects
        '''
        r = re.compile(search or '')
        return [_ for _ in self.connection().vm.list() if re.search(r, _['name'])]

    def get_instances(self, instance_ids):
        '''Returns a list of instances with the given instance ID list

            Arguments:
                instance_ids ([str]): list of instance id strings

            Returns:
                [objs]: list of backend instance objects
        '''
        return [_ for _ in self.find_instances() if _['name'] in instance_ids]

    def get_instance(self, instance_id):
        '''Get a specific instance by instance ID

            Arguments:
                instance_id (str)

            Returns:
                obj or None
        '''
        try:
            return self.connection().vm.get(name=instance_id)
        except Exception as e:
            log.debug(e)
            return None

    def wait_for_status(self, instance, status, retries=ServiceBase.WAIT_FOR_STATUS):
        '''Poll on a given instance for status

            Arguments:
                instance (obj): backend instance object
                status (str): status string to watch for
                retries (int, optional): number of retries

            Raises: vFXTServiceTimeout
        '''
        s = '...' # in case our instance is not yet alive
        errors = 0
        while status != s:
            if retries % 10 == 0: # rate limit
                log.debug("Waiting for status: {} != {}".format(s, status))
            time.sleep(self.POLLTIME)
            try:
                instance = self.refresh(instance)
                s = self.status(instance)
                status_errors = [_ for _ in s if 'ProvisioningState/failed' in _]
                if status_errors:
                    raise vFXTServiceFailure("Instance {} failed: {}".format(instance['name'], status_errors))
            except vFXTServiceFailure:
                raise
            except Exception as e:
                log.debug('Ignored: {}'.format(e))
                errors += 1
                time.sleep(backoff(errors))
            retries -= 1
            if retries == 0:
                raise vFXTServiceTimeout("Timed out waiting for {} on {}".format(status, instance['name']))

    def wait_for_service_checks(self, instance, retries=ServiceBase.WAIT_FOR_SERVICE_CHECKS):
        # No MS Azure equivalent
        return True

    def _wait_for_operation(self, operation_id, msg='operation to complete', retries=ServiceBase.WAIT_FOR_OPERATION, location=None, status='Succeeded'):
        '''Wait for an operation to complete by polling the response

            Arguments:
                operation_id (string): operation ID
                retries (int, optional): number of retries
                location (str, optional): location to check (defaults to Service.location)
                status (str, optional): status text

            Raises: vFXTServiceFailure
        '''
        location = location or self.location
        conn = self.connection()

        response = conn.locations.getOperation(location=location, name=operation_id)

        while response['status'] != status:
            time.sleep(self.POLLTIME)
            if retries % 10 == 0:
                log.debug("Waiting for {}: {}".format(msg, response['status']))

            response = conn.locations.getOperation(location=location, name=operation_id)

            retries -= 1
            if retries == 0:
                raise vFXTServiceTimeout("Failed waiting for operation to complete")

    def stop(self, instance, wait=WAIT_FOR_STOP):
        '''Stop an instance

            Arguments:
                instance: backend instance
                wait (int, optional): wait time for operation to complete
        '''
        if not self.can_stop(instance):
            raise vFXTConfigurationException("Node configuration prevents them from being stopped")
        log.info("Stopping instance {}".format(self.name(instance)))
        conn = self.connection()
        # r = conn.vm.stop(name=self.name(instance))
        # use deallocate so that we do not get charged for the vm
        r = conn.vm.deallocate(name=self.name(instance))
        self._wait_for_operation(r.headers['x-ms-request-id'], msg='instance to stop', retries=wait)

    def start(self, instance, wait=ServiceBase.WAIT_FOR_START):
        '''Start an instance

            Arguments:
                instance: backend instance
                wait (int, optional): wait time for operation to complete
        '''
        log.info("Starting instance {}".format(self.name(instance)))
        conn = self.connection()
        r = conn.vm.start(name=self.name(instance))
        self._wait_for_operation(r.headers['x-ms-request-id'], msg='instance to start', retries=wait)

    def restart(self, instance, wait=ServiceBase.WAIT_FOR_RESTART):
        '''Restart an instance

            Arguments:
                instance: backend instance
                wait (int): wait time
        '''
        assert self.can_stop(instance)
        log.info("Restarting instance {}".format(self.name(instance)))
        # Azure does have a restart option, but we want to track the instance status
        self.stop(instance)
        self.start(instance)

    def _reset(self, instance, wait=ServiceBase.WAIT_FOR_RESTART):
        '''Reset an instance.

            Arguments:
                instance: backend instance
                wait (int, optional): wait time for restart

            This is like restart but does not run the stop/start cycle.  This seems
            to be useful if the instance is not responding after starting up from
            a stop state.
        '''
        log.info("Resetting instance {}".format(self.name(instance)))
        conn = self.connection()
        r = conn.vm.restart(name=self.name(instance))
        self._wait_for_operation(r.headers['x-ms-request-id'], msg='instance to restart', retries=wait)

    def destroy(self, instance, wait=ServiceBase.WAIT_FOR_DESTROY):
        '''Destroy an instance

            Arguments:
                instance: backend instance
                wait (int, optional): wait time for operation to complete
        '''
        log.info("Destroying instance {}".format(self.name(instance)))
        conn = self.connection()
        primary_ip = self.ip(instance)

        r = conn.vm.delete(name=self.name(instance))

        # we wait because we cannot destroy resources still attached to the instance
        self._wait_for_operation(r.headers['x-ms-request-id'], msg='instance to be destroyed', retries=wait)

        # Also need to delete any leftover disks
        try:
            root_disk  = self._parse_vhd_uri(instance['properties']['storageProfile']['osDisk']['vhd']['uri'])
            conn.blob.delete(**root_disk)
        except Exception as e:
            log.debug("Failed to delete root disk: {}".format(e))
        for data_disk in instance['properties']['storageProfile']['dataDisks']:
            try:
                disk = self._parse_vhd_uri(data_disk['vhd']['uri'])
                conn.blob.delete(**disk)
            except Exception as e:
                log.debug("Failed to delete data disk: {}".format(e))

        # Also need to delete any leftover nics
        for nic_data in instance['properties']['networkProfile']['networkInterfaces']:
            nic_name = nic_data['id'].split('/')[-1]
            try:
                nic = conn.networks.getNIC(name=nic_name)
                conn.networks.deleteNIC(name=nic_name)
                # if a public address is associated
                public_addresses = [_['properties']['publicIPAddress']['id'].split('/')[-1] for _ in nic['properties']['ipConfigurations'] if 'publicIPAddress' in _['properties']]
                for public_addr in public_addresses:
                    conn.networks.deletePublicAddress(name=public_addr)
            except Exception as e:
                log.debug("Failed to delete NIC: {}".format(e))

        for rt in conn.networks.listRouteTables():
            for route in rt['properties']['routes']:
                if route['properties']['nextHopType'] != 'VirtualAppliance':
                    continue
                if route['properties']['nextHopIpAddress'] != primary_ip:
                    continue
                try:
                    table_name = route['id'].split('/')[-3]
                    route_name = route['id'].split('/')[-1]
                    r = conn.networks.deleteRoute(table=table_name, name=route_name, retry=ServiceBase.CLOUD_API_RETRIES)
                except Exception as e:
                    log.debug("Failed to delete route: {}".format(e))

    def is_on(self, instance):
        '''Return True if the instance is currently on

            Arguments:
                instance: backend instance
        '''
        status = self.status(instance)
        return status != self.OFF_STATUS and status != self.STOP_STATUS

    def is_off(self, instance):
        '''Return True if the instance is currently off

            Arguments:
                instance: backend instance
        '''
        status = self.status(instance)
        return status == self.OFF_STATUS or status == self.STOP_STATUS

    def name(self, instance):
        '''Returns the instance name (may be different from instance id)

            Arguments:
                instance: backend instance
        '''
        return instance['name']

    def instance_id(self, instance):
        '''Returns the instance id (may be different from instance name)

            Arguments:
                instance: backend instance
        '''
        return instance['name']

    def ip(self, instance):
        '''Return the primary IP address of the instance

            Arguments:
                instance: backend instance
        '''
        conn = self.connection()
        primary_nic_id = instance['properties']['networkProfile']['networkInterfaces'][0]['id'].split('/')[-1]
        primary_nic = conn.networks.getNIC(name=primary_nic_id)
        return primary_nic['properties']['ipConfigurations'][0]['properties']['privateIPAddress']

    def _instance_subnet(self, instance):
        '''Return the subnet of an instance

            Arguments:
                instance: backend instance
        '''
        conn = self.connection()
        nic_id      = instance['properties']['networkProfile']['networkInterfaces'][0]['id'].split('/')[-1]
        nic         = conn.networks.getNIC(name=nic_id)
        subnet_id   = nic['properties']['ipConfigurations'][0]['properties']['subnet']['id'].split('/')[-1]
        return conn.networks.getSubnet(network=self.network, subnet=subnet_id)

    def fqdn(self, instance):
        '''Provide the fully qualified domain name of the instance

            Arguments:
                instance: backend instance
        '''
        return instance['properties']['osProfile']['computerName']

    def status(self, instance):
        '''Return the instance status

            Arguments:
                instance: backend instance
        '''
        conn = self.connection()
        return [_['code'] for _ in conn.vm.instanceView(name=instance['name'])['statuses']]

    def refresh(self, instance):
        '''Refresh the instance from the MS Azure backend

            Arguments:
                instance: backend instance
        '''
        return self.get_instance(instance['name'])

    def can_stop(self, instance):
        '''Check whether this instance configuration can be stopped

            Arguments:
                instance: backend instance
        '''
        return True

    def create_instance(self, machine_type, name, boot_disk_image, other_disks=None, **options):
        '''Create and return an Azure instance

            Arguments:
                machine_type (str): Azure machine type
                name (str): name of the instance
                boot_disk_image (str): the name of the disk image for the root disk
                other_disks ([], optional): Azure disk definitions
                tags (dict, optional): tags to apply to instance
                admin_username (str, optional): defaults to az12345
                admin_password (str, optional): defaults to @Zz12345
                admin_ssh_data (str, optional): SSH key data (used in place of the admin password)
                availability_set (str, optional): availability set name
                network_security_group (str, optional): network security group name
                location (str, optional): Azure location
                root_premium (bool, optional): place root on premium storage (defaults False)
                wait_for_success (int, optional): wait time for the instance to report success (default WAIT_FOR_SUCCESS)
                auto_public_address (bool, optional): auto assign a public address (defaults to False)
        '''
        if not self.valid_instancename(name):
            raise vFXTConfigurationException("{} is not a valid instance name".format(name))
        if machine_type not in self.MACHINE_TYPES:
            raise vFXTConfigurationException("{} is not a valid instance type".format(machine_type))
        if self.get_instance(name):
            raise vFXTConfigurationException("{} exists".format(name))

        conn           = self.connection()
        network        = options.get('network') or self.network
        subnet         = options.get('subnet') or self.subnets[0]
        location       = options.get('location') or self.location
        root_disk_name = '{}-root-{}'.format(name, int(time.time()))
        ip_forward     = options.get('enable_ip_forwarding') or False
        wait_for_success = options.get('wait_for_success') or self.WAIT_FOR_SUCCESS

        # root disk on basic or premium
        root_storage_account = self.storage_account
        if options.get('root_premium') or False:
            root_storage_account = self.premium_storage_account

        # https://msdn.microsoft.com/en-US/library/azure/mt163591.aspx
        body = {
            'name': name,
            'location': location,
            'tags': options.get('tags') or {},
            'properties':{
                'hardwareProfile':{'vmSize':machine_type},
                'networkProfile':{'networkInterfaces':[]},
                'provisioningState': 0,
                'storageProfile': {
                    'dataDisks':[],
                    'osDisk': {
                        'osType': 'Linux',
                        'caching': 'None',
                        'name': root_disk_name,
                        'vhd': {'uri': 'https://{}.blob.core.windows.net/{}/{}.vhd'.format(root_storage_account, self.VHDS_CONTAINER, root_disk_name)},
                    },
                },
                'osProfile':{
                    'computerName': name,
                    'adminUsername': options.get('admin_username') or 'az12345',
                    'adminPassword': options.get('admin_password') or '@Zz12345',
                    'linuxConfiguration': {'disablePasswordAuthentication': False},
                },
            },
        }

        admin_ssh_data = options.get('admin_ssh_data') or None
        if admin_ssh_data:
            del body['properties']['osProfile']['adminPassword']
            body['properties']['osProfile']['linuxConfiguration']['disablePasswordAuthentication'] = True
            ssh_config = {
                'publicKeys': [{
                    'path': '/home/{}/.ssh/authorized_keys'.format(body['properties']['osProfile']['adminUsername']),
                    'keyData': admin_ssh_data
                }]
            }
            body['properties']['osProfile']['linuxConfiguration']['ssh'] = ssh_config

        availability_set = options.get('availability_set') or None
        if availability_set:
            try:
                a_set = conn.availabilitysets.get(name=availability_set)
                body['properties']['availabilitySet'] = {'id': a_set['id']}
            except Exception as e:
                raise vFXTServiceFailure("Failed to lookup availability set {}: {}".format(availability_set, e))

        # make sure we have our two expected containers for our root storage
        containers = conn.blob.listContainers(storage_account=root_storage_account)
        if not isinstance(containers, list):
            containers = [containers]
        for dest in [self.SYSTEM_CONTAINER, self.VHDS_CONTAINER]:
            if dest not in [_['Name'] for _ in containers]:
                conn.blob.createContainer(container=dest, storage_account=root_storage_account)

        # determine where we are getting the root disk
        # if its a url and in our storage account, use it directly
        boot_disk_image_url = urlparse.urlparse(boot_disk_image)
        if boot_disk_image_url.hostname == '{}.blob.core.windows.net'.format(root_storage_account):
            log.info("Using local image {}".format(boot_disk_image))
            body['properties']['storageProfile']['osDisk']['createOption'] = 'FromImage'
            body['properties']['storageProfile']['osDisk']['image'] = {'uri':boot_disk_image}
        # if its some other azure storage account, copy it in
        elif boot_disk_image_url.hostname and boot_disk_image_url.hostname.endswith('blob.core.windows.net'):
            blob_name = 'Microsoft.Compute/Images/{}/{}'.format(self.VHDS_CONTAINER, boot_disk_image_url.path.split('/')[-1])

            # Simple existing check... there may be better ways if we want to invalidate our existing copy
            if blob_name not in [_['Name'] for _ in conn.blob.list(storage_account=root_storage_account, container=self.SYSTEM_CONTAINER)]:
                log.info("Copying {} to {}".format(boot_disk_image, blob_name))
                try:
                    self._copy_blob(boot_disk_image, blob_name, container=self.SYSTEM_CONTAINER, storage_account=root_storage_account)
                except Exception as e:
                    raise vFXTServiceFailure("Failed to copy image {}: {}".format(boot_disk_image, e))

            body['properties']['storageProfile']['osDisk']['createOption'] = 'FromImage'
            local_blob_url = 'https://{}.blob.core.windows.net/{}/{}'.format(root_storage_account, self.SYSTEM_CONTAINER, blob_name)
            body['properties']['storageProfile']['osDisk']['image'] = {'uri':local_blob_url}
        # if its a marketplace path like OpenLogic:CentOS:7.1:latest
        elif boot_disk_image.count(':') == 3: # must be marketplace
            log.info("Using marketplace URN {}".format(boot_disk_image))
            pub,offer,sku,version = boot_disk_image.split(':')
            body['properties']['storageProfile']['imageReference'] = {
                "publisher":pub,
                "offer":offer,
                "sku":sku,
                "version":version
            }
            body['properties']['storageProfile']['osDisk']['createOption'] = 'FromImage'
            del body['properties']['storageProfile']['osDisk']['osType']
        else:
            raise vFXTConfigurationException("Unable to handle boot disk {}".format(boot_disk_image))

        # if we turn on boot diagnostics, log to our non-premium account
        if options.get('enable_boot_diagnostics'):
            body['properties']['diagnosticsProfile'] = {
                'bootDiagnostics': {
                    'enabled': True,
                    'storageUri': 'https://{}.blob.core.windows.net'.format(self.storage_account)}
            }

        # base64 encoded user data
        user_data = options.get('user_data') or None
        if user_data:
            body['properties']['osProfile']['customData'] = user_data.encode('base64').replace('\n','').strip()

        # network interface
        network_security_group = options.get('network_security_group') or self.network_security_group
        public_ip_address = options.get('auto_public_address', False)
        nic = None
        try:
            nic = self._create_nic('{}-1-NIC'.format(name), network, subnet,
                network_security_group=network_security_group, enable_ip_forwarding=ip_forward,
                enable_public_address=public_ip_address)
        except Exception as e:
            log.debug(e)
            raise vFXTServiceFailure("Failed to create NIC: {}".format(e))
        nic_cfg = {'id': nic['id']}
        body['properties']['networkProfile']['networkInterfaces'].append(nic_cfg)

        if other_disks:
            body['properties']['storageProfile']['dataDisks'] = other_disks

        log.debug("Create instance request body: {}".format(body))

        try:
            instance = conn.vm.create(name=name, json=body)
            self.wait_for_status(instance, self.ON_STATUS, wait_for_success)
            return instance
        except Exception as e:
            log.debug("Failed to create instance: {}".format(e))

            try: # it seems we have to manually delete a failed instance
                r = conn.vm.delete(name=name)
                self._wait_for_operation(r.headers['x-ms-request-id'], msg='instance to be destroyed', retries=self.WAIT_FOR_DESTROY)
            except Exception as instance_e:
                log.debug("Failed while cleaning up instance: {}".format(instance_e))

            if public_ip_address:
                try:
                    conn.networks.deletePublicAddress('{}-public-address'.format(name))
                except Exception as addr_e:
                    log.debug("Failed while cleaning up public address: {}".format(addr_e))

            try: # delete nic, disk
                conn.networks.deleteNIC(name='{}-1-NIC'.format(name))
            except Exception as nic_e:
                log.debug("Failed while cleaning up instance NIC: {}".format(nic_e))

            # delete root disk if we did not attach it
            if body['properties']['storageProfile']['osDisk']['createOption'] != 'Attach':
                try:
                    conn.blob.delete(container=self.VHDS_CONTAINER, blob='{}.vhd'.format(root_disk_name))
                except Exception as root_disk_e:
                    log.debug("Failed while cleaning up instance root disk: {}".format(root_disk_e))

            # delete data disks if we have them
            if other_disks:
                for disk in other_disks:
                    vhd_data = self._parse_vhd_uri(disk['vhd']['uri'])
                    try:
                        conn.blob.delete(**vhd_data)
                    except Exception as data_disk_e:
                        log.debug("Failed while cleaning up instance data disk: {}".format(data_disk_e))

            raise vFXTServiceFailure("Create instance failed: {}".format(e))

    def create_node(self, node_name, cfg, node_opts, instance_options):
        '''Create a cluster node

            This is a frontend for create_instance that handles vFXT node specifics

            Arguments:
                node_name (str): name of the node
                cfg (str): configuration string to pass to the node
                node_opts (dict): node creation options
                instance_options (dict): options passed to create_instance

                node_opts include:
                    data_disk_size (int): size of data disks
                    data_disk_count (int): number of data disks
                    data_disk_caching (str, optional): None, ReadOnly, ReadWrite (defaults to None)
                    machine_type (str): machine type
                    root_image (str): VHD ID

        '''
        # XXX weird azure limitation (max size is 1TB but they reject 1024)
        if node_opts['data_disk_size'] > 1023:
            node_opts['data_disk_size'] = 1023
        data_disk_disks = []
        data_disk_caching = node_opts.get('data_disk_caching') or None
        for idx in xrange(node_opts['data_disk_count']):
            disk_name = '{}-data_disk-{}'.format(node_name, idx)
            data_disk_disks.append({
                'name': disk_name,
                'diskSizeGB': node_opts['data_disk_size'],
                'createOption':'Empty',
                'caching': data_disk_caching,
                'vhd': {'uri': 'https://{}.blob.core.windows.net/{}/{}.vhd'.format(self.premium_storage_account, self.VHDS_CONTAINER, disk_name)},
                'lun': str(idx),
            })

        log.info("Creating node {}".format(node_name))
        n = self.create_instance(machine_type=node_opts['machine_type'],
            name=node_name,
            boot_disk_image=node_opts['root_image'],
            other_disks=data_disk_disks,
            user_data=cfg,
            enable_ip_forwarding=True,
            root_premium=True,
            **instance_options
        )
        log.info("Created {} ({})".format(n['name'], self.ip(n)))
        return n

    def create_cluster(self, cluster, **options):
        '''Create a vFXT cluster (calls create_node for each node)
            Typically called via vFXT.Cluster.create()

            Arguments:
                cluster (vFXT.cluster.Cluster): cluster object
                size (int, optional): size of cluster (node count)
                root_image (str, optional): root disk image name
                data_disk_size (int, optional): size of data disk (or machine type default)
                data_disk_count (int, optional): number of data disks (or machine type default)
                data_disk_caching (str, optional): None, ReadOnly, ReadWrite (defaults to None)
                wait_for_state (str, optional): red, yellow, green cluster state (defaults to yellow)
                skip_cleanup (bool, optional): do not clean up on failure
                role_name (str, optional): role name for the service principal (otherwise one is created)
                availability_set (str, optional): existing availability set for the cluster instances
                subnets ([str], optional): one or more subnets
                location (str, optional): location for availability set
                management_address (str, optional): management address for the cluster

                service_principal_id (str, optional): ID of the service principal to provide to the cluster (per cluster override)
                subscription_id (str, optional): Azure subscription identifier (per cluster override)
                tenant_id (str, optional): AD application tenant identifier (per cluster override)
                instance_client_id (str, optional): client ID for instances (per cluster override)
                instance_client_secret (str, optional): client secret for instances (per cluster override)

                Additional arguments are passed through to create_node()

            Raises: vFXTConfigurationException, vFXTCreateFailure
        '''
        machine_type    = cluster.machine_type
        if machine_type not in self.MACHINE_DEFAULTS:
            raise vFXTConfigurationException('{} is not a valid instance type'.format(machine_type))
        machine_defs    = self.MACHINE_DEFAULTS[machine_type]
        cluster_size    = int(options.get('size', machine_defs['node_count']))
        location        = options.get('location') or self.location
        subnets         = options.get('subnets') or self.subnets
        subnets         = [subnets] if isinstance(subnets, basestring) else subnets
        cycle_subnets   = cycle(subnets)

        # authentication information
        subscription_id        = options.get('subscription_id') or self.subscription_id
        tenant_id              = options.get('tenant_id') or self.tenant_id
        instance_client_id     = options.get('instance_client_id') or self.instance_client_id
        instance_client_secret = options.get('instance_client_secret') or self.instance_client_secret
        service_principal_id   = options.get('service_principal_id') or self.instance_service_principal_id

        # disk sizing
        root_image        = options.get('root_image')      or self._get_default_image(location)
        data_disk_size    = options.get('data_disk_size')  or machine_defs['data_disk_size']
        data_disk_count   = options.get('data_disk_count') or machine_defs['data_disk_count']
        data_disk_caching = options.get('data_disk_caching') or None

        # verify our data_disk_size is in self.VALID_DATA_DISK_SIZES
        # https://azure.microsoft.com/en-us/documentation/articles/storage-premium-storage/#premium-storage-features
        if data_disk_size not in self.VALID_DATA_DISK_SIZES:
            raise vFXTConfigurationException('{} is not in the allowed disk size list: {}'.format(data_disk_size, self.VALID_DATA_DISK_SIZES))

        if data_disk_count > self.MAX_DATA_DISK_COUNT:
            raise vFXTConfigurationException('{} exceeds the maximum allowed disk count of {}'.format(data_disk_count, self.MAX_DATA_DISK_COUNT))

        if not all([subscription_id, tenant_id, instance_client_id, instance_client_secret, service_principal_id]):
            raise vFXTConfigurationException('Missing credentials.  Unable to create the cluster.')

        ip_count        = cluster_size + (1 if not options.get('management_address') else 0)
        avail,mask      = self.get_available_addresses(count=ip_count, contiguous=True)
        cluster.mgmt_ip = options.get('management_address') or avail.pop(0)
        cluster_ips     = avail

        # store for cluster config
        cluster.mgmt_netmask     = mask
        cluster.cluster_ip_start = cluster_ips[0]
        cluster.cluster_ip_end   = cluster_ips[-1]

        log.info('Creating cluster configuration')
        cfg     = cluster.cluster_config(expiration=options.get('config_expiration', None))
        joincfg = cluster.cluster_config(joining=True, expiration=options.get('config_expiration', None))
        cfg     += '''\n[EC2 admin credential]''' \
                   '''\nname=vFXT Admin Credential''' \
                   '''\nserviceAccount={2}''' \
                   '''\ntype=azure''' \
                   '''\nsubscription={0}''' \
                   '''\ntenant={1}''' \
                   '''\nclientId={2}''' \
                   '''\nclientSecret={3}''' \
                   .format(subscription_id, tenant_id, instance_client_id, instance_client_secret)
        log.debug("Generated cluster config: {}".format(cfg))
        log.debug("Generated cluster join config: {}".format(joincfg))

        try:
            # create a role if we weren't specified one
            role = options.get('role_name') or None
            if not role:
                role_name = '{}-cluster-role'.format(cluster.name)
                log.info('Creating cluster role {}'.format(role_name))
                cluster.role = self._create_role(role_name)
            else:
                cluster.role = self._get_role(role)
            self._assign_role(service_principal_id, cluster.role['name'])

            # availability set (we can keep creating it as thats just an update operation)
            availability_set = options.get('availability_set') or '{}-availability_set'.format(cluster.name)
            log.info('Creating cluster availability set {}'.format(availability_set))
            self._create_availability_set(availability_set)
            cluster.availability_set = availability_set

            # create the initial node
            name = '{}-{}'.format(cluster.name, 1)
            opts = {'data_disk_count': data_disk_count, 'data_disk_size': data_disk_size, 'data_disk_caching': data_disk_caching,
                    'machine_type': machine_type, 'root_image': root_image,
                    }
            options['subnet'] = next(cycle_subnets)
            n    = self.create_node(name, cfg, node_opts=opts, instance_options=options)
            cluster.nodes.append(ServiceInstance(service=self, instance=n))

            if not options.get('skip_configuration'):
                cluster.first_node_configuration(wait_for_state=options.get('wait_for_state', 'yellow'))

            # Create the rest of the nodes
            nodeq   = Queue.Queue()
            failq   = Queue.Queue()
            threads = []
            def cb(nodenum, inst_opts, nodeq, failq):
                '''callback'''
                try:
                    name = '{}-{}'.format(cluster.name, nodenum)
                    n    = self.create_node(name, joincfg, node_opts=opts, instance_options=inst_opts)
                    nodeq.put(n)
                except Exception as e:
                    failq.put(e)

            for node_num in range(1,cluster_size):
                inst_opts = options.copy()
                inst_opts['subnet'] = next(cycle_subnets)
                t = threading.Thread(target=cb, args=(node_num+1, inst_opts, nodeq, failq,))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            while True:
                try:
                    n = nodeq.get_nowait()
                    cluster.nodes.append(ServiceInstance(service=self, instance=n))
                except Queue.Empty:
                    break

            failed = []
            while True:
                try:
                    failed.append(failq.get_nowait())
                except Queue.Empty:
                    break
            if failed:
                raise Exception(failed)

        except Exception as e:
            log.error("Failed to create node: {}".format(e))
            if not options.get('skip_cleanup', False):
                for n in cluster.nodes:
                    try:
                        n.destroy()
                    except Exception as e:
                        log.debug(e)
                self.post_destroy_cluster(cluster)
            raise vFXTCreateFailure(e)


    def add_cluster_nodes(self, cluster, count, **options):
        '''Add nodes to the cluster (delegates to create_node())

            Arguments:
                cluster (vFXT.cluster.Cluster): cluster object
                count (int): number of nodes to add
                skip_cleanup (bool, optional): do not clean up on failure
                **options: passed to create_node()

            Raises: exceptions from create_node()
        '''
        subnets         = options.get('subnets') or self.subnets
        subnets         = [subnets] if isinstance(subnets, basestring) else subnets
        # make sure to use unused zones first
        unused_subnets  = [z for z in self.subnets if z not in subnets]
        unused_subnets.extend([z for z in subnets if z not in unused_subnets])
        cycle_subnets   = cycle(subnets)

        # extend our service subnets if necessary
        for z in subnets:
            if z not in self.subnets:
                self.subnets.append(z)

        # look at cluster.nodes[0].instance
        instance          = cluster.nodes[0].instance
        data_disk_count   = len(instance['properties']['storageProfile']['dataDisks'])
        data_disk_size    = instance['properties']['storageProfile']['dataDisks'][0]['diskSizeGB']
        data_disk_caching = instance['properties']['storageProfile']['dataDisks'][0]['caching']
        root_image        = instance['properties']['storageProfile']['osDisk']['image']['uri']
        tags              = instance['tags'] if 'tags' in instance else {}
        machine_type      = cluster.machine_type
        availability_set  = cluster.availability_set

        # overrides
        if options.get('machine_type'):
            machine_type = options.pop('machine_type')
        if options.get('root_image'):
            root_image = options.pop('root_image')
        if options.get('data_disk_size'):
            data_disk_size = options.pop('data_disk_size')

        opts         = {'data_disk_size':data_disk_size, 'data_disk_count':data_disk_count, 'data_disk_caching': data_disk_caching,
                        'tags': tags.copy(), 'machine_type':machine_type,
                        'availability_set':availability_set, 'root_image':root_image}

        # Requires cluster be online
        # XXX assume our node name always ends in the node number
        max_node_num = max([int(i.name().split('-')[-1]) for i in cluster.nodes])
        joincfg     = cluster.cluster_config(joining=True)

        nodeq   = Queue.Queue()
        failq   = Queue.Queue()
        threads = []

        def cb(nodenum, inst_opts, nodeq, failq):
            '''callback'''
            try:
                name = '{}-{}'.format(cluster.name, nodenum)
                n = self.create_node(name, joincfg, node_opts=opts, instance_options=inst_opts)
                nodeq.put(n)
            except Exception as e:
                failq.put(e)

        for node_num in xrange(max_node_num, max_node_num+count):
            next_node_num = node_num + 1
            inst_opts = options.copy()
            inst_opts['subnet'] = next(cycle_subnets)
            t  = threading.Thread(target=cb, args=(next_node_num, inst_opts, nodeq, failq,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        nodes = []
        while True:
            try:
                n = nodeq.get_nowait()
                nodes.append(ServiceInstance(service=self, instance=n))
            except Queue.Empty:
                break

        failed = []
        while True:
            try:
                failed.append(failq.get_nowait())
            except Queue.Empty:
                break
        if failed:
            if not options.get('skip_cleanup', False):
                for n in nodes:
                    n.destroy()
            raise Exception(failed)

        cluster.nodes.extend(nodes)

    def post_destroy_cluster(self, cluster):
        '''Post cluster destroy cleanup'''
        try:
            if cluster.role:
                self._delete_role(cluster.role['name'])
        except Exception as e:
            log.debug('Ignoring cleanup error: {}'.format(e))
        try:
            if cluster.availability_set:
                self._delete_availability_set(cluster.availability_set)
        except Exception as e:
            log.debug('Ignoring cleanup error: {}'.format(e))

    def load_cluster_information(self, cluster, **options):
        '''Loads cluster information from the service and cluster itself
        '''
        xmlrpc = cluster.xmlrpc()

        # make sure mgmt_ip is set to the valid address (in case we used
        # a node address to get in)
        cluster.mgmt_ip = xmlrpc.cluster.get()['mgmtIP']['IP']

        node_ips = set([ip['IP']
                        for name in xmlrpc.node.list()
                        for n in [xmlrpc.node.get(name)[name]]
                        if 'clusterIPs' in n
                        for ip in n['clusterIPs'] ])

        # Find instances by address... this is unfortunately not simple
        # no searching.. expensive... hopefully resource group is small
        instances = []
        instance_data = self.find_instances()
        for inst_dict in instance_data:
            address = self.ip(inst_dict)
            if address in node_ips:
                instances.append(inst_dict)

        if instances:
            cluster.nodes = []
            for i in instances:
                cluster.nodes.append(ServiceInstance(service=self, instance=i))

            # subnet info
            cluster.subnets = list(set([self._instance_subnet(i)['name'] for i in instances]))

            # XXX assume all instances have the same settings
            properties               = instances[0]['properties']
            cluster.location         = instances[0]['location']
            cluster.machine_type     = properties['hardwareProfile']['vmSize']
            cluster.availability_set = None
            if 'availabilitySet' in properties:
                cluster.availability_set = properties['availabilitySet']['id'].split('/')[-1]

            cluster.name             = instances[0]['name'][:-2]
            cluster.role             = None
            try: # try and find the cluster role
                # cluster.role = self._get_role('{}-cluster-role'.format(cluster.name))
                conn = self.connection()
                roles = [_ for _ in conn.rbac.listRoles() if _['properties']['roleName'].startswith('{}-cluster-role'.format(cluster.name))]
                # if we only find one role prefixed with the cluster name (with maybe a timestamp afterwards)
                if roles and len(roles) == 1:
                    cluster.role = self._get_role(roles[0]['properties']['roleName'])
            except Exception as e:
                log.debug("Failed trying to lookup cluster role: {}".format(e))

            # try and find the network security group
            try:
                nic_name = properties['networkProfile']['networkInterfaces'][0]['id'].split('/')[-1]
                nic = self.connection().networks.getNIC(name=nic_name)
                if 'networkSecurityGroup' in nic['properties']:
                    cluster.service.network_security_group = nic['properties']['networkSecurityGroup']['id'].split('/')[-1]
            except Exception as e:
                log.debug("Failed trying to lookup network security group: {}".format(e))

    def _commit_instance(self, instance):
        '''Commit changes to the instance with the backend

            Arguments:
                instance: backend instance

            Returns an updated backend instance
        '''
        try:
            return self.connection().vm.create(name=instance['name'], json=instance)
        except Exception as e:
            raise vFXTServiceFailure("Failed to commit instance changes: {}".format(e))

    def shelve(self, instance):
        ''' shelve the instance; shut it down, detach and delete
            all non-root block devices

            Arguments:
                instance: backend instance
            Raises: vFXTServiceFailure
        '''
        instance = self.refresh(instance)
        if not self.can_shelve(instance):
            raise vFXTConfigurationException("Node configuration prevents them from being shelved")
        conn = self.connection()

        if self.is_on(instance):
            self.stop(instance)
            instance = self.refresh(instance)

        if not instance['properties']['storageProfile']['dataDisks']:
            log.info("No non-root volumes for instance {}, already shelved?".format(instance['name']))
            return
        data_disk_count   = len(instance['properties']['storageProfile']['dataDisks'])
        data_disk_size    = instance['properties']['storageProfile']['dataDisks'][0]['diskSizeGB']
        data_disk_caching = instance['properties']['storageProfile']['dataDisks'][0]['caching']

        data_disks = instance['properties']['storageProfile']['dataDisks']
        # We could look at each disk and make sure it is using a premium storage
        # account using _parse_vhd_uri()['storage_account'] and storageaccounts.get(name='')
        # but its really overkill... just remove all of the data disks.
        instance['properties']['storageProfile']['dataDisks'] = []
        instance = self._commit_instance(instance)
        self.wait_for_status(instance, self.OFF_STATUS)

        # delete the disk blobs
        errors = ShelveErrors()
        failed = []
        for disk in data_disks:
            vhd_data = self._parse_vhd_uri(disk['vhd']['uri'])
            try:
                conn.blob.delete(**vhd_data)
            except Exception as e:
                log.debug(e)
                failed.append(vhd_data['blob'])
        if failed:
            errors['notdeleted'] = ','.join(failed)

        shelved = "{}|{}|{}".format(data_disk_count, data_disk_size, data_disk_caching)
        if errors:
            shelved += '|{}'.format(errors)

        # tag and commit our instance metadata to the backend
        try:
            if 'tags' not in instance:
                instance['tags'] = {}
            instance['tags']['shelved'] = shelved
            instance = self._commit_instance(instance)
            self.wait_for_status(instance, self.OFF_STATUS)
        except Exception as e:
            log.debug(e)
            raise vFXTServiceFailure("Failed to shelve instance {}: {}".format(instance['name'], e))

    def can_shelve(self, instance):
        ''' Some instance configurations cannot be shelved. Check if this is one.

            Arguments:
                instance: backend instance
        '''
        return True

    def is_shelved(self, instance):
        '''Return True if the instance is currently shelved

            Arguments:
                instance: backend instance
        '''
        try:
            if 'tags' in instance and 'shelved' in instance['tags']:
                return True
        except Exception as e:
            log.debug(e)
        return False

    def unshelve(self, instance, count_override=None, size_override=None, type_override=None):
        ''' bring our instance back to life.  This requires a tag called
            shelved that contains the number of disks and their size/type

            Arguments:
                instance: backend instance
                count_override (int, optional): number of data disks
                size_override (int, optional): size of data disks
                type_override (str, optional): type of data caching

            Raises: vFXTServiceFailure
        '''
        instance = self.refresh(instance)
        if not self.is_shelved(instance):
            log.info( "{} does not have shelved tag, skipping".format(instance['name']))
            return

        # check that instance is already stopped
        if self.is_on(instance):
            log.info("{} is not stopped, skipping".format(instance['name']))
            return

        try:
            attrs = instance['tags']['shelved'].split('|')
            data_disk_count, data_disk_size, data_disk_caching = attrs[0:3]
        except:
            log.error("{} does not have data in the shelved tag".format(instance['name']))
            return

        if count_override:
            data_disk_count = count_override
        if size_override:
            data_disk_size = size_override
        if type_override:
            data_disk_caching = type_override

        data_disks = []
        for idx in xrange(int(data_disk_count)):
            disk_name = '{}-data_disk-{}'.format(self.name(instance), idx)
            # TODO maybe we could check shelve error for disk, query it exists
            # and use createOption: Attach
            data_disks.append({
                'name': disk_name,
                'diskSizeGB': data_disk_size,
                'createOption':'Empty',
                'caching': data_disk_caching,
                'vhd': {'uri': 'https://{}.blob.core.windows.net/{}/{}.vhd'.format(self.premium_storage_account, self.VHDS_CONTAINER, disk_name)},
                'lun': str(idx),
            })
        try:
            instance['properties']['storageProfile']['dataDisks'] = data_disks
            del instance['tags']['shelved']
            instance = self._commit_instance(instance)
        except Exception as e:
            log.debug(e)
            raise vFXTServiceFailure("Failed to shelve instance {}: {}".format(instance['name'], e))
        self.start(instance)

    def create_bucket(self, name):
        # XXX TODO storage/buckets
        raise NotImplementedError()
    def delete_bucket(self, name):
        # XXX TODO storage/buckets
        raise NotImplementedError()
    def authorize_bucket(self, cluster, name, retries=ServiceBase.CLOUD_API_RETRIES):
        # XXX TODO storage/buckets
        raise NotImplementedError()

    def get_default_router(self, subnet_id=None):
        '''Get default route address

            Arguments:
                subnet_id (str): subnet id (optional if given to constructor)
            Returns:
                str: address of default router
        '''
        subnet_id   = subnet_id or self.subnets[0]
        conn        = self.connection()
        subnet      = conn.networks.getSubnet(network=self.network, subnet=subnet_id)
        c           = Cidr(subnet['properties']['addressPrefix'])
        return c.to_address(c.start()+1)

    def get_dns_servers(self):
        '''Get DNS server addresses
        '''
        # maybe check .networks.getNIC(name='...nic...')['properties']['dnsSettings']
        # {u'dnsServers': [], u'appliedDnsServers': []}
        return self.DNS_SERVERS

    def get_ntp_servers(self):
        '''Get NTP server addresses
        '''
        return self.NTP_SERVERS

    def get_available_addresses(self, count=1, contiguous=False, addr_range=None, in_use=None):
        '''Returns a list of available addresses for the given range
            Arguments:
                count (int, optional): number of addresses required
                contiguous (bool=False): addresses must be contiguous
                addr_range (str, optional): address range cidr block
                in_use ([str], optional): list of addresses known to be used

            Returns:
                ([], str): tuple of address list and netmask str

            Raises: vFXTConfigurationException
        '''
        conn       = self.connection()
        addr_range = addr_range or self.private_range
        netmask    = '255.255.255.255'

        if not addr_range:
            network       = conn.networks.getNetwork(network=self.network)
            network_range = network['properties']['addressSpace']['addressPrefixes'][0]
            network_c     = Cidr(network_range)
            addr_range    ='{}/{}'.format(Cidr.to_address(network_c.end()+1),
                                network_range.split('/')[-1])

        used = self.in_use_addresses(addr_range)
        if in_use:
            used.extend(in_use)
            used = list(set(used))

        try:
            addr_cidr = Cidr(addr_range)
            avail     = addr_cidr.available(count, contiguous, used)
            if not netmask:
                netmask   = addr_cidr.netmask
            return (avail, netmask)
        except Exception as e:
            raise vFXTConfigurationException(e)

    def add_instance_address(self, instance, address, **options):
        '''Add a new route to the instance

            Arguments:
                instance: backend instance
                address (str): IP address
                route_table (str, optional): route table for route
                allow_reassignment (bool, optional): defaults to True

            Raises: vFXTServiceFailure
        '''
        if address in self.instance_in_use_addresses(instance):
            raise vFXTConfigurationException("{} already assigned to {}".format(address, self.name(instance)))

        conn = self.connection()

        try:
            route_table = options.get('route_table') or None
            if not route_table:
                subnet = self._instance_subnet(instance)
                if 'routeTable' not in subnet['properties']:
                    raise vFXTConfigurationException("Unable to find a route table")
                route_table = subnet['properties']['routeTable']['id'].split('/')[-1]

            dest = '{}/32'.format(address)
            addr = Cidr(dest)
            addr_name = '{}-{}'.format(self.name(instance), addr.address.replace('.', '-'))

            # check for existing
            existing = []
            for rt in conn.networks.listRouteTables():
                for route in rt['properties']['routes']:
                    if route['properties']['nextHopType'] != 'VirtualAppliance':
                        continue
                    if route['properties']['addressPrefix'] == dest:
                        existing.append(route)
            if existing:
                if not options.get('allow_reassignment', True):
                    raise vFXTConfigurationException("Route already assigned for {}".format(dest))
                for route in existing:
                    table_name = route['id'].split('/')[-3]
                    route_name = route['id'].split('/')[-1]
                    log.debug("Removing existing route {}".format(route_name))
                    r = conn.networks.deleteRoute(table=table_name, name=route_name, retry=ServiceBase.CLOUD_API_RETRIES)
                    log.debug(r)

            # add the route
            body = {
                'properties': {
                    'addressPrefix': dest,
                    'nextHopType': 'VirtualAppliance',
                    'nextHopIpAddress': self.ip(instance)
                }
            }
            r = conn.networks.createRoute(table=route_table, name=addr_name, json=body)
            log.debug(r)
            return r
        except vFXTConfigurationException:
            raise
        except Exception as e:
            log.debug(e)
            raise vFXTServiceFailure("Failed to add route for {}: {}".format(address, e))
        # TODO retry on 409 conflict errors?
        # XXX is there something to wait for?

    def remove_instance_address(self, instance, address):
        '''Remove an instance route address

            Arguments:
                instance: backend instance
                address (str): IP address

            Raises: vFXTServiceFailure
        '''
        conn = self.connection()
        primary_ip = self.ip(instance)

        if address not in self.instance_in_use_addresses(instance):
            raise vFXTConfigurationException("{} is not assigned to {}".format(address, self.name(instance)))

        to_remove = []
        for rt in conn.networks.listRouteTables():
            for route in rt['properties']['routes']:
                if route['properties']['nextHopType'] != 'VirtualAppliance':
                    continue
                if route['properties']['nextHopIpAddress'] != primary_ip:
                    continue
                addr = Cidr(route['properties']['addressPrefix']).address
                if addr == address:
                    to_remove.append(route)

        if to_remove:
            try:
                for route in to_remove:
                    table_name = route['id'].split('/')[-3]
                    route_name = route['id'].split('/')[-1]
                    r = conn.networks.deleteRoute(table=table_name, name=route_name, retry=ServiceBase.CLOUD_API_RETRIES)
                    log.debug(r)
            except Exception as e:
                log.debug(e)
                raise vFXTServiceFailure("Failed to remove route for {}".format(address))
        # TODO retry on 409 conflict errors?

    def in_use_addresses(self, cidr_block):
        '''Return a list of in use addresses within the specified cidr

            Arguments:
                cidr_block (str)
        '''
        conn        = self.connection()
        c           = Cidr(cidr_block)
        addresses   = set()
        nics        = conn.networks.listNICs() # faster to fetch all up front

        for instance in self.find_instances():
            try:
                for iface in instance['properties']['networkProfile']['networkInterfaces']:
                    iface_id = iface['id'].split('/')[-1]
                    # search prefetched nic list
                    interface = next((_ for _ in nics if _['name'] == iface_id), None)
                    if not interface:
                        continue

                    for ipconfig in interface['properties']['ipConfigurations']:
                        if 'privateIPAddress' in ipconfig['properties']:
                            addr = ipconfig['properties']['privateIPAddress']
                            if c.contains(addr):
                                addresses.add(addr)
            except Exception as e:
                log.debug("Ignoring exception: {}".format(e))
                pass # sometimes old instances show up for a while

        for rt in conn.networks.listRouteTables():
            for route in rt['properties']['routes']:
                if route['properties']['nextHopType'] != 'VirtualAppliance':
                    continue
                addr = Cidr(route['properties']['addressPrefix']).address
                if c.contains(addr):
                    addresses.add(addr)

        return list(addresses)

    def instance_in_use_addresses(self, instance, category='all'):
        '''Get the in use addresses for the instance

            Arguments:
                instance (dict)
                category (str): all, instance, routes

            To obtain the public instance address, use 'public' category.  This
            is not included with 'all'.
        '''
        addresses = set()
        conn = self.connection()

        if category in ['all', 'instance']:
            for iface in instance['properties']['networkProfile']['networkInterfaces']:
                iface_id = iface['id'].split('/')[-1]
                interface = conn.networks.getNIC(name=iface_id)
                for ipconfig in interface['properties']['ipConfigurations']:
                    if 'privateIPAddress' in ipconfig['properties']:
                        addresses.add(ipconfig['properties']['privateIPAddress'])

        if category in ['all', 'routes']:
            primary_ip = self.ip(instance)
            for rt in conn.networks.listRouteTables():
                for route in rt['properties']['routes']:
                    if route['properties']['nextHopType'] != 'VirtualAppliance':
                        continue
                    if route['properties']['nextHopIpAddress'] == primary_ip:
                        addr = Cidr(route['properties']['addressPrefix']).address
                        addresses.add(addr)

        # for special requests
        if category == 'public':
            for iface in instance['properties']['networkProfile']['networkInterfaces']:
                iface_id = iface['id'].split('/')[-1]
                interface = conn.networks.getNIC(name=iface_id)
                for ipconfig in interface['properties']['ipConfigurations']:
                    if 'publicIPAddress' in ipconfig['properties']:
                        public_ip_cfg = ipconfig['properties']['publicIPAddress']['id'].split('/')[-1]
                        public_addr = conn.networks.getPublicAddress(name=public_ip_cfg)
                        if public_addr and 'ipAddress' in public_addr['properties']:
                            addresses.add(public_addr['properties']['ipAddress'])

        return list(addresses)

    def export(self):
        '''Export the service object in an easy to serialize format
            Returns:
                {}: serializable dictionary
        '''
        data = {
            'subscription_id': self.subscription_id,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'tenant_id': self.tenant_id,
            'resource_group': self.resource_group,
            'storage_account': self.storage_account,
            'location': self.location,
            'network': self.network,
            'subnet': self.subnets,
            'proxy_uri': self.proxy_uri,
            'premium_storage_account': self.premium_storage_account,
            'instance_client_id': self.instance_client_id,
            'instance_client_secret': self.instance_client_secret,
            'instance_service_principal_id': self.instance_service_principal_id,
            'private_range': self.private_range,
            'network_security_group': self.network_security_group,
        }
        return data

    def valid_bucketname(self, name):
        '''Validate the bucket name

            Returns: bool
        '''
        return False

    def valid_instancename(self, name):
        '''Validate the instance name

            Returns: bool
        '''
        if not ServiceBase.valid_instancename(self, name):
            return False
        if len(name) > 64 or len(name) < 1:
            return False
        if self.INSTANCENAME_RE.match(name):
            return True
        return False

    def _copy_blob(self, src, dest_blob, container=None, storage_account=None, timeout=ServiceBase.WAIT_FOR_SERVICE_CHECKS):
        '''
            Copy a blob from a source URL to a local blob

            Arguments:
                src (str): the source URL of the blob (typically Avere SAS image)
                dest_blob (str): blob name
                container (str): container for the destination blob
                storage_account (str, optional): the storage account to use
                timeout (int, optional): timeout for the copy operation
        '''
        conn = self.connection()
        container = container or self.VHDS_CONTAINER
        log.debug("Copying {} to {} in container {}".format(src, dest_blob, container))
        storage_account = storage_account or self.storage_account

        containers = conn.blob.listContainers(storage_account=storage_account)
        if not isinstance(containers,list):
            containers = [containers]
        if container not in [_['Name'] for _ in containers]:
            conn.blob.createContainer(storage_account=storage_account, container=container)

        copy_response = conn.blob.copy(storage_account=storage_account, container=container, blob=dest_blob, headers={'x-ms-copy-source':src})
        status = conn.blob.getProperties(storage_account=storage_account, container=container, blob=dest_blob, headers={'x-ms-copy-id':copy_response['x-ms-copy-id']})

        stall_count = 0
        last_progress = None
        rate_limit = 0
        while status['x-ms-copy-status'] != 'success':
            try:
                status = conn.blob.getProperties(storage_account=storage_account, container=container, blob=dest_blob, headers={'x-ms-copy-id':copy_response['x-ms-copy-id']})
            except Exception as e:
                log.error('Failed to get blob properties: {}'.format(e))
                raise
            if rate_limit == 10:
                log.debug('{}: {}'.format(status['x-ms-copy-status'],status['x-ms-copy-progress']))
                rate_limit = 0

            # check for stalled
            if last_progress == status['x-ms-copy-progress']:
                stall_count += 1
            else:
                stall_count = 0
                last_progress = status['x-ms-copy-progress']
            if stall_count == timeout:
                raise vFXTServiceTimeout("Failed waiting for {} to copy".format(dest_blob))

            rate_limit += 1
            time.sleep(self.POLLTIME)

    def _create_nic(self, name, network=None, subnet=None, location=None, private_address=None,
                    enable_ip_forwarding=False, network_security_group=None, enable_public_address=False):
        conn = self.connection()
        network = network or self.network
        subnet = subnet or self.subnets[0]
        location = location or self.location
        subnet_url = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'
        data = {
            'location':location,
            'properties':{
                'enableIPForwarding': enable_ip_forwarding,
                'ipConfigurations':[
                    {
                        'name':'ipconfig-{}-{}'.format(name, int(time.time())),
                        'properties':{
                            'subnet':{'id':subnet_url.format(self.subscription_id, self.resource_group, network, subnet)}
                        }
                    }
                ]
             }
        }
        if private_address:
            data['properties']['ipConfigurations'][0]['properties']['privateIPAllocationMethod'] = 'Static'
            data['properties']['ipConfigurations'][0]['properties']['privateIPAddress'] = private_address
        else:
            data['properties']['ipConfigurations'][0]['properties']['privateIPAllocationMethod'] = 'Dynamic'

        if enable_public_address:
            body = {
                'location': self.location,
                'properties': {'publicIPAllocationMethod': 'Dynamic'}
            }
            # create it
            public_address = conn.networks.createPublicAddress(name='{}-public-address'.format(name), json=body)

            # make sure it succeeded
            retries = ServiceBase.CLOUD_API_RETRIES
            while public_address['properties']['provisioningState'] != 'Succeeded':
                retries -= 1
                if retries == 0:
                    public_address = None
                    break
                time.sleep(self.POLLTIME)
                public_address = conn.networks.getPublicAddress(name='{}-public-address'.format(name))
            if public_address: # if successful, assign it to our nic
                log.debug("Created {}-public-address".format(name))
                data['properties']['ipConfigurations'][0]['properties']['publicIPAddress'] = {'id': public_address['id']}
            else:
                # TODO make this fatal?
                log.error("Failed to create {}-public-address".format(name))

        if network_security_group:
            nsg_url = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/networkSecurityGroups/{}'
            data['properties']['networkSecurityGroup'] = {
                'id': nsg_url.format(self.subscription_id, self.resource_group, network_security_group),
            }

        conn.networks.createNIC(name=name, json=data)
        return conn.networks.getNIC(name=name)

    def _create_role(self, name, **options):
        '''Create an Azure role

            Arguments:
                name (str): role name
                permissions ([{}]): permissions for role (defaults to vFXT.msazure.ROLE_PERMISSIONS)

            Returns
                role dictionary

            Raises: vFXTServiceFailure
        '''
        conn = self.connection()

        role_id     = str(uuid.uuid4())
        sub_id      = self.subscription_id
        rgroup      = self.resource_group
        permissions = options.get('permissions') or self.ROLE_PERMISSIONS

        body = {
            'name': name,
            'properties': {
                'roleName': name,
                'type': 'CustomRole',
                'assignableScopes': ['/subscriptions/{}/ResourceGroups/{}'.format(sub_id, rgroup)],
                'description': 'Automatically created for Avere {}'.format(name),
                'permissions': permissions,
            }
        }

        try:
            r = conn.rbac.createRole(id=role_id, json=body)
            log.debug("Created role {} with body {}".format(role_id, body))
            return r
        except Exception as e:
            log.debug(e)
            raise vFXTServiceFailure("Failed to create role {}: {}".format(name, e))

    def _get_role(self, role):
        conn = self.connection()
        roles = [_ for _ in conn.rbac.listRoles()
                    if role in [_['name'], _['properties']['roleName']]]
        if not roles:
            raise vFXTConfigurationException("Role {} not found".format(role))
        return roles[0]

    def _delete_role(self, role):
        '''Delete an Azure role

            Arguments:
                role (str): role ID or role name

            Raises: vFXTServiceFailure
        '''
        conn = self.connection()

        r = self._get_role(role)
        try:
            # must delete assignments first
            assignments = [_ for _ in conn.rbac.listAssignments() if _['properties']['roleDefinitionId'].endswith(r['name'])]
            for assignment in assignments:
                conn.rbac.deleteAssignment(id=assignment['name'])

            conn.rbac.deleteRole(id=r['name'])
        except Exception as e:
            log.debug(e)
            raise vFXTServiceFailure("Failed to delete role {}: {}".format(role, e))

    def _assign_role(self, principal, role):
        '''Assign a role to a service principal

            Arguments:
                principal (str): principal ID
                role (str): role ID or name to use

            Raises: vFXTServiceFailure
        '''
        conn = self.connection()
        association_id = str(uuid.uuid4())
        role = self._get_role(role)
        assignments = [_ for _ in conn.rbac.listAssignments() if _['properties']['roleDefinitionId'].endswith(role['name'])]
        if principal in [_['properties']['principalId'] for _ in assignments]:
            log.debug("Assignment for role {} and principal {} exists.".format(role['properties']['roleName'], principal))
            return

        body = {'properties': {
            'roleDefinitionId': role['id'],
            'principalId': principal
        }}

        try:
            r = conn.rbac.createAssignment(id=association_id, json=body)
            log.debug("Assigned role {} with principal {}: {}".format(role, principal, body))
            return r
        except Exception as e:
            log.debug(e)
            raise vFXTServiceFailure("Failed to assign role {}: {}".format(role['name'], e))

    def _create_availability_set(self, name, **options):
        '''Create an availability set

            Arguments:
                name (str): availability set name
                location (str, optional): location for availability set

            Raises: vFXTServiceFailure
        '''
        conn = self.connection()

        body = {
            'name': name,
            'type': 'Microsoft.Compute/availabilitySets',
            'location': options.get('location') or self.location
        }
        try:
            availability_set = conn.availabilitysets.create(name=name, json=body)
            return availability_set
        except Exception as e:
            raise vFXTServiceFailure("Failed to create availability set {}: {}".format(name, e))

    def _delete_availability_set(self, name, **options):
        '''Delete an availability set

            Arguments:
                name (str): availability set name

            Raises: vFXTServiceFailure
        '''
        conn = self.connection()
        try:
            r = conn.availabilitysets.delete(name=name)
            return r
        except Exception as e:
            raise vFXTServiceFailure("Failed to delete availability set {}: {}".format(name, e))

    def _location_names(self):
        '''Get a list of location names
            Returns: list
        '''
        conn = self.connection()
        return [_['name'] for _ in conn.listLocations()]

    def _parse_vhd_uri(self, vhd_uri):
        '''Parse the VHD URI

            Returns {'storage_account': '', 'container': '', 'blob':''}
        '''
        parts = vhd_uri.split('/')
        storage_account = parts[2].split('.')[0]
        container = parts[3]
        blob = '/'.join(parts[4:])
        return {'storage_account':storage_account, 'container': container, 'blob': blob}

    @classmethod
    def _list_subscriptions(cls, tenant_id, client_id, client_secret):
        '''Get a list of subscriptions tied to the client/tenant

            Arguments:
                tenant_id (str): AD application tenant identifier
                client_id (str): AD application client ID
                client_secret (str): Client secret
        '''
        conn = vFXT.azureutils.AzureApi(client_id=client_id, client_secret=client_secret, tenant=tenant_id, timeout=CONNECTION_TIMEOUT)
        return list(conn.listSubscriptions())

    def _cache_to_disk_config(self, cache_size, machine_type=None, disk_type=None):
        '''For a given cache size, output the default data disk count and size

            Arguments:
                cache_size (int): vFXT cluster node cache size
                machine_type (str, optional): vFXT cluster node machine type
                disk_type (str, optional): vFXT cluster node disk type

            Returns:
                tuple (disk count, size per disk)
        '''
        assert cache_size > 0
        sizes = sorted(self.VALID_DATA_DISK_SIZES, reverse=True)

        size = 0
        for sz in sizes:
            if cache_size < sz: continue
            if cache_size % sz == 0:
                size = sz
                break
        # If it wasn't a perfect multiple of one of the sizes, choose
        # the closest match and round up
        if not size:
            for i in reversed(range(len(sizes))):
                if cache_size <= sizes[i]:
                    size = sizes[i]
                    break
        # If the cache is bigger than the biggest disk, just use the
        # big disks.
        if not size:
            size = sizes[0]

        count = int((cache_size+size-1) / size)
        return tuple([count, size])

    def _get_network(self):
        '''Return the current network
        '''
        conn = self.connection()
        return conn.networks.getNetwork(network=self.network)

    def _list_storage_accounts(self):
        '''Return a list of storage accounts
        '''
        conn = self.connection()
        return conn.storageaccounts.list()

    def _get_default_image(self, location):
        '''Get the default image from the defaults

            Arguments:
                location (str, optional): Azure location

            This may not be available if we are unable to fetch the defaults.
        '''
        try:
            return self.defaults[location]['current']
        except:
            raise vFXTConfigurationException("You must provide a root disk image.")


