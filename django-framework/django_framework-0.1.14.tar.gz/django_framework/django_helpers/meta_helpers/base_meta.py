

class BaseMeta(object):
    
    ALLOWED_DEFAULT = None  # A list of request.methods allows for non-admin users.  ex: ['GET', 'PUT', 'POST', 'DELETE']
    ALLOWED_ADMIN   = None  # A list of request.methods for admin users, accessible via the  /admin/ endpoints ex: ['GET', 'PUT', 'POST', 'DELETE']

    DEFAULT_REQUIRE_AUTHENTICATION = True # do you need to be an authenticated user to view anything?
    DEFAULT_ALLOWED_ACTIONS_UNAUTHENTICATED = [] # if not authenticated, what methods are allowed? -- typically ['GET']
    
    ADMIN_REQUIRE_AUTHENTICATION   = True # do admin endpoints require authentication, typically True!
    

    @classmethod
    def allowed_method(cls, method, version = False):
        '''Based on the version (the type of endpoint coming in, /admin/ or not) 
        determine the allowed HTTP methods.
        '''
        
        if version == 'default' and method in cls.ALLOWED_DEFAULT:
            return True
        
        if version == 'admin' and method in cls.ALLOWED_ADMIN:
            return True
        
        raise ValueError('The requested method does not work with this model!')
        
        
        
        