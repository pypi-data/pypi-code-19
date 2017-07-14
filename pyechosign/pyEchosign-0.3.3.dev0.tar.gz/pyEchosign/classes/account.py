import logging

import requests

from .library_document import LibraryDocumentsEndpoint
from .agreement import AgreementEndpoints
from pyEchosign.utils import endpoints

log = logging.getLogger('pyOutlook - {}'.format(__name__))
__all__ = ['EchosignAccount']


class EchosignAccount(object):
    """ Saves OAuth Information for connecting to Echosign
    
    Attributes:
        access_token: The OAuth Access token to use for authenticating to Echosign
        user_id: The ID of the user to specify as the API caller, if not provided the caller is inferred from the token
        user_email: The email of the user to specify as the API caller, if not provided the caller is inferred from the token
        api_access_point: The API endpoint used as a base for all API calls
    """
    def __init__(self, access_token: str, **kwargs):
        self.access_token = access_token
        self.user_id = kwargs.pop('user_id', None)
        self.user_email = kwargs.pop('user_email', None)

        log.debug('EchosignAccount instantiated. Requesting base_uris from API...')
        headers = {'Access-Token': access_token}
        response = requests.get(endpoints.BASE_URIS, headers=headers)
        response_body = response.json()
        log.debug('Received status code {} from Echosign API'.format(response.status_code))
        self.api_access_point = response_body.get('api_access_point') + endpoints.API_URL_EXTENSION

    access_token = None

    def get_agreements(self, query=None):
        """ Gets all agreements for the EchosignAccount

        Keyword Args:
            query: (str) A search query to filter results by
        
        Returns: An iterator of :class:`Agreement <pyEchosign.classes.agreement.Agreement>` objects
        """
        return AgreementEndpoints(self).get_agreements(query=query)

    def get_library_documents(self):
        """ Gets all Library Documents for the EchosignAccount

        Returns: A list of :class:`Agreement <pyEchosign.classes.library_document.LibraryDocument>` objects
        """
        return LibraryDocumentsEndpoint(self).get_library_documents()


