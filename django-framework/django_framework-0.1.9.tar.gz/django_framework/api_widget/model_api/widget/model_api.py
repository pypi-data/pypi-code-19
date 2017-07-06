import json

import copy
from django_framework.django_helpers.api_helpers import BaseAPI

from django_framework.django_helpers.exception_helpers.common_exceptions import PermissionError, PermissionAdminError
from django_framework.django_helpers.model_helpers import get_model
from django_framework.django_helpers.serializer_helpers import get_serializer
from django_framework.django_helpers.manager_helpers import get_manager
from django_framework.django_helpers.meta_helpers import get_meta

from django_framework.django_helpers.api_helpers import register_api


from kafka.protocol.api import Response

class ModelAPI(BaseAPI):
    
    def __init__(self, request, model_name, model_pk = None, model_uuid = None, admin = False, **kwargs):
        
        
        self.request_requires_authentication = False # this is used so that we can initiate other variables before checking authentication
        kwargs['request_requires_authentication'] = self.request_requires_authentication # we will authenticate afterwards, sicne it is dependent on the specific Model.
        
        super(ModelAPI, self).__init__(request=request, admin=admin, **kwargs)
        
        self.model_name = self.clean_model_name(model_name)
        self.model_pk = model_pk
        self.model_uuid = model_uuid
        
        self.Model = get_model(model_name = self.model_name)
        self.Serializer = get_serializer(serializer_name = self.model_name, version = self.version)
        
        self.Manager = get_manager(manager_name = self.model_name)
        self.set_model_meta()

        self.validate_permissions()
    
    def set_model_meta(self):
        '''This is mainly used for testing as we do not expect people to swap!'''
        user_set_meta = self.request.META.get('HTTP_MODEL_META') or self.request.META.get('MODEL_META')
        if user_set_meta:
            self.Meta = get_meta(meta_name = user_set_meta)
        else:
            self.Meta = get_meta(meta_name = self.model_name)
        
    
    def validate_permissions(self):
        '''Restrict basic actions based on if logged in and user priveldges!'''
        try:
            self.is_user_authenticated()  # since we no longer check during initiation, we check explicitely
            self.request_is_authenticated = True
            return

        except PermissionAdminError as e:
            # if the error is because the user hit an admin endpoint and are not admin,
            # then we always error out.
            raise 
        
        except PermissionError as e:
            # the user is not authenticated, but maybe the endpoint does nto require it!
            if self.Meta.DEFAULT_REQUIRE_AUTHENTICATION == False:  # all meta should have this but this is easier.
                if self.request_method in self.Meta.DEFAULT_ALLOWED_ACTIONS_UNAUTHENTICATED:
                    self.request_requires_authentication = False
                    return
        raise PermissionError('This request method is not allowed when not authenticated!')
        
    def run(self):
        if self.request.method == 'GET':
            objs = self.get()

        elif self.request.method == 'POST':
            objs = self.post()
            
        elif self.request.method == 'PUT':
            objs = self.put()
            
        elif self.request.method == 'DELETE':
            objs = self.delete()
                
        self.data = objs
        return objs

    def get(self):
        self._check_request_method_is_allowed()
        objs = self.get_model_with_permissions()
        self._need_to_cache_results = True
        return objs
    
    def post(self):
        self._check_request_method_is_allowed()
        objs = self.Manager.create(Serializer = self.Serializer, data = self.query_data)
        self._set_clear_cache_level(level = None)
        return objs
    
    def put(self):
        self._check_request_method_is_allowed(model_information_required = True)
        objs = self.get_model_with_permissions(exactly_one_result = True)
        objs = self.Manager.update(Serializer = self.Serializer, data = self.query_data, model = objs[0])
        self._set_clear_cache_level(level = None)
        
        return objs

    def delete(self):
        self._check_request_method_is_allowed(model_information_required = True)
        objs = self.get_model_with_permissions(exactly_one_result = True)
        objs = self.Manager.delete(model = objs[0])
        
        self._set_clear_cache_level(level = None)
        
        return objs

    def _check_request_method_is_allowed(self, model_information_required = False):
        '''Check to make sure that everything is allowed
        1.  Check if the Meta allows the method to be run
        2.  Check to make sure , if needed, that a model is specified (mainly for PUT and DELETE)
        '''
        self.Meta.allowed_method(method = self.request.method, version = self.version)
        
        if model_information_required == True:
            if self.model_pk is None and self.model_uuid is None:
                raise ValueError('You cannot change a model without specifying a specific one!')

    def get_model_with_permissions(self, exactly_one_result = False):
        '''Requesting the appropriate model from DB.  We add in a filter to limit by the user if they are not admin'''
        query_params = copy.copy(self.query_params) # when updating query_params, do not want to mess up the original!

        if self.version == "admin": 
            # Admin's are allowed to manipulate everyone!
            pass
        elif self.request_requires_authentication == False:  
            # this means that the method and endpoint doesnt need to be validated (ie no permission restrictions)
            pass
        else:
            # update the query_parmas to include a relationship requirement to this profile!
            query_params = self.Manager._update_query(query_params=query_params, param_name = 'relationship', update_dict = {'profile' : [self.user.profile_id]})
            
        if self.model_pk:
            query_params = self.Manager._update_query(query_params=query_params, param_name = 'filter', update_dict = {'pk' : self.model_pk})
        
        if self.model_uuid:
            query_params = self.Manager._update_query(query_params=query_params, param_name = 'filter', update_dict = {'uuid' : self.model_uuid})
        

        objs = self.Manager.get_by_query(query_params = query_params, query_set = None)
        
        # do quick check if results require at least one.
        if exactly_one_result == True:
            if len(objs) != 1:
                raise ValueError('Either returned 0 or 2+ results.  Expected exactly one result!  Cannot proceed.')
        
        return objs
    
    
    def get_response(self):
        '''Override BaseAPI version of get_response to get autoformatting of data'''
        return self.format_data(data = self.data)
    
    def format_data(self, data):
        '''Serializes data and paginate data. Includes meta data as well.'''
        meta_data = { "total_query_results" : len(data),
                      "type" : self.model_name
                     }
        
        if self.request_method == 'DELETE':
            pass
        else:
            data = self.serialize_data(data = self._paginate(data))
        return dict(data=data, meta_data = meta_data)
    
    

            
register_api(ModelAPI)
