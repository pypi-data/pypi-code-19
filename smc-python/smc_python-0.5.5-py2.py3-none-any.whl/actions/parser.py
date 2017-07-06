"""
Searchable is used by policy rules to simplify creation of elements used
in source / destination and service cells. Each element class that derives 
from SMCElement has a 'typeof' class attribute which is the entry point 
href for in the SMC API.

Use Searchable this way::

    searchable = Searchable(class_factory('domain_name'))
    href_list = searchable(['yahoo.com'])
    
    searchable = Searchable(class_factory('network'))
    href_list = searchable(['172.18.1.0/24', '192.168.0.0/16'])

The class_factory is used to return the right class based on the entry point (type)
specified. Searchable is a callable with the value of the entry point type. 

Valid entry point keys are:
---------------------------
address_range|application_situation|domain_name|ethernet_service|
expression|group|host|icmp_ipv6_service|icmp_service|ip_list|ip_service|ip_service_group|
network|protocol|router|service_group|tcp_service|tcp_service_group|udp_service|
udp_service_group|url_list_application|interface_zone
    
The object of this class is to first attempt to search for the elements by value, and
if possible, create the element if it doesn't exist and return the href.

This is primarily used for rules to simplify the input to source/destination and 
service cells. 

Input for services/destinations are of the format:
sources=('host', ['1.1.1.1', '2.2.2.2])    #specify element by type and searchable values
sources=['http://href_to_element', 'http://href_to_element'] #send direct hrefs as list
sources='any'    #set field to ANY
source=None      #set field to None (rule is effectively disabled)

For example, obtaining elements for a source/destination cell would be 
in the format::

    sources=[('host':['1.1.1.1', '2.2.2.2', '3.3.3.3']),
             ('network': ['172.18.1.0/24', '192.168.3.0/24']),
             ('address_range': ['1.1.1.1-1.1.1.254']),
             ('router': ['1.2.3.4', '5.6.7.8']),
             ('interface_zone': ['Internal', 'External']),
             ('domain_name': ['google.com', 'test.com'])
             .....
             .....
             ('ip_list': ['iplist1', 'iplist2']),
             ('expression': ['expression1', 'expression2']),
             ('group': ['group1': 'group2']),

.. note:: Element types ip_list, expression, and group require that the elements 
          exist and will attempt to find them by the name provided in the list. 
          These complex element types will not be created automatically if they are
          not found.

Service elements have a slightly different tuple syntax. Like source/destination, the 
first tuple field should be a valid service type. The second tuple field should be a list
of tuples with the first value being the name of the service, and second tuple field the value.
An attempt will first be made to find the service by name and if it cannot be found, or if
there are multiple results, a service will be created for that service type and the specified
service. Naming convention will be 'service_type-port'. For a tcp_service on port 5555, this 
would be named 'tcp_service-5555'.

    services=[('tcp_service': [('HTTP', '80'), ('HTTPS', '443'),('Squid','8443')]),
              ('udp_service': [('DNS', 53'), ('Netbios-137', '137'), ('Netbios-138', '138')]),
              ('application_situation': ['application1', application2']),
              ('icmp_service': []),
              ('icmp_ipv6_service': []),
              ('ip_service': []),
              ('protocol': []),
              ('ethernet_service': []),
              ('tcp_service_group': []),
              ('udp_service_group': []),
              ('ip_service_group': []),
              ('service_group': []),
              ('url_list_application': [])]

"""
import inspect
import smc.elements.network
import smc.elements.service
import smc.elements.group
from smc.actions.search import fetch_json_by_href, fetch_href_by_name

mods = [smc.elements.network, smc.elements.service, smc.elements.group]

def class_factory(typeof):
    """
    Class factory returns the class specified by the typeof class attribute
    """
    for k in mods:
        for _,klazzmod in inspect.getmembers(k, inspect.isclass):
            if hasattr(klazzmod, 'typeof') and klazzmod.typeof == typeof:
                return klazzmod
        raise AttributeError('Unsupported entry point: {}'.format(typeof))

class CachedProperty(object):
    def __init__(self, cache=None):
        self._cache = cache
        
    def __get__(self, instance, cls=None):
        return self._cache

    def __set__(self, instance, value):
        self._cache = value
        
class Searchable(object):
    cache = CachedProperty()
    
    def __init__(self, typeof):
        self.klazz = class_factory(typeof)
        self.unknown = []
    
    def prefilter(self, element):
        """
        Pre-filter network and address ranges for search. Search in SMC API
        doesn't return matches if search criteria uses '-' or '/'. The strategy 
        is to check for these element types, split these delimiters by filtering 
        out leftmost portion, and using that for the filtered search. Store the
        original value in cache (i.e. 172.18.1.0/24 will become 172.18.1.0).
        Postfilter is called if multiple elements are returned, at which time if
        the element type is network/address range and more exact match is located.
        This will prevent incorrect elements from being added, i.e. searching for
        172.18.0.0/16 and 172.18.0.0/24 would actually search '172.18.0.0' and return
        both as results. The postfilter checks the primary field value for that element
        type for an exact match when multiple results are returned.
        """
        filtered = element
        if self.klazz.typeof == 'address_range':
            filtered = element.split('-')[0]
            self.cache = element
        elif self.klazz.typeof == 'network':
            filtered = element.split('/')[0]
            self.cache = element
        return filtered
    
    def postfilter(self, element):
        """
        Called when there are multiple matches for either network or
        address range elements.
        This will look for a more exact match. For other network elements just 
        return the first one in the list as the SMC API will validate these 
        based on the network specified. For example, 172.18.0.0/24, 172.18.0.0/16, 
        etc. If the mask doesn'tmatch the network address it will fail so the 
        network matches should be valid. Just get the first entry and return for 
        those
        """
        if self.cache:
            attr = None
            if self.klazz.typeof == 'network':
                attr = 'ipv4_network'
            elif self.klazz.typeof == 'address_range':
                attr = 'ip_range'
            for possible_match in element:
                result = fetch_json_by_href(possible_match.get('href')).json
                if result.get(attr) == self.cache:
                    print("Found a more exact match: %s" % possible_match.get('href'))
                    return possible_match.get('href')
    
    def process_unknown(self):
        """
        Unknown services will be in the unknown list in format:
        [(service_name, port)]
        
        Create is expected to be done:
        
        Class.create(name, value)
        
        Some elements require only one value such as domain_name and interface_zone
        
        Class.create(value)
        The first name is expected to be name, the rest args
        """
        created = []
        if self.klazz.typeof in self.exclusions:
            return created
        for unknown in self.unknown:
            print("Attempting to create: %s, with args: %s" % (self.klazz.typeof, unknown))
            result = self.klazz.create(*unknown)
            print(result)
    
    def create_unknown(self):
        """
        Create items that are not found during search. The class will either support
        one or two parameters for creation. If ip_list, expression or group, do not
        create as these are more complex and should already exist. If they landed in
        self.unknown, they were not found by name.
        """
        created=[]
        if self.klazz.typeof in self.exclusions:
            return created
        for unknown in self.unknown:
            result=None
            if self.klazz.typeof in ['domain_name','interface_zone']:
                result = self.klazz.create(unknown)
            else: #2 args
                result = self.klazz.create('{}-{}'
                                           .format(self.klazz.__name__.lower(),
                                                   unknown), unknown)
            if result.href:
                created.append(result.href)
        return created
    
class SourceDest(Searchable):
    def __init__(self, typeof):
        Searchable.__init__(self, typeof)
        
        self.exclusions = ['group', 'iplist', 'expression']
    
    def __call__(self, elements_to_search):
        searchables=[]
        for element in elements_to_search:
            filtered = self.prefilter(element)
            result = fetch_href_by_name(filtered, 
                                        filter_context=self.klazz.typeof,
                                        exact_match=True)
            if not result.json:
                if self.cache is None: #not network or addr_range
                    self.unknown.append(element)
                else: #need original value cached
                    self.unknown.append(self.cache)
            elif len(result.json) > 1:
                if self.cache is None:
                    searchables.append(result.json[0].get('href'))
                else:
                    element = self.postfilter(result.json) #need more exact match
                    if element:
                        searchables.append(element)
                    else:
                        #Found matches but no direct match
                        self.unknown.append(self.cache)
            else:
                searchables.append(result.href)
            self.cache = None #reset
        if self.unknown:
            print("Have unknowns, creating: %s" % self.unknown)
            for created in self.create_unknown():
                searchables.append(created)
        return searchables
        
class Services(Searchable):
    def __init__(self, typeof):
        Searchable.__init__(self, typeof)

        self.exclusions = ['tcp_service_group', 'udp_service_group',
                           'ip_service_group', 'service_group']
    
    def __call__(self, elements_to_search):
        print("Called service callable: %s" % elements_to_search)
        print("Element is of type: %s" % self.klazz)
        searchables=[]
        for element in elements_to_search: #tuple
            service, port = element
            print("service: %s, port: %s" % (service, port))
            result = fetch_href_by_name(service, 
                                        filter_context='services')
            if not result.json:
                print("No result found, gotta create %s" % service)
                prepared=[]
                prepared.append(service)
                prepared.extend(port.split('-'))
                print("prepared: %s" % prepared)
                self.unknown.append(prepared)
            elif len(result.json) > 1:
                print("More than one of these found, just grab one")
                print(result.json)
                entry = [item.get('href') 
                         for item in result.json 
                         if item.get('type') == self.klazz.typeof]
                if entry:
                    print("Were all good, found it!")
                else:
                    print("Did not find a direct match.. creating new service with new name")
                    prepared=[]
                    prepared.append('{}-{}'.format(self.klazz.typeof, service))
                    prepared.append(port)
                    self.unknown.append(prepared)
            else:
                searchables.append(result.href)
        if self.unknown:
            print("Have unknowns, they are of type: %s, %s" % (self.klazz.typeof, self.unknown))
            self.process_unknown()        
    
class GroupAdder(object):
    def __init__(self, group_elements):
        pass
        