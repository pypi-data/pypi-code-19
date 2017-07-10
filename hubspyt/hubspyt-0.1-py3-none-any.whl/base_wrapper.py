"""Base API endpoint class"""

class BaseWrapper(object):
    """Provides a baseline for the API endpoint wrappers"""

    def __init__(self, api_key):
        """Set API key"""

        self.api_key = api_key
        self.base_url = 'https://api.hubapi.com'
        self.contacts_base_url = '/contacts/v1'
        self.contacts_all_url = '/lists/all/contacts/all'
        self.contacts_batch_url = '/contact/batch'

    def _get_url(self, endpoint, params=None):
        """Constructs a url with a given endpoint and params"""

        base_url = self.base_url
        api_key = self.api_key
        api_key_param = '?hapikey={api_key}'.format(api_key=api_key)

        url = '{base_url}{endpoint}'.format(base_url=base_url, endpoint=endpoint)
        url += api_key_param

        if params is not None:
            for param in params:
                if param.get('value') is not None:
                    url += '&{name}={value}'.format(
                        name=param.get('name'),
                        value=param.get('value'),
                    )

        return url
