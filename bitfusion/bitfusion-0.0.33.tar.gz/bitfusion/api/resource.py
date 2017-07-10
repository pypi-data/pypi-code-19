import os

from bitfusion.api.base import BaseMixin

def ResourceFactory(api_session):
  ###########################################
  # BEGIN Resource Class
  ###########################################
  class Resource(BaseMixin):
    api = api_session
    base_url = '/api/resource'

    @staticmethod
    def info():
      """Returns a dictionary containing aggregate resource info"""
      return Resource.api.get(os.path.join(Resource.base_url, 'aggregate'))

  ###########################################
  # END Resource Class
  ###########################################

  return Resource
