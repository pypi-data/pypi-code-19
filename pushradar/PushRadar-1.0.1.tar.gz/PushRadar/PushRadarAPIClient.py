import time
from contextlib import closing
from urllib.parse import urlencode
from urllib.request import urlopen


class PushRadarAPIClient:
    """ A client that interacts with PushRadar's API. """

    # ------------------------------
    # Initialisation & configuration
    # ------------------------------

    # PushRadar's API endpoint
    api_endpoint = "https://api.pushradar.com/v1"

    # The user's API secret
    api_secret = ""

    def __init__(self, api_secret):
        """ Creates a new instance of the PushRadar API client with the specified API secret. """
        # Set the API secret
        self.api_secret = api_secret

    # ------------------------------
    # API methods
    # ------------------------------

    def post(self, destination, data):
        """ Performs a POST request to the API destination specified. """
        # Add in the fields that should be sent with each request
        data["api_secret"] = self.api_secret.strip()
        data["client_platform"] = "python"
        data["request_sent_at"] = time.time()
        # Make sure the destination does not contain the base URL
        destination = destination.replace(self.api_endpoint, "").strip("/")
        # Construct the actual URL to POST the data to
        url = self.api_endpoint + "/" + destination
        # Send a POST request to the server
        post_data = urlencode(data).encode()
        with closing(urlopen(url, post_data)) as response:
            return response.read().decode()