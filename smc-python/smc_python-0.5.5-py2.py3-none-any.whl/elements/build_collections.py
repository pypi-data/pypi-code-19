# -*- coding: utf-8 -*- 
"""
Build script to create the smc.elements.collection module. Each of the nodes in the
SMC API that are mounted at <smc>/<version>/elements/xxxx are enumerated by this module
and describe_** functions are created. They are meant as collections to view details from
any of the mount points. Use 'gen_diff_for_new_version' to check whether new entry points
are in the new API and it will check the collection module to determine if the describe_*
method exists or it will create them in collection_new.py. 
Also, you can reverse validate that an entry point hasnt been removed by running the
validate function as well.
"""
from smc import session
from smc.administration.system import System
import smc.elements.collection
import logging

logger = logging.getLogger(__name__)

collection_module = 'collection2.py'
collection_module_new = 'collection_new.py'
element_to_class_map = {}
engine_map = {'engine.Engine': ['single_fw','fw_cluster','single_layer2', 
                                'layer2_cluster', 'single_ips', 'ips_cluster', 
                                'master_engine','virtual_fw','virtual_ips',
                                'virtual_fwlayer2']}

def gen_diff_for_new_version(api_version):
    """
    This will get the new entry points from one version to the next,
    create the function and put an if clause in based on the version. It
    will be written to current directory as collection_new.py
    """
    print("Checking against SMC API version {} for new entry points".format(api_version))
    system = System()
    print("SMC Version: %s" % system.smc_version)
    lookup_class_typeof_attr() #set element_to_class_map
    import inspect
    all_functions = inspect.getmembers(smc.elements.collection, inspect.isfunction)
    func_names = [func[0] for func in all_functions]
    
    with open(collection_module_new, 'w') as outfile:
        for entry_point in session.cache.entry_points:
            describe_func = 'describe_%s' % entry_point
            if describe_func in func_names:
                print("Entry point function already exists, skipping: %s" % entry_point)
            else:
                fqdn = session.cache.get_entry_href(entry_point)
                print("New entry point found %s, @ %s" % (entry_point,fqdn))
                name = "describe_%s" % entry_point
                doc_string = 'smc.base.model.Element'
                if element_to_class_map.get(entry_point):
                    print("Have class: %s for entry_point: %s" % \
                            (element_to_class_map.get(entry_point), entry_point))
                    #Formatting for doc_string and return class in generlic_list
                    n = element_to_class_map.get(entry_point).__module__.split('.')
                    doc_string='.'.join(n) + '.{}'.format(element_to_class_map.get(entry_point).__name__)
                    classtype = '{}.{}'.format(n[-1], element_to_class_map.get(entry_point).__name__)
                    code='''
def {}(name=None, exact_match=True):
    """ 
    Describe {} entries on the SMC
    
    ..note :: Requires SMC API version >= {} 
    
    :return: :py:class:`{}` 
    """
    if session.api_version >= {}:
        return generic_list_builder('{}', name, exact_match, {})
    else:
        return []
'''.format(name, entry_point, api_version, doc_string, api_version, entry_point, 
           classtype)
                    outfile.write(code)
                else: #SMCElement
                    code='''
def {}(name=None, exact_match=True):
    """ 
    Describe {} entries on the SMC
    
    ..note :: Requires SMC API version {}
    
    :return: :py:class:`{}`
    """
    if session.api_version >= {}:
        return generic_list_builder('{}', name, exact_match)
    else:
        return []
'''.format(name, entry_point, api_version, doc_string, api_version, entry_point)
                    outfile.write(code)

def gen_function(name, classtype=None, doc_string='smc.base.model.Element'):
    """
    Create all of the functions for the collection module. If classtype is 
    not none, this will format a generic_list_builder specifying the return
    class should be of classtype. This is called in write_py 
    """
    if classtype is None:
        code = '''
def {}(name=None, exact_match=True):
    """ 
    Describe {} entries on the SMC
    
    :return: :py:class:`{}` 
    """
    return generic_list_builder('{}', name, exact_match)
'''.format('describe_{}'.format(name), name, doc_string, name)

    else:
        code = '''
def {}(name=None, exact_match=True):
    """ 
    Describe {} entries on the SMC
    
    :return: :py:class:`{}` 
    """
    return generic_list_builder('{}', name, exact_match, {})
'''.format('describe_{}'.format(name), name, doc_string, name, classtype)
    return code

def write_py():
    """
    This writes out the entire collection module from scratch. You should use the diff
    function (gen_diff_for_new_version) when going from one version to the next. That function
    will discover new entry points and create the function definitions along with
    checks based on version in the return code. 
    
    To make imports work, the needed classes are added like so:
    import smc.base.model as element
    
    If a class with the typeof class attribute is found, the generic_class_list will be
    formatted for specific classes with 'element.ElementName' so the imports work. Each import
    should be imported "as" using the last octet of the full qualified package name.
    """
    lookup_class_typeof_attr()
    
    with open(collection_module, 'w') as outfile:
        imp = \
'''"""
Collection module allows for search queries against the SMC API to retrieve
element data.

Each describe function allows two possible (optional) parameters:

* name: search parameter (can be any value)
* exact_match: True|False, whether to match exactly on name field

Each function returns a list of objects based on the specified element type. Most
elements will return a list of type :py:class:`smc.elements._element.SMCElement`. 
SMCElement is a generic container class with helper methods for elements, such as 
:py:func:`smc.elements._element.SMCElement.describe` to view the elements raw contents.

.. seealso:: :py:class:`smc.elements._element.SMCElement`

All return element types (regardless of type) will have the following attributes as
metadata::

    href: href location of the element in SMC
    type: type of element
    name: name of element

Some additional generic search examples follow...

    import smc.elements._collection
    
To search for all host objects::

    for host in describe_host():
        print host.name, host.href
        
To search only for a host with name 'test'::

    for host in describe_host(name=['test']):
        print host

To search for all hosts with 'test' in the name::

    for host in describe_hosts(name=['test'], exact_match=False):
        print host
        
It may be useful to do a wildcard search for an element type and view the entire
object info::

    for host in describe_networks(name=['1.1.1.0'], exact_match=False):
        print host.name, host.describe() #returned SMCElement

Modify a specific SMCElement type by changing the name::

    for host in describe_hosts(name=['myhost']):
        if host:
            host.modify_attribute(name='mynewname')   
            
It is also possible to use wildcards when searching for a specific host, without
setting the exact_match=False flag. For example::

    for x in describe_hosts(name=['TOR*']):
        print x.describe()
        
    for y in describe_hosts(name=['TOR'], exact_match=False):
        print y
        
Both will work, however the first option will only find items starting with TOR*, whereas
the second option could find items such as 'DHCP Broadcast OriginaTOR', etc.

This module is generated dynamically based on SMC API entry points mounted at
the http://<smc>/api/elements node.

    :param list name: list of names to retrieve
    :param boolean exact_match: True|False, whether to match specifically on name field
           or do a wildcard search (default: True)
"""
from smc import session
import smc.elements.servers as servers
import smc.vpn.policy as vpn_policy
import smc.vpn.elements as vpn_elements
import smc.elements.policy as policy
import smc.elements._element as element
import smc.elements.user as user
import smc.core.engine as engine
from smc.api.common import fetch_json_by_href, fetch_href_by_name
'''
        outfile.write(imp)
        for x in session.cache.entry_points:
            handled=False
            #Check map to see if we need to return a specific object type
            for k, v in engine_map.iteritems():
                if x in v:
                    print("Function: %s should return obj type: %s" % (x, k))
                    #Function should return a specific object type and not SMCElement
                    outfile.write(gen_function(x, k, doc_string='smc.core.engine.Engine'))
                    handled=True
                    break
            if not handled:
                #Check the smc.elements._element map to see if we can return a specific
                #element type, mostly for aescetic reasons but this is also relevant if an
                #object type has methods specific to that type.
                if element_to_class_map.get(x):
                    print("Found element type in MAP: %s, %s" % (x, element_to_class_map.get(x)))
                    #Get last part of full package name, i.e. smc.elements._element.SMCElement would
                    #be element.SMCElement
                    n = element_to_class_map.get(x).__module__.split('.')
                    #When writing our the docstring, rejoin the module information and append the 
                    #class name
                    outfile.write(gen_function(x, '{}.{}'.format(n[-1], element_to_class_map.get(x).__name__),
                                               doc_string='.'.join(n) + '.{}'
                                               .format(element_to_class_map.get(x).__name__)))
                else:
                    outfile.write(gen_function(x))
        func='''
def generic_list_builder(typeof, name=None, exact_match=True, klazz=element.SMCElement):
    """
    Build the query to SMC based on parameters
    
    Each constructor that has a describe function must have two arguments, 
    name=None, meta=None. This is because some top level classes require name.
    If the resource does not have a top level api entry point, it will be
    referenced by the linked resource using meta only.
    
    Before the META data is returned, the dict values are encoded to utf-8 to
    support unicode chars.
    
    :param list name: Name of host object (optional)
    :param exact_match: Do exact match against name field (default True)
    :return: list :py:class:`smc.elements._element.SMCElement`
    """
    global element
    result=[]
    if not name:
        lst = fetch_json_by_href(
                    session.cache.get_entry_href(typeof)).json
        if lst:
            for item in lst:
                result.append(klazz(name=item.get('name'), 
                                    meta=element.Meta(**item)))
    else: #Filter provided
        for elements in name:
            for item in fetch_href_by_name(elements, 
                                           filter_context=typeof, 
                                           exact_match=exact_match).json:
                result.append(klazz(name=item.get('name'),
                                    meta=element.Meta(**item)))
    return result
'''
        outfile.write(func)


def lookup_class_typeof_attr():
    """
    Maps classes from smcpackages that have a typeof attribute to an entry 
    point in SMC API; typeof = entry_point
    """
    import inspect
    import smc.elements.network
    import smc.elements.service
    import smc.elements.other
    import smc.vpn.policy
    import smc.vpn.elements
    import smc.elements.user
    import smc.elements.servers
    import smc.policy.policy
    mods = [smc.elements.network, smc.elements.service, smc.elements.other, 
            smc.vpn.policy, smc.vpn.elements, smc.elements.user, 
            smc.elements.servers, smc.policy.policy]
    for mod in mods:
        all_classes = inspect.getmembers(mod, inspect.isclass)
        for clazz in all_classes:
            if hasattr(clazz[1], 'typeof'):
                element_to_class_map[clazz[1].typeof] = clazz[1]
                print("Class: %s has attr: %s" % (clazz[1], clazz[1].typeof))
                
def validate_functions_have_entry_points():
    """ 
    Validate whether the functions in collection have valid entry points still.
    Just in case an entry point goes away. Call gen_diff_for_new_version to find
    whether each entry point has a describe_* function
    """
    import inspect
    all_functions = inspect.getmembers(smc.elements.collection, inspect.isfunction)
    func_names = [func[0] for func in all_functions]
    for func in func_names:
        f = func.split('describe_')
        if len(f) > 1:
            if f[1] not in session.cache.entry_points:
                if f[1] not in ['engines', 'ips_engines', 'layer2_engines', 'layer3_engines']: #Ignore
                    print("Missing entry point for function: %s" % f[1])
        
if __name__ == '__main__':

    import time
    start_time = time.time()
    logging.getLogger()
    #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s.%(funcName)s: %(message)s')
    logging.basicConfig(filename='/Users/davidlepage/example.log', filemode='w', level=logging.DEBUG)
    
    #session.login(url='http://172.18.1.150:8082', api_key='EiGpKD4QxlLJ25dbBEp20001', timeout=120)
    session.login(url='http://172.18.1.26:8082', api_key='kKphtsbQKjjfHR7amodA0001', timeout=45)
    
    #write_py()
    #gen_diff_for_new_version(session.api_version)
    lookup_class_typeof_attr()
    #validate_functions_have_entry_points()
    
    session.logout()