# -*- coding: utf-8 -*-
'''
Created on Oct 17, 2016

@author: davidlepage
'''
import logging
from smc import session
from smc.policy.layer3 import FirewallPolicy, FirewallTemplatePolicy,\
    FirewallSubPolicy
from smc.base.model import prepared_request, Meta, ElementLocator, Element,\
    ElementFactory, Registry, lookup_class, SubElement, ElementCreator,\
    ElementBase, SimpleElement, load_element
from smc.elements.service import TCPService, EthernetService, IPService,\
    UDPService
from smc.core.engine import Engine, InternalGateway, InternalEndpoint,\
    VirtualResource
from smc.core.contact_address import ContactAddress
from smc.core.interfaces import PhysicalInterface, \
    SingleNodeInterface, PhysicalVlanInterface, TunnelInterface, Interface,\
    _interface_helper, InterfaceModifier, InterfaceBuilder
from smc.elements.helpers import zone_helper, location_helper,\
    logical_intf_helper, domain_helper
from smc.core.sub_interfaces import NodeInterface, SubInterface,\
    CaptureInterface, ClusterVirtualInterface, InlineInterface,\
    _add_vlan_to_inline, LoopbackInterface
from smc.elements.other import Category, AdminDomain, CategoryTag
from smc.core.engines import Layer3Firewall, Layer2Firewall, MasterEngineCluster,\
    FirewallCluster
from smc.core import sub_interfaces
from smc.api.common import SMCRequest, fetch_json_by_href, fetch_entry_point,\
    fetch_no_filter
from smc.elements.network import Network, IPList, Alias, Host, Router,\
    AddressRange, URLListApplication, DomainName
from smc.api.exceptions import ElementNotFound, CreateElementFailed,\
    ActionCommandFailed, DeleteElementFailed, EngineCommandFailed,\
    FetchElementFailed, ModificationFailed, UpdateElementFailed,\
    InvalidSearchFilter, ConfigLoadError, ResourceNotFound
from smc.policy.rule_elements import LogOptions, Action, AuthenticationOptions, Source,\
    MatchExpression
from smc.policy.rule import _rule_common, IPv4Rule, EthernetRule, IPv6Rule, Rule
from smc.policy.layer2 import Layer2Policy
from smc.base.util import find_link_by_name, find_type_from_self, merge_dicts,\
    element_resolver
from smc.elements.user import ApiClient, AdminUser
from smc.vpn.policy import VPNPolicy
from smc.policy.ips import IPSPolicy
from smc.routing.ospf import OSPFArea, OSPFProfile
from collections import namedtuple
from smc.administration.access_rights import AccessControlList, Permission
from smc.base.mixins import UnicodeMixin
from smc.administration.tasks import Task, task_history
from smc.policy.file_filtering import FileFilteringPolicy
from smc.policy.rule_nat import IPv4NATRule, NATRule
from smc.administration.updates import UpdatePackage
from _collections import defaultdict
from smc.elements.servers import ManagementServer, ServerContactAddress,\
    LogServer
from smc.routing.prefix_list import IPPrefixList, IPv6PrefixList
from smc.routing.access_list import IPAccessList
from smc.core.properties import SandboxService
from smc.routing.bgp import AutonomousSystem, BGPProfile, ExternalBGPPeer,\
    BGPPeering, BGPConnectionProfile
from smc.vpn.elements import GatewaySettings, ExternalGateway, VPNSite
from lib2to3.fixer_util import parenthesize
from smc.core.node import Node
from smc.elements.netlink import StaticNetlink, Multilink, multilink_member
from smc.elements.group import Group
from smc.administration.role import Role
from smc.base.collection import Search
from smc.base.decorators import cached_property
from smc.administration.license import License
from smc.api.session import get_api_base, get_entry_points,\
    available_api_versions, get_api_version, _EntryPoint
import base64
from smc.api.configloader import load_from_environ
from smc.core.engine_vss import VSSContainer, VSSContext, SecurityGroup,\
    VSSContainerNode
from pip._vendor.retrying import MAX_WAIT
from smc.core.waiters import ConfigurationStatusWaiter
from smc.elements import network
from _codecs import encode


logger = logging.getLogger(__name__)


def get_options_for_link(link):
    r = session.session.options(link)
    headers = r.headers['allow']
    allowed = []
    if headers:
        for header in headers.split(','):
            if header.replace(' ', '') != 'OPTIONS':
                allowed.append(header)
    return allowed

def head_request(link):
    r = session.session.head(link)
    print(vars(r))

if __name__ == '__main__':

    import time
    from pprint import pprint
    start_time = time.time()
    logging.getLogger()
    logging.basicConfig(
        level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s.%(funcName)s: %(message)s')
    #logging.basicConfig(filename='/Users/davidlepage/example.log', filemode='w', level=logging.DEBUG)
    #session.login(url='https://172.18.1.25:8082', api_key='avUj6vFZTUSZ7sr8mNsP0001', timeout=120,
    #              verify=False)

    #session.login(url='https://172.18.1.151:8082',
    #              api_key='vsMoA3eb9kB9pvN6vJBLMBNX', timeout=30,
    #              verify=False, beta=True)
    session.login(url='http://172.18.1.26:8082', api_key='kKphtsbQKjjfHR7amodA0001', timeout=45,
                  beta=True)
    #session.login(url='http://172.18.1.150:8082', api_key='EiGpKD4QxlLJ25dbBEp20001', timeout=30,
    #              domain='foo')
    #session.login()

    """@type engine: Engine"""
    #engine = Engine('ve-1')

    engine = Engine('vm')

    class ProbingProfile(Element):
        typeof = 'probing_profile'
        def __init__(self, name, **meta):
            super(ProbingProfile, self).__init__(name, **meta)

    class ThirdPartyMonitoring(object):
        def __init__(self, log_server=None, probing_profile=None,
                     netflow=False, snmp_trap=False):

            if not log_server:
                log_server = LogServer.objects.first()

            self.monitoring_log_server_ref = element_resolver(log_server)

            if not probing_profile:
                probing_profile = ProbingProfile.objects.filter('Ping').first()

            self.probing_profile_ref = element_resolver(probing_profile)

            self.netflow = netflow
            self.snmp_trap = snmp_trap

        def __call__(self):
            return vars(self)


    #host.third_party_monitoring = ThirdPartyMonitoring()
    #print(vars(host))
    #host.update()

    #t = ThirdPartyMonitoring()
    #host.third_party_monitoring = t


    #print("Finished polling, result is: %s" % poller.result())
    vss_def = {"isc_ovf_appliance_model": 'virtual',
               "isc_ovf_appliance_version": '',
               "isc_ip_address": '1.1.1.1',
               "isc_vss_id": 'foo',
               "isc_virtual_connector_name": 'smc-python'}

    vss_node_def = {
            'management_ip': '4.4.4.6',
            'management_netmask': '24',
            'isc_hypervisor': 'default',
            'management_gateway': '2.2.2.1',
            'contact_ip': None}


    v = VSSContainer('myfirewall')
    
    import hashlib
    import binascii
    
    def encrypt(password):
        secretkey = "HG58YZ3CR9".encode('UTF-8', 'strict')
        print("Encoded string: %s" % secretkey)
        
        # Get the md5 digest of the secret key, 16 bytes
        m = hashlib.md5()
        m.update(secretkey)
        
        message_digest = m.digest()
        print("Key Digest (bytes): %s" % message_digest)
        assert m.digest_size == 16
        print("Key as hex: %s" % binascii.hexlify(message_digest))
        
        # Pad the 16 byte message to 24 bytes using the 8 bytes from the beginning
        # padded to the end of the buffer
        message_digest_ba = bytearray(message_digest)
        print("Byte array: %s" % message_digest_ba)
        slice_of_ba = message_digest_ba[0:8]
        print("Slice of byte array in hex: %s"  % binascii.hexlify(slice_of_ba))
        message_digest_ba.extend(slice_of_ba)
        assert len(message_digest_ba) == 24
        print("Byte array after extension: %s" % message_digest_ba)
        print("Slice of byte array in hex: %s"  % binascii.hexlify(message_digest_ba))
        print("Byte array to bytes: %s" % bytes(message_digest_ba))
        
        import pyDes
        k = pyDes.triple_des(
            key=message_digest_ba, 
            mode=pyDes.CBC, 
            IV=b"\0\0\0\0\0\0\0\0",
            pad=None,
            padmode=pyDes.PAD_PKCS5)
        
        encrypted = k.encrypt(password)
        print("Encrypted byte cipher: %s" % encrypted)
        b64cipher = base64.b64encode(encrypted)
        print("Base64 encoded cipher: %s" % b64cipher)
        return b64cipher
    
    #mypassword = 'password'
    
    #encrypted = k.encrypt(mypassword)
    #print("Encrypted cipher: %s" % encrypted)
    #print("Base64 encoded cipher: %s" % base64.b64encode(encrypted))
    
    #decrypted = k.decrypt(encrypted)
    #print("Decrypted cipher: %s" % decrypted)
    #print("As clear: %s" % base64.b64decode(decrypted))
    
    #print(k.encrypt(mypassword).decode('UTF-8'))
    #for r in engine.routing.all():
    #    r.add_ospf_area(OSPFArea('myarea'))
        
    #for entry in engine.antispoofing.all():
    #    if entry.name == 'Interface 0':
    #        entry.add(Network('mynetwork'))
    
    
    #for entry in engine.antispoofing.all():
    #    if entry.nicid == '100':
    #        entry.add(Network('mynetwork'))
    
    '''
    {'antispoofing_node': [{'antispoofing_node': [],
                            'auto_generated': 'true',
                            'href': 'https://172.18.1.151:8082/6.2/elements/network/1122',
                            'ip': '1.1.1.0/24',
                            'key': 87,
                            'level': 'network',
                            'link': [{'href': 'https://172.18.1.151:8082/6.2/elements/single_fw/1120/antispoofing/87',
                                      'rel': 'self',
                                      'type': 'antispoofing'}],
                            'name': 'network-1.1.1.0/24',
                            'read_only': False,
                            'system': False,
                            'validity': 'enable'},
                           {'antispoofing_node': [],
                            'auto_generated': 'system',
                            'href': 'https://172.18.1.151:8082/6.2/elements/host/293',
                            'ip': '0.0.0.0',
                            'key': 88,
                            'level': 'network',
                            'link': [{'href': 'https://172.18.1.151:8082/6.2/elements/single_fw/1120/antispoofing/88',
                                      'rel': 'self',
                                      'type': 'antispoofing'}],
                            'name': 'DHCP Broadcast Originator',
                            'read_only': False,
                            'system': False,
                            'validity': 'absolute'},
                           {'antispoofing_node': [],
                            'auto_generated': 'false',
                            'href': 'https://172.18.1.151:8082/6.2/elements/network/1127',
                            'level': 'interface',
                            'validity': 'enable'}],
     'auto_generated': 'true',
     'href': 'https://172.18.1.151:8082/6.2/elements/single_fw/1120/physical_interface/274',
     'key': 86,
     'level': 'interface',
     'link': [{'href': 'https://172.18.1.151:8082/6.2/elements/single_fw/1120/antispoofing/86',
               'rel': 'self',
               'type': 'antispoofing'}],
     'name': 'Interface 100',
     'nic_id': '100',
     'read_only': False,
     'system': False,
     'validity': 'enable'}
 '''
    #callback = ContainerPolicyCallback(v)
    #waiter = ConfigurationStatusWaiter(node, 'Configured')
    #waiter.add_done_callback(callback)

    #waiter = ConfigurationStatusWaiter(node, 'Configured')
    #waiter.add_done_callback(callback)

    #while not waiter.finished():
    #    print(waiter.result(5))

    #poller = v.upload(wait_for_finish=True)
    #poller.add_done_callback()
    #while not poller.done():
    #    poller.wait(3)
    #    poller.stop()#

    #print(poller.result())
    #print(poller.last_message())
    #print(poller.done())
    '''
    node = v.nodes[0]
    pprint(vars(node.status()))

    def run_after_ready(status):
        print("Called run after ready: %s" % status)

    waiter = ConfigurationStatusWaiter(node, 'Initial', max_wait=5)
    waiter.add_done_callback(run_after_ready)
    #while not waiter.finished():
    #    print("Current result: %s" % waiter.result(5))
    '''
    
    #t = ConfigurationStatusWaiter(node, 'Declared', max_wait=4)
    #t.wait()
    #print(t.status())
    #t = NodeStatusWaiter(node, 'Not Monitored')
    #t.add_done_callback(run_after_ready)
    #t.wait()



    #for node in vss.nodes:
    #    pprint(vars(node.status()))

    #task = v.refresh(wait_for_finish=True)
    #task.add_done_callback(after_refresh)
    #while not task.done():
    #    task.wait(5)
        #task.task.abort()



    #    print(node.data['vss_node_isc']['management_ip'])
    #for sg in v.security_groups:
    #    pprint(sg.data)
    #for node in v.vss_contexts:
    #    pprint(node.data)

    #v = VSSContainer('blah-105')
    #for sg in v.security_groups:
    #    pprint(sg.data)
    #for node in v.vss_contexts:
    #    pprint(node.data)


    #BasicAuth encoded: YWdlbnQ6MTk3MGtlZWdhbg==
    #import base64


    #PolicyUploadWaiter(container=v, policy=fwpolicy)
    #context = v.add_context(isc_name='myisc', isc_policy_id=16, isc_traffic_tag='securitygroup-17')
    #print(context)


#n = VSSContainerNode(href='https://172.18.1.151:8082/6.2/elements/vss_container/847/vss_container_node/848')
    #pprint(n.data)

    #print("Before call")
    #a = VSSContext.from_href('https://172.18.1.151:8082/6.2/elements/vss_container/847/vss_context/852')
    #print(vars(a))

    #for x in v.security_groups:
    #    x.delete()
        #x.update()

    #SecurityGroup.create(name='poo', isc_id='securitygroup-13', vss_container=v)
    #print(v.security_groups)
    #pprint(v.data)

    #pprint(SMCRequest(href='https://172.18.1.151:8082/6.2/elements/vss_container/776/security_group').read().json)

    ### Save
    import requests, base64

    print(base64.b64decode(b'Om51bGw='))

    # 2017-06-22 08:36:18,383 DEBUG smc.api.session.logout: Call counters: Counter({'read': 7, 'create': 5, 'delete': 0, 'update': 0, 'cache': 0})

    #v = VSSContext('mytestfw_VMPolicy-100')
    #pprint(v.data)


    #print("GETTING NODE IP")
    #for container in c:
    #    print("Container: %s, Node IP: %s " % (container.name, getVssContextMgmtAddress(container)))


    #p = VSSContainer('myfw')
    #for node in p.container_node:
    #    print(node.data['vss_node_isc'])
    # read': 4,
    #for node in p.nodes:
    #    print(node.data['vss_node_isc'])

    #v = VSSContainer('myfw')
    #for sg in v.security_groups:
    #    print(sg, sg.isc_name)


    #v = SecurityGroup('PortSecurityGroup2 (virtualfw)')
    #print(v.referenced_by)
    #print(v.referenced_by)
    #SecurityGroup.create('PortSecurityGroup2', isc_id='securitygroup-17', vss_container=v)

    #for groups in list(SecurityGroup.objects.filter('PortSecurityGroup')):
    #    print("Group: %s, ref by: %s" % (groups, groups.referenced_by))

    #for container in list(VSSContainer.objects.all()):
    #    print(container.security_groups)





    #'PortSecurityGroup'

    #for x in list(SecurityGroup.objects.all()):
    #    if 'virtualfw' in x.name:
    #        x.delete()

    #for context in v.vss_contexts:
    #    print('context........')
    #    pprint(context.data)


    #for context in list(VSSContext.objects.all()):
    #    print(context)
    #    if context.name.startswith('virtualfw_VMPolicy'):
    #        print("Yea")

    #print('c: %s' % VSSContext.objects.filter('123virtualfw_VMPolicy').first())


    #task = v.upload()
    #for progress in task.wait(timeout=5):
    #    if not task.done():
    #        print(progress)




    #v = VSSContext('virtualfw_VMPolicy-serviceinstance-124')
    #pprint(v.data)
    #pprint(v.data)
    #pprint(v.data)

    #pprint(v.data)
    #mgmt_if = v.interface.get(0)
    #for ip in mgmt_if.sub_interfaces():
    #    print(ip.address)




    #pprint(VSSContainer('virtualfw-GlobalInstance').data)
    #c = VSSContext.create(isc_name='test',
    #                      isc_policy_id=key,
    #                      isc_traffic_tag='serviceprofile23',
    #                      vss_container=VSSContainer('grace-95'))


    #print(list(VSSContainer.objects.filter('vsmagent-165')))
    #for c in v.vss_contexts:
    #    pprint(c.data)
    #for node in v.nodes:
    #    pprint(node.data)


    #SecurityGroup.create(name='PortSecurityGroup',
    #                     isc_id='security-group-17',
    #                     vss_container=VSSContainer('virtualfw-GlobalInstance'))


    #for x in list(SecurityGroup.objects.all()):
    #    pprint(x.data)



    # a = type('InterfaceCollection', (PhysicalInterface, SubElementCollection), {}
    #        )(href=engine.resource.physical_interface, engine=engine)

    #f = FirewallPolicy('TestPolicy')
    #f.fw_ipv4_access_rules.create(name='inserted5', sources='any', add_pos=5)
    #a = sub_collection(engine.resource.virtual_resources)

    #c = create_collection(engine.virtual_resource.href, VirtualResource)
    # pprint(list(c.all()))
    #c.create(name='foo', vfw_id=33)

    #e = Element.from_href('http://172.18.1.151:8082/6.2/elements/single_fw/1038/physical_interface/421')
    # pprint(e.data)

    # for x in list(Search('admin_domain').objects.all()):
    #    print(x)
    #    pprint(x.data)

    # dns_translated = {'dns_answer_translation': [{'original_ipaddress': '1.1.1.1',
    #                                              'translated_ipaddress': '2.2.2.2'}]}
    #print(DNSRelayProfile.create('mydnsprofile', **dns_translated))

    # relay.add_fixed_domain_answer(domain_name='google.com',
    #                              translated_domain_value='yahoo.com')
    # relay.add_fixed_domain_answer(values=[{'domain_name': 'google.com'},
    #                                      {'domain_name': 'dogpile.com'},
    #                                      {'domain_name': 'espn.com', 'translated_domain_name': '1.1.1.1'}])

    # print(relay.dns_answer_translation)
    # print(relay.fixed_domain_answer)
    # print(relay.domain_specific_dns_server)
    # print(relay.hostname_mapping)

    # DNSRelayProfile.create('test')

    # print(get_options_for_link('http://172.18.1.151:8082/6.2/elements/single_fw/659/disapprove_all_changes'))

    '''
       {'active_alerts_ack_all',
     'dns_relay_profile',
     'ea_method',
     'ea_server',
     'ea_user_domain',
     'igmp_querier_settings',
     'pim_ipv4_interface_settings',
     'pim_ipv4_profile',
     'role',
     'sandbox_service',
     'snmp_agent',
     'user_response_entry'}
     '''

    # pprint(engine.data)

    # pprint(search.element_by_href_as_json('http://172.18.1.151:8082/6.2/elements/single_fw/659/pending_changes'))

    # print(alias.resolve('vm'))
    # print(location[0].data)
    #{'meta': Meta(name=None, href='http://172.18.1.150:8082/6.1/elements/fw_cluster/116/interface', type=None), '_engine': FirewallCluster(name=sg_vm)}
    # pprint(Registry._registry)

    # http://172.18.1.150:8082/6.1/elements/category_tag
    # pprint(search.element_by_href_as_json('http://172.18.1.150:8082/6.1/elements/category_tag'))

    # pprint(search.element_by_href_as_json('http://172.18.1.150:8082/6.1/elements/category_tag/3439'))
    # pprint(serialize_interface(interface_e.data))

    # print(SMCRequest(href=interface_e.href, etag=interface_e.etag,
    #                 json=serialize_interface(interface_e.data)).update())

    # engine.physical_interface.add_vlan_to_inline_interface(interface_id='4-5',
    #                                                       vlan_id='315',
    #                                                       logical_interface_ref=logical_intf_helper('inelinefw'))

    #import timeit
    # print(timeit.timeit("a = MyEngine();a.link('internal_gateway')",
    #                    setup="from __main__ import MyEngine", number=1000000))
    #insp = InspectionTemplatePolicy('No Inspection Policy')
    # print(insp.href)

    #import timeit
    # print(timeit.timeit("ElementFactory('http://172.18.1.150:8082/6.1/elements/host/978')",
    # setup="from __main__ import ElementFactory", number=1000000))

    #print(timeit.timeit("find_link_by_name('self', [])", setup="from smc.base.util import find_link_by_name"))


    print(time.time() - start_time)
    session.logout()
