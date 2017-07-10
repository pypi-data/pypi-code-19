import pyrebrandly.version
import pyrebrandly.exceptions as exc

import requests
import json

class Request:
    """
    Base class for Rebrandly API actions
    """

    base_uri = 'api.rebrandly.com/v1'

    @property
    def __version__(self):
        """
        :returns: version
        """
        return repr(pyrebrandly.version.pyrebrandly)

    def __init__(self, api_key='', domain_name='rebrand.ly', domain_id='', team_id=None):
        """
        Initialize the class

        :param api_key: An API key from your account
        :type api_key: str
        :param domain_name: A domain name to use against the API
        :type domain_name: str
        :param domain_id: Your optional hexadecimal Domain ID
        :type domain_id: str
        :param team_id: Optional Team ID
        :type team_id: str
        """

        hdrs = {}

        self.api_key = api_key
        self.domain_name = domain_name
        self.domain_id = domain_id
        self.uri = base_uri

        if domain_id and domain_name:
            self.domain = {
                'fullName': domain_name,
                'id':       domain_id
            }

        hdrs['Content-Type'] = 'application/json'
        hdrs['apikey'] = api_key
        if team_id:
            hdrs['team'] = team_id

    def make_path(self, path, params, uri=base_uri):
        """

        :param path: Method path
        :type path: str
        :param params: Path Parameters (ID, etc.)
        :type params: str
        :param uri: API endpoint
        :type uri: str
        :returns: Joined path
        :rtype: str
        """
        return _join(uri, path, params)


class Links(Request):
    """

    Rebrandly.Links class

    For managing links, including adding, removing, updating, returning
    """
    path = "links"

    def list(options=None):
        """
        Lists links that follow certain criteria

        orderBy => {createdAt, updatedAt, title, slashtag} -- Sort by

        orderDir=> {desc, asc} -- Order Direction

        offset => N -- Skip N links

        limit => N -- Limit to N links

        favourite => true/false -- optional, shows or hides favourites if given

        status => active -- Sort by status, {active, trashed}

        :param options: A Dict of options
        :type options: dict

        :returns: RebrandlyResponse

        """
        if not options:
            r = requests.get('/', options)
            status_code = r.status_code
            response = RebrandlyResponse.raise_exception(status_code, r.json())
            if response == 'ok':
                return response['response']

    def get(id=None, options=None):
        """
        :param id: Link ID to lookup
        :type id: str
        :param options: A Dict of options
        :type options: dict

        :returns: RebrandlyResponse
        """
        if id is None:
            raise exc.APIError
        if options is None:
            return requests.get("/{}")
        else:
            return requests.get("/{}", options)

    def count(options=None):
        """
        :param options: A Dict of options
        :type options: dict

        :returns: RebrandlyResponse
        """
        if options is None:
            return requests.get("/count")
        else:
            return requests.get('/count', options)

    def new(method=None, options=None):
        """
        :param method: POST or GET HTTP method
        :type method: str
        :param options: Dict of Options
        :type options: dict

        :returns: RebrandlyResponse

        """
        if method == 'get':
            if options:
                return requests.get('/new')
            else:
                return requests.get('/new', options)
        if method == 'post':
            if options is None:
                return requests.get('/')
            else:
                return requests.get('/', options)

    def update(id=None, options=None):
        """
        :param id: Link ID to update
        :type id: str
        :param options: A Dict of options
        :type options: dict
        """
        if options is None:
            raise exc.APIError("Rebrandly#update must be used with options.")
        else:
            return requests.post("/{}", options)

    def delete(id=None, options=None):
        """
        :param id: Link ID
        :type id: str
        :param options: Options Dict
        :type options: dict
        """
        if id == None:
            raise exc.APIError("No ID to delete")

        else:
            if options:
                return requests.delete("/{}".format(id))
            else:
                if options.keys == ['trash']:
                    if options['trash'] == True or options['trash'] == False:
                        return requests.delete("/{}".format(id), options)
                    else:
                        raise exc.APIError("Rebrandly#delete supports one key only, 'trash', which is a boolean")
                else:
                    raise exc.APIError("Rebrandly#delete supports one key only, 'trash', which is a boolean")


class Domain(Request):
    """
    """
    path = 'domains'

    def list(options=None):
        """
        List the domains in the account.

        :param options:
            active
                optional boolean -- true/false
            type:
                optional string -- user/service
            orderBy:
                optional string -- criteria to filter by/ createdAt, updatedAt, fullName
            orderDir:
                optional string -- Order Direction, asc/desc
            offset:
                optional integer -- skip N domains
            limit:
                optional integer -- limit to N domains
        :type options: dict

        :returns: RebrandlyResponse
        """
        if options is None:
            return requests.get('/')
        else:
            return requests.get('/', options)

    def get(id=None):
        """
        Return information about a certain domain.

        :param id: domain ID to pull information about
        :type id: str

        :returns: RebrandlyResponse
        """
        return requests.get("/{}".format(id))

    def count(options=None):
        """
        Count the number of Domains the account has

        :param options: Options
        :type options: dict

        :returns: RebrandlyResponse

        """
        if options is None:
            return requests.get("/count")
        else:
            return requests.get("/count", options)


class Account(Request):
    """

    """
    path = 'account'

    def get(options=None):
        """
        Get account information

        :param dict options: A dict of options

        """

    def teams(options=None):
        """
        :param options: Options to filter teams by
        :type options: dict

        :returns: RebrandlyResponse
        """
        if options is None:
            return requests.get("/teams")
        else:
            return requests.get("/teams", options)


class Response(requests.Response):

    def __init__(self, *args, **kwargs):
        self.tuple = {
            'msg': args,
            'extra': kwargs
        }
    def __str__(self):
        return self.tuple

    @staticmethod
    def raise_exception(code, rebrandly_response):
        """
        Raise an exception based on whether we got an error, and which one.

        :param code:
        :type code:
        :param rebrandly_response:
        :type rebrandly_response:
        :return:
        :rtype:
        """
        if code == 200:
            return {
                'status': 'ok',
                'code': 200,
                'response': rebrandly_response
            }
            # Everything went well, continue.
        elif code == 400:
            raise exc.BadRequestError(rebrandly_response.code, rebrandly_response.message)
        elif code == 401:
            raise exc.NotAuthorizedError(rebrandly_response.code, rebrandly_response.message)
        elif code == 403:
            if rebrandly_response.code == 'AlreadyExists':
                raise exc.AlreadyExistsError(rebrandly_response.code, rebrandly_response.message)
            else:
                raise exc.InvalidFormatError(rebrandly_response.code, rebrandly_response.message)
        if code == 404:
            raise exc.NotFoundError(rebrandly_response.code, rebrandly_response.message)
        if code == 500:
            raise exc.InternalServerError(rebrandly_response.code, rebrandly_response.message)
        if code == 502:
            raise exc.BadGatewayError(rebrandly_response.code, rebrandly_response.message)
        if code == 503:
            raise exc.APIUnavailableError(rebrandly_response.code, rebrandly_response.message)
        if code == 504:
            raise exc.APITimeoutError(rebrandly_response.code, rebrandly_response.message)
