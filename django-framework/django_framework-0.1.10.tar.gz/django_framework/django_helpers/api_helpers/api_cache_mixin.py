from django_framework.django_helpers.cache_helpers import APICache

class APICacheMixin(object):
    
    def __init__(self):
        
        self._need_to_cache_results = False # this is set by a method if needed
        self._need_to_clear_cache = False # or 0, For false, 1, for local user, 2 for ALL
        self._api_cache = None

    @property
    def api_cache(self, model_name = None):
        if self._api_cache == None:
            token = self.user.profile_uuid
            
            if model_name == None:
                model_name = self.model_name
                
            self._api_cache = APICache(model_name=model_name, token=token, url=self.request.get_full_path())
        return self._api_cache
    

    def _set_clear_cache_level(self, level = None):
        '''Set the level for clearing the cache.  0 or False means don't clear cache, 1 means clear for user's model, 2 means clear full user, 
        10 means clear EVERYONE! and just flush the freaken cache db.
        '''
        if level == None:
            self._need_to_clear_cache = 1
            if self.version == 'admin':
                self._need_to_clear_cache = 2 # clear it all the model level!
        else:
            self._need_to_clear_cache = level