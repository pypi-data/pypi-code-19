"""
Resource Collection for SMC Elements
"""
from smc import session
import smc.base.model
from smc.api.exceptions import UnsupportedEntryPoint

class ElementCollection(object):
    """
    ElementCollection is generated dynamically from the
    connection manager and provides methods to obtain
    data from the SMC.
    """
    def __init__(self, resource):
        self._resource = resource #: cls resource
        self._params = {'filter': '*',
                        'filter_context': self._resource.typeof,
                        'exact_match': True}
    
    def __iter__(self):
        limit = self._params.pop('limit', None)
        
        count = 0
        for item in self.items():
            yield self._resource(name=item.get('name'),
                                 meta=smc.base.model.Meta(**item))
                        
            # If the limit is set and has been reached, then
            # we stop processing items here.
            count += 1
            if limit is not None and count >= limit:
                return
    
    def items(self, **kwargs):
        print("Called pages with params: %s" % self._params)
        return smc.base.model.prepared_request(
                                        params=self._params,
                                              ).read().json

    def all(self):
        """
        Retrieve all elements based on element type
        """
        self._params.update(filter='*')
        return self
       
    def filter(self, match_on, exact_match=False):
        """
        Filter results for specific element type.
        
        :param str,list match_on: any parameter to attempt to match on. For example, if
            this is a service, you could match on service name 'http' or ports
            of interest, '80'.
        :param boolean exact_match: Whether match needs to be exact or not
        """
        self._params.update(filter=match_on,
                            exact_match=exact_match)
        return self
       
    def limit(self, count):
        """
        Limit provides the ability to limit the number of results returned from
        the collection.
        
        :param int count: number of records to page
        """
        self._params.update(limit=count)
        return self
    
                                
class CollectionManager(object):
    """
    CollectionManager takes a class type as input and dynamically
    creates an ElementCollection for that class.
    """
    def __init__(self, resource):
        print('resource: %s' % resource)
        self._cls = resource #Class type
        
    def _load_collection(self, **kwargs):
        """
        Factory method to construct the class with the proper
        attributes. Return a collection object based on the calling
        class type.
        """
        attrs={'__doc__': self._docstring()}
        cls_name = '{0}Collection'.format(self._cls.__name__)
        collection_cls = type(str(cls_name), (ElementCollection,), attrs)
        return collection_cls(self._cls)

    def _docstring(self):
        return """
               A resource collection provides a set of methods for
               filtering search results for a specific object type.
               """      

class Search(object):
    """
    Search is an interface to the collection manager and provides a way to
    search for any object by type, as long as there is a valid entry point.
    The returned elements will be the defined class element if it exists, 
    otherwise a dynamic class is returned of type :py:class:`smc.base.model.Element`
    
    :param str resource: name of resource, should be entry point name as found
        from called :func:`~Search.object_types()`
    """
    def __init__(self, resource):
        self._resource = resource.lower() #Entry point
        # Make sure entry point exists
        self._validate(self._resource)

    @property
    def objects(self):
        """
        A collection resource for the element selected
        
        :return: :class:`~ElementCollection`
        """
        if smc.base.model.lookup_class(self._resource) is smc.base.model.Element:
            # Create a class of type Element for the Collection Manager
            attrs={'typeof': self._resource}
            cls_name = '{0}Element'.format(self._resource.title())
            element_cls = type(str(cls_name), (smc.base.model.Element,), attrs)
        else: # Existing class of this type already exists
            element_cls = smc.base.model.lookup_class(self._resource)
        # Return the collection from manager
        mgr =  CollectionManager(element_cls)
        return mgr._load_collection()
    
    def _validate(self, name):
        """
        Return dict of all entry points, dict will be 
        {'href', 'rel', 'method'}. This is used to filter
        out elements not bound to the elements URI
        """
        if name.lower() not in Search.object_types():
            raise UnsupportedEntryPoint('An entry point was specified that does '
                                        'not exist. Entry point: %s', name)
            
    @staticmethod
    def object_types():
        """
        Return a list of all entry points within the SMC. These can be used to 
        search for any elements using it's type::
        
            >>> list(Search('vpn').objects.all())
            [VPNPolicy(name=Amazon AWS), VPNPolicy(name=sg_vm_vpn)]

        And subsequently filtering as well::

            >>> list(Search('vpn').objects.filter('AWS'))
            [VPNPolicy(name=Amazon AWS)]
        
        :return: list of entry points
        """
        # Return all elements from the root of the API nested under elements URI
        element_uri = str('{}/{}/elements'.format(session.url, session.api_version))
        return [element.get('rel')
                for element in session.cache.get_all_entry_points()
                if element.get('href').startswith(element_uri)]
