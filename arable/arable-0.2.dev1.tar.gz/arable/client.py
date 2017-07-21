from base64 import b64encode
import requests


class ArableClient(object):
    """A client for connecting to Arable and making data queries."""
    base_url = "https://api.arable.com/dev3"
    param_options = {"devices", "end", "format", "limit", "location",
                     "measure", "meta", "order", "select", "start"}

    def __init__(self):
        self.header = None

    def _login(self, email=None, password=None, org=None):
        url = "{0}/auth/user/{1}".format(ArableClient.base_url, org)
        # utf-8 encode/decode for python3 support
        token = b64encode("{0}:{1}".format(email, password).encode('utf-8')).decode('utf-8')
        headers = {"Authorization": "Basic " + token}

        r = requests.post(url, headers=headers)
        if r.status_code == 200:
            return {"Authorization": "Bearer " + r.json()['access_token']}
        else:
            r.raise_for_status()

    def check_connection(self):
        """Returns True if client has auth token, raises an exception if not"""
        if not self.header:
            raise Exception("Authentication exception: not connected.")
        return True

    def connect(self, email=None, password=None, org=None, apikey=None):
        """Logs the client in to the API.
            :param email : user email address
            :param password : user password
            :param group_id : user's group ID (a UUID string)
            :param apikey: user's apikey (a UUID string)
        """
        if apikey:
            self.header = {"Authorization": apikey}
            return
        elif not all([email, password, org]):
            raise Exception("Missing parameter; connect requires email, password, and tenant")  # NOQA
        try:
            self.header = self._login(email, password, org)
        except Exception as e:
            raise Exception("Failed to connect:\n{}".format(str(e)))

    def devices(self, device_id=None, name=None):
        """ Lists the devices associated with the user's group.
            :param device_id : optional; look up a single device by id; takes
            precedence over name, if present
            :param name : optional; look up a single device by name (serial);
            ignored if device_id is present
        """

        self.check_connection()

        url = ArableClient.base_url + "/devices"
        if device_id:
            url += "/" + device_id
        elif name:
            url += "?name=" + name

        r = requests.get(url, headers=self.header)
        if 200 == r.status_code:
            return r.json()
        else:
            r.raise_for_status()

    def query(self, **kwargs):
        """Query Arable pod data.
            :param devices : optional; list of devices to retrieve data for;
            ignored if deployments are specified
            :param location : optional; id of location to retrieve data for;
            devices list is ignored if this parameter is provided
            :param start : optional; beginning of query time range
            :param end : optional; end of query time range
            :param order : optional; "time" (time ascending) or "-time" (time
            descending)
            :param limit : optional; maximum number of data points to return;
            defaults to 1000
            :param format : optional; use format=csv to get csv-formatted data;
            otherwise data is returned as json
            :param select : optional; "all", "spectrometer", or "microclimate"
        """

        self.check_connection()

        url = ArableClient.base_url + "/data"
        params = {}
        for param in ArableClient.param_options:
            if kwargs.get(param):
                params[param] = str(kwargs[param])
        if not params.get('order'):
            params['order'] = '-time'
        if not params.get('limit'):
            params['limit'] = '1000'

        r = requests.get(url, headers=self.header, params=params)

        if r.status_code == 200:
            if params.get('format') == 'csv':
                return r.text
            else:
                return r.json()
        else:
            r.raise_for_status()
