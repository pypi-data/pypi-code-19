"""HubSpot class"""

from hubspyt.contacts import Contacts

class HubSpot(object):
    """HubSpot's API"""

    def __init__(self, api_key):
        """Set API key"""

        self.api_key = api_key
        self.contacts = Contacts(self.api_key)
