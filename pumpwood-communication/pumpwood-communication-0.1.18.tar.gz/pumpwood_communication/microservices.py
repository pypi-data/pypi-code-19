# -*- coding: utf-8 -*-
import requests
import grequests
import simplejson as json
import math

from .exceptions import exceptions_dict\
                      , ObjectDoesNotExist\
                      , PumpWoodUnauthorized\
                      , ModelWronglyDefined\
                      , WrongModelEstimationWorkflow\
                      , WrongDataLoading\
                      , PumpWoodException\
                      , PumpWoodForbidden

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

class PumpWoodMicroService():
  '''
    :param microservice_name: Name of the microservice, helps when exceptions are raised
    :type microservice_name: str
    :param server_url: url of the server that will be connected
    :type server_url: str
    :param user_name: Username that will be logged on.
    :type user_name: str
    :param password: Variable to be converted to JSON and posted along with the request
    :type password: str
    :param local: Boolean if the service is to be considered local so have no conections with other PumpWoods
    :type local: bool

    Class to define an inter-pumpwood MicroService
  '''
  def __init__(self, microservice_name='', server_url=None, user_name=None, password=None, verify_ssl=True):
      self._headers = {}

      self.user_name = user_name
      self.password = password
      self.server_url = server_url
      self.request_session = None
      self.microservice_name = microservice_name
      self.verify_ssl = verify_ssl

  def raise_if_local(self):
    if self.local:
      raise PumpWoodException('MicroService {name} is working as local, so no connection can be stabilised.'.format(name=self.microservice_name))

  def error_handler(cls, response):
    if ( math.floor(response.status_code / 100) ) != 2:
      response_dict = PumpWoodMicroService.angular_json(response)
      exception_type = exceptions_dict.get('type')
      if exception_type is not None:
        raise exceptions_dict[response_dict['type']]( response_dict['msg'] )
      else:
        raise response_dict

  @staticmethod
  def angular_json(request_result):
    string_start = ")]}',\n"
    try:
      if request_result.text[:6] == string_start:
        return ( json.loads(request_result.text[6:]) )
      else:
        return ( json.loads(request_result.text) )
    except:
      return {"error": "Can not decode to Json", 'msg': request_result.text}
  #
  def login(self, force=False):
    if self.request_session is None or force:
      self.request_session = requests.Session()

      self._headers = {'Content-Type': 'application/json'}
      self.request_session.headers.update(self._headers)
      login_url = self.server_url + '/rest/registration/login/'

      login_result = self.request_session.post(login_url, data=json.dumps({'username': self.user_name, 'password': self.password}), verify=self.verify_ssl)
      login_data   = PumpWoodMicroService.angular_json(login_result)

      self._headers.update({'X-CSRFToken': login_data['csrf_token'], 'Authorization': 'Token ' + login_data['token']})
      self.request_session.headers.update(self._headers)
  #
  def post(self, url, data):
    if self.request_session is None:
      raise PumpWoodUnauthorized('MicroService {name} not looged'.format(name=self.microservice_name))
    
    post_url  = self.server_url + url
    post_data = json.dumps(data)

    response = self.request_session.post(url=post_url, data=post_data, verify=self.verify_ssl)
    self.error_handler(response)

    return PumpWoodMicroService.angular_json(response)

  def get(self, url):
    if self.request_session is None:
      raise PumpWoodUnauthorized('MicroService {name} not looged'.format(name=self.microservice_name))
    
    post_url = self.server_url + url
    response = self.request_session.get(post_url, verify=self.verify_ssl)
    self.error_handler(response)

    return PumpWoodMicroService.angular_json(response)

  def delete(self, url):
    if self.request_session is None:
      raise PumpWoodUnauthorized('MicroService {name} not looged'.format(name=self.microservice_name))
    
    post_url = self.server_url + url
    response = self.request_session.delete(post_url, verify=self.verify_ssl)
    self.error_handler(response)

    return PumpWoodMicroService.angular_json(response)

  def default_pumpwood_services(self, model_class, end_point, type, args=None, post_data=None):
      '''
        :param model_class: Name of the class that will be requested
        :type model_class: str,
        :param type: Type of the request ("GET"/"POST")
        :type type: str,
        :param args: Args to be used in url creation
        :type args: str,int
        :param post_data: Variable to be converted to JSON and posted along with the request
        :type post_data: any

        Make a request to the deafult REST service at pumpwood.
      '''
      url_str = "/rest/" + model_class.lower() + "/" + end_point + "/"
      if end_point in ['retrieve']:
        url_str = url_str + str(args['pk']) + "/"

      if end_point in ['actions']:
        if type == 'post':
          if args['pk'] is not None:
            url_str = url_str + args['action'] + '/' + str(args['pk']) + "/"
          else:
            url_str = url_str + args['action'] + '/'

      if type == 'post':
        return self.post(url=url_str
                       , data=post_data)
      elif type == 'get':
        return self.get(url=url_str)
      else:
        raise Exception('Wrong type:', type)

  def list(self, model_class, filter_dict={}, exclude_dict={}, ordering_list=[]):
    '''Function to post at list end-point (resumed data) of PumpWood like systems, results will be 
    paginated. To get next pag, send recived pk at exclude dict (ex.: exclude_dict={id__in: [1,2,...,30]}).
       
        Args:
          model_class (str): Model class of the end-point
        
        Kwargs:
          filter_dict (dict): Filter dict to be used at the query (objects.filter arguments)
          exclude_dict (dict):  Exclude dict to be used at the query (objects.exclude arguments)
          ordering_list (list): Ordering list to be used at the query (objects.order_by arguments)

        Returns:
          list: Contaiing objects serialized by list Serializer.

        Raises:
          No especific raises.

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/list/" % ( model_class.lower(), )
    post_data = {'filter_dict': filter_dict, 'exclude_dict': exclude_dict, 'ordering_list': ordering_list}
    return self.post(url=url_str, data=post_data)

  def list_without_pag(self, model_class, filter_dict={}, exclude_dict={}, ordering_list=[]):
    '''Function to post at list end-point (resumed data) of PumpWood like systems, results won't be paginated.
    **Be carefull with large returns.**
       
        Args:
          model_class (str): Model class of the end-point
        
        Kwargs:
          filter_dict (dict): Filter dict to be used at the query (objects.filter arguments)
          exclude_dict (dict):  Exclude dict to be used at the query (objects.exclude arguments)
          ordering_list (list): Ordering list to be used at the query (objects.order_by arguments)

        Returns:
          list: Contaiing objects serialized by list Serializer.

        Raises:
          No especific raises.

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/list-without-pag/" % ( model_class.lower(), )
    post_data = {'filter_dict': filter_dict, 'exclude_dict': exclude_dict, 'ordering_list': ordering_list}
    return self.post(url=url_str, data=post_data)

  def retrieve(self, model_class, pk):
    '''Function to get object serialized by retrieve end-point (more detailed data)
       
        Args:
          model_class (str): Model class of the end-point
          pk (int): Object pk

        Returns:
          list: Contaiing objects serialized by retrieve Serializer.

        Raises:
          No especific raises.

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/retrieve/%d" % ( model_class.lower(), pk)
    return self.get( url=url_str )

  def save(self, obj_dict):
    '''Function to save or update a new model_class object. If obj_dict{'pk'} is None or
    not defined a new object will be created. The obj model class is defided at obj_dict['model_class']
    and if not defined an PumpWoodException will be raised.
       
        Args:
          obj_dict (dict): Model data dictionary. It must have 'model_class' key and if 'pk' key
          is not defined a new object will be created, else object with pk will be updated.

        Returns:
          dict: Updated/Created object data.

        Raises:
          PumpWoodException('To save an object obj_dict must have model_class defined.'): Will be raised if
          model_class key is not present on obj_dict dictionary

        Example:
          No example yet.
    '''
    model_class = obj_dict.get('model_class')
    if model_class is None:
      raise PumpWoodException('To save an object obj_dict must have model_class defined.')
    
    url_str = "/rest/%s/save/" % ( model_class.lower())
    return self.post( url=url_str, data=obj_dict )

  def delete(self, model_class, pk):
    '''Delete (or whatever the PumpWood system have been implemented) the object with the specified pk.
       
        Args:
          model_class (str): Model class to delete the object
          pk (int): Object pk to be deleted (or whatever the PumpWood system have been implemented)

        Returns:
          Dependends on backend implementation

        Raises:
          Dependends on backend implementation

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/delete/%d" % ( model_class.lower(), pk )
    return self.delete( url=url_str )
    

  def list_actions(self, model_class):
    '''Return a list of all actions avaiable at this model class.
       
        Args:
          model_class (str): Model class to list possible actions.

        Returns:
          list: List of possible actions and its descriptions

        Raises:
          Dependends on backend implementation

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/actions/" % ( model_class.lower())
    return self.get( url=url_str )

  def execute_action(self, model_class, action, pk=None, parameters={}):
    '''Execute action exposed. If action is static or classfunction no pk is necessary.
       
        Args:
          model_class (str): Model class to delete the object
          action (str): Action that will be performed.

        Returns:
          pk (int): Pk of the object that action will be performed over.
          parameters (dict): Parameter dictionary to use in the action.

        Raises:
          dict: Return a dict with four keys:
            - result: Result of the action.
            - action: Action description.
            - parameters: Parameters used to perform action.
            - obj: Object over which were performed the action.

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/actions/%s/" % ( model_class.lower(), action)
    if pk is not None:
      url_str = url_str + str(pk) + '/'
    return self.post( url=url_str, data=parameters )

  def search_options(self, model_class):
    '''Returns options to search, like forenging keys and choice fields.
       
        Args:
          model_class (str): Model class to check search parameters

        Returns:
          dict: Dictionary with search parameters

        Raises:
          Dependends on backend implementation

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/options/" % ( model_class.lower() )
    return self.get( url=url_str )

  def fill_options(self, model_class, parcial_obj_dict):
    '''Returns options for object fields. This function send partial fillment and return options to finish object fillment.
       
        Args:
          model_class (str): Model class to check filment options.
          parcial_obj_dict (dict): Partial object data

        Returns:
          dict: Dictionary with possible data.

        Raises:
          Dependends on backend implementation

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/options/" % ( model_class.lower() )
    return self.post( url=url_str, data=parcial_obj_dict )

  def pivot(self, model_class, columns=[], format='list', filter_dict={}, exclude_dict={}, ordering_list=[]):
    '''Pivots object data acording to columns specified.
       
        Args:
          model_class (str): Model class to be pivoted.
          columns (str): Fields to be used as columns.
          format (str): Format to be used to convert pandas.DataFrame to dictionary.
          filter_dict (dict): Dictionary to to be used in objects.filter argument (Same as list end-point).
          exclude_dict (dict): Dictionary to to be used in objects.exclude argument (Same as list end-point).
          ordering_list (list): Dictionary to to be used in objects.order_by argument (Same as list end-point).

        Returns:
          dict or list: Depends on format type used to convert pandas.DataFrame

        Raises:
          Dependends on backend implementation

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/pivot/" % ( model_class.lower(), )
    post_data = {'columns':columns, 'format':format, 'filter_dict': filter_dict, 'exclude_dict': exclude_dict, 'ordering_list': ordering_list}
    return self.post( url=url_str, data=parcial_obj_dict )

    
  #########################################
  #########################################
  #########Bach assyncronous calls#########
  #########################################
  #########################################
  #########################################
  def parallel_post(self, url_list, data, max_parallel_calls, return_details):
    '''
      Create assync calls to parallel_post
    '''
    urls = []
    body = []
    results = []
    for batch_index in batch(range(len(data)), max_parallel_calls*4):
      requests_list = []
      i = batch_index[0]
      for i in batch_index:
        urls.append( url_list[i] )
        url_temp = post_url  = self.server_url + url_list[i]
        body.append( data[i] )
        post_data = json.dumps( data[i] )
        requests_list.append( grequests.post(url=url_temp, data=post_data, verify=self.verify_ssl, session=self.request_session) )

      responses = grequests.map(requests_list, size=max_parallel_calls)
      for r in responses:
        results.append( PumpWoodMicroService.angular_json( r ) )
    
    if return_details:
      to_return = []
      for i in range(len(urls)):
        to_return.append({'url': urls[i], 'body': body[i], 'results': results[i]})
      return to_return

    else:
      return results

  def parallel_get(self, url_list, max_parallel_calls, return_details):
    '''
      Create assync calls to parallel_get
    '''
    urls = []
    results = []
    for batch_index in batch(range(len(url_list)), max_parallel_calls*4):
      requests_list = []
      i = batch_index[0]
      for i in batch_index:
        urls.append( url_list[i] )
        url_temp = post_url  = self.server_url + url_list[i]
        requests_list.append( grequests.get(url=url_temp, verify=self.verify_ssl, session=self.request_session) )

      responses = grequests.map(requests_list, size=max_parallel_calls)
      for r in responses:
        results.append( PumpWoodMicroService.angular_json( r ) )
    
    if return_details:
      to_return = []
      for i in range(len(urls)):
        to_return.append({'url': urls[i], 'results': results[i]})
      return to_return
    else:
      return results

  def parallel_delete(self, url_list, max_parallel_calls, return_details):
    '''
      Create assync calls to parallel_delete
    '''
    urls = []
    results = []
    for batch_index in batch(range(len(url_list)), max_parallel_calls*4):
      requests_list = []
      i = batch_index[0]
      for i in batch_index:
        urls.append( url_list[i] )
        url_temp = post_url  = self.server_url + url_list[i]
        requests_list.append( grequests.delete(url=url_temp, verify=self.verify_ssl, session=self.request_session) )

      responses = grequests.map(requests_list, size=max_parallel_calls)
      for r in responses:
        results.append( PumpWoodMicroService.angular_json( r ) )
    
    if return_details:
      to_return = []
      for i in range(len(urls)):
        to_return.append({'url': urls[i], 'results': results[i]})
    else:
      return results

  def parallel_list(self, model_class, query_list=[], max_parallel_calls=20, return_details=False):
    '''Function to post at list end-point (resumed data) of PumpWood like systems, results will be 
    paginated. To get next pag, send recived pk at exclude dict (ex.: exclude_dict={id__in: [1,2,...,30]}).
       
        Args:
          model_class (str): Model class of the end-point
        
        Kwargs:
          filter_dict (dict): Filter dict to be used at the query (objects.filter arguments)
          exclude_dict (dict):  Exclude dict to be used at the query (objects.exclude arguments)
          ordering_list (list): Ordering list to be used at the query (objects.order_by arguments)

        Returns:
          list: Contaiing objects serialized by list Serializer.

        Raises:
          No especific raises.

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/list/" % ( model_class.lower(), )
    data = []
    for q in query_list:
      if type(q) != dict:
        raise PumpWoodException('All members of query_list must be dict')
      else:
        dict_to_add = {'filter_dict': q.get('filter_dict', {})
                     , 'exclude_dict': q.get('exclude_dict', {})
                     , 'ordering_list': q.get('ordering_list', [])}
        data.append( dict_to_add )
    return self.parallel_post(url_list=url_str, data=data, max_parallel_calls=max_parallel_calls, return_details=return_details)

  def parallel_list_without_pag(self, model_class, query_list=[], max_parallel_calls=20, return_details=False):
    '''Function to post at list end-point (resumed data) of PumpWood like systems, results won't be paginated.
    **Be carefull with large returns.**
       
        Args:
          model_class (str): Model class of the end-point
        
        Kwargs:
          filter_dict (dict): Filter dict to be used at the query (objects.filter arguments)
          exclude_dict (dict):  Exclude dict to be used at the query (objects.exclude arguments)
          ordering_list (list): Ordering list to be used at the query (objects.order_by arguments)

        Returns:
          list: Contaiing objects serialized by list Serializer.

        Raises:
          No especific raises.

        Example:
          No example yet.
    '''
    url_str = "/rest/%s/list-without-pag/" % ( model_class.lower(), )
    data = []
    for q in query_list:
      if type(q) != dict:
        raise PumpWoodException('All members of query_list must be dict')
      else:
        dict_to_add = {'filter_dict': q.get('filter_dict', {})
                     , 'exclude_dict': q.get('exclude_dict', {})
                     , 'ordering_list': q.get('ordering_list', [])}
        data.append( dict_to_add )
    return self.parallel_post(url_list=url_str, data=data, max_parallel_calls=max_parallel_calls, return_details=return_details)

  def parallel_retrieve(self, model_class, pk_list=[], max_parallel_calls=20, return_details=False):
    '''Function to get object serialized by retrieve end-point (more detailed data)
       
        Args:
          model_class (str): Model class of the end-point
          pk (int): Object pk

        Returns:
          list: Contaiing objects serialized by retrieve Serializer.

        Raises:
          No especific raises.

        Example:
          No example yet.
    '''
    url_str_list = []
    for pk in pk_list:
      url_str_list.append( "/rest/%s/retrieve/%d" % ( model_class.lower(), pk) )
    return self.parallel_get( url_list=url_str_list, max_parallel_calls=max_parallel_calls, return_details=return_details )

  def parallel_save(self, obj_dict_list=[], max_parallel_calls=20, return_details=False):
    '''Function to save or update a new model_class object. If obj_dict{'pk'} is None or
    not defined a new object will be created. The obj model class is defided at obj_dict['model_class']
    and if not defined an PumpWoodException will be raised.
       
        Args:
          obj_dict (dict): Model data dictionary. It must have 'model_class' key and if 'pk' key
          is not defined a new object will be created, else object with pk will be updated.

        Returns:
          dict: Updated/Created object data.

        Raises:
          PumpWoodException('To save an object obj_dict must have model_class defined.'): Will be raised if
          model_class key is not present on obj_dict dictionary

        Example:
          No example yet.
    '''
    urls_list = []
    for obj_dict in obj_dict_list:
      urls_list.append( "/rest/%s/save/" % ( obj_dict['model_class'].lower() ) )
    return self.parallel_post( url_list=urls_list, data=obj_dict_list, max_parallel_calls=max_parallel_calls, return_details=return_details )

  def parallel_delete(self, model_class, pk_list=[], max_parallel_calls=20, return_details=False):
    '''Delete (or whatever the PumpWood system have been implemented) the object with the specified pk.
       
        Args:
          model_class (str): Model class to delete the object
          pk (int): Object pk to be deleted (or whatever the PumpWood system have been implemented)

        Returns:
          Dependends on backend implementation

        Raises:
          Dependends on backend implementation

        Example:
          No example yet.
    '''
    url_list = []
    for pk in pk_list:
      url_list.append( "/rest/%s/delete/%d" % ( model_class.lower(), pk ) )
    return self.delete( url_list=url_list, max_parallel_calls=max_parallel_calls, return_details=return_details )


  def parallel_execute_action(self, model_class, action_list, pk_list, parameters_list, max_parallel_calls=20, return_details=False):
    '''Execute action exposed. If action is static or classfunction no pk is necessary.
       
        Args:
          model_class (str): Model class to delete the object
          action (str): Action that will be performed.

        Returns:
          pk (int): Pk of the object that action will be performed over.
          parameters (dict): Parameter dictionary to use in the action.

        Raises:
          dict: Return a dict with four keys:
            - result: Result of the action.
            - action: Action description.
            - parameters: Parameters used to perform action.
            - obj: Object over which were performed the action.

        Example:
          No example yet.
    '''
    if not(len(action_list) == len(pk_list) and len(pk_list) == len(parameters_list)):
      raise PumpWoodException('Length of action_list, pk_list and parameters_list must be the same')

    url_list = []
    for i in range(len(action_list)):
      url_str = "/rest/%s/actions/%s/" % ( model_class.lower(), action_list[i])
      pk = pk_list[i]
      if pk is not None:
        url_str = url_str + str(pk) + '/'
      url_list.append( url_str )
    
    return self.parallel_post( url_list=url_list, data=parameters_list, max_parallel_calls=max_parallel_calls, return_details=return_details )

  def parallel_pivot(self, model_class, query_list=[], max_parallel_calls=20, return_details=False):
    '''Pivots object data acording to columns specified.
       
        Args:
          model_class (str): Model class to be pivoted.
          columns (str): Fields to be used as columns.
          format (str): Format to be used to convert pandas.DataFrame to dictionary.
          filter_dict (dict): Dictionary to to be used in objects.filter argument (Same as list end-point).
          exclude_dict (dict): Dictionary to to be used in objects.exclude argument (Same as list end-point).
          ordering_list (list): Dictionary to to be used in objects.order_by argument (Same as list end-point).
        
        Returns:
          dict or list: Depends on format type used to convert pandas.DataFrame

        Raises:
          Dependends on backend implementation

        Example:
          No example yet.
    '''

    url_str = "/rest/%s/pivot/" % ( model_class.lower(), )
    data = []
    for q in query_list:
      if type(q) != dict:
        raise PumpWoodException('All members of query_list must be dict')
      else:
        dict_to_add = {'filter_dict': q.get('filter_dict', {})
                     , 'exclude_dict': q.get('exclude_dict', {})
                     , 'ordering_list': q.get('ordering_list', [])
                     , 'columns': q.get('columns', [])
                     , 'format': q.get('format', 'list')}
        data.append( dict_to_add )
    return self.parallel_post(url_list=url_str, data=data, max_parallel_calls=max_parallel_calls, return_details=return_details)