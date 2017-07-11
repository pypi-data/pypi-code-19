import functools
import json

import requests

from apprendaapipythonclient.api_client import ApiClient
from apprendaapipythonclient.services.DepagingService import DepagingService


class ApprendaAPIClient(object):
    internalClient = None
    portal = None

    # Constructor for the client
    def __init__(self, host, portal, username, password):
        self.portal = portal
        self.internalClient = self.connect(self, host, portal, username, password)
        self.internalClient.set_default_header("ApprendaSessionToken", self.sessionToken)
        self.internalClient.set_portal(portal)

    @staticmethod
    def connect(self, host, portal, username, password):
        # We need to create a session with the Apprenda Platform and store the authorization token for further use
        payload = '{"Username": "' + username + '", "Password": "' + password + '", "TenantAlias": null}'
        headers = {'Content-Type': 'application/json; charset=utf-8'}

        # hack to avoid tenant specification with account portal
        if portal != 'account':
            url = host + '/authentication/api/v1/sessions/' + portal
        else:
            url = host + '/authentication/api/v1/sessions/soc'
        response = requests.post(url, data=payload, headers=headers, verify=False)

        if response.status_code == 201:
            self.sessionToken = json.loads(response.content)['apprendaSessionToken']
            return ApiClient(host + '/' + portal, "ApprendaSessionToken", self.sessionToken)
        elif response.status_code == 400:
            raise IOError(
                'The provided credentials are not valid. Please provide the correct username/password')
        else:
            raise Exception('There was an issue connecting to the platform')

    """
    Worker function to begin retrieving results in a paged format.  This creates a generator, that returns an iterator
    """
    @staticmethod
    def get_paged_items_start(search_function, page_size):
        kwargs = {'page_size': page_size, 'page_number': 1}
        return search_function(**kwargs)

    """
    Worker function to continue retrieving results from a paged format.  
    Assumes the function takes page_size and page_number as params
    """
    @staticmethod
    def get_paged_items_next(search_function, page_size, url):
        page = DepagingService.extract_page_number_from_url(url)

        kwargs = {'page_size': page_size, 'page_number': str(page + 1)}
        return search_function(**kwargs)

    """
    Worker function to get depaged results when the search function is used for both first and next
    """
    def get_depager(self, search_function, page_size):
        function_arguments = [search_function, page_size]
        start_function = functools.partial(self.get_paged_items_start, *function_arguments)

        next_function = functools.partial(self.get_paged_items_next, *function_arguments)

        return DepagingService(start_function, next_function)