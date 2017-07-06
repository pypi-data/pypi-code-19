'''
Created on Mar 9, 2017

@author: davidlepage
'''

from smc import session                        
from smc.base.model import Element
from smc.elements.resources import CollectionManager, classproperty, Search

class WierdObject(Element):
    typeof = 'host'
    
    def __init__(self, name, meta=None):
        super(WierdObject, self).__init__(name, meta)
        pass
    
    @classproperty
    def objects(self):
        print("Type: %s" % self)
        mgr =  CollectionManager(self)
        return mgr._load_collection()

if __name__ == '__main__':
    from pprint import pprint
    session.login(url='http://172.18.1.150:8082', api_key='EiGpKD4QxlLJ25dbBEp20001', timeout=30)
    
    
    from smc.elements.network import Host
    #print(Search.object_types())
    print(list(Search('vpn').objects.all()))
    
    #print(list(Host.objects.all()))
    #print('break')
    #print(list(Search('tcp_service').objects.all()))
    #from smc.elements.network import Host
    #print(list(WierdObject.objects.all()))
    #print(help(WierdObject.objects))
    #print(list(Host.objects.all()))  # @UndefinedVariable
    #Host.objects = 1
    #WierdObject.objects = 5
    #print(list(WierdObject.objects.all()))
    
    session.logout() 