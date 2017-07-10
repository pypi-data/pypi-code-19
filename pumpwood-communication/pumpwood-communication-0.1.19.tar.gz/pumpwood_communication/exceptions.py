# -*- coding: utf-8 -*-
class ModelWronglyDefined(Exception):
  pass

class WrongModelEstimationWorkflow(Exception):
  pass

class WrongDataLoading(Exception):
  pass

class PumpWoodException(Exception):
  pass

class PumpWoodUnauthorized(Exception):
  pass

class PumpWoodForbidden(Exception):
  pass

class ObjectDoesNotExist(Exception):
  pass

def SerializerException(exc):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    # Now add the HTTP status code to the response.
    if isinstance(exc, ModelWronglyDefined):
      return {'pk':None, 'model_class': 'Error', 'type': 'ModelWronglyDefined', 'msg': str(exc)}
      
    if isinstance(exc, WrongModelEstimationWorkflow):
      return {'pk':None, 'model_class': 'Error' ,'type': 'WrongModelEstimationWorkflow', 'msg': str(exc)}

    if isinstance(exc, WrongDataLoading):
      return {'pk':None, 'model_class': 'Error' ,'type': 'WrongDataLoading', 'msg': str(exc)}

    if isinstance(exc, PumpWoodException):
      return {'pk':None, 'model_class': 'Error' ,'type': 'PumpWoodException', 'msg': str(exc)}

    if isinstance(exc, ObjectDoesNotExist):
      return {'pk':None, 'model_class': 'Error' ,'type': 'ObjectDoesNotExist', 'msg': str(exc)}

    if isinstance(exc, PumpWoodUnauthorized):
      return {'pk':None, 'model_class': 'Error' ,'type': 'PumpWoodUnauthorized', 'msg': str(exc)}

    if isinstance(exc, PumpWoodForbidden):
      return {'pk':None, 'model_class': 'Error' ,'type': 'PumpWoodForbidden', 'msg': str(exc)}

    return None

exceptions_dict = {'PumpWoodUnauthorized':         PumpWoodUnauthorized
                 , 'ModelWronglyDefined':          ModelWronglyDefined
                 , 'WrongModelEstimationWorkflow': WrongModelEstimationWorkflow
                 , 'WrongDataLoading':             WrongDataLoading
                 , 'PumpWoodException':            PumpWoodException
                 , 'PumpWoodUnauthorized':         PumpWoodUnauthorized
                 , 'PumpWoodForbidden':            PumpWoodForbidden
                 , 'ObjectDoesNotExist':           ObjectDoesNotExist }