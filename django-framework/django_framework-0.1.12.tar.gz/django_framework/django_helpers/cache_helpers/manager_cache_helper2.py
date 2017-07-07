
from base_cache import BaseCache

import json




class ManagerCache(object):
    '''This APICache is used only to cache queries generated from the model_api section.
    It can be used for any other location, but it is designed to function well only with the model_api!!
    '''

    def __init__(self, model_name, key):
        
        self.model_name = model_name
        
        self.key = key
        self.key = self.generate_key_name()
        
    def get(self):
        print('oof')
        response = self.redis_connection.get(self.key) # simple key value lookup
        # it could also be None:
        if response is not None:
            response = json.loads(response)

        return response
    
    def set(self, value, ttl = None):
        # we first check that the model_name has this use
        # set the expire time in ttl in seconds

        value = json.dumps(value)
        
        if ttl is None:
            #If not specified, then ttl is forever
            response = self.redis_connection.set(self.key, value)
            
        else:
            # ttl in seconds
            response = self.redis_connection.setex(name = self.key, value = value, time = ttl)

        return response
    
    def clear(self):

        response = self.redis_connection.delete(self.key)
        return response

    
    def generate_key_name(self):
        return 'manager:' + self.model_name + ':' +self.key
