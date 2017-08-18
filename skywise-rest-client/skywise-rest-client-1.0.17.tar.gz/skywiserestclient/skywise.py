import json
import logging
import requests
from requests.auth import HTTPBasicAuth
from voluptuous import REMOVE_EXTRA, ALLOW_EXTRA
from requests.exceptions import HTTPError

logger = logging.getLogger('skywise-request-client')

try:
    import grequests
except:
    logger.warning('grequests failed to import. Async methods are unavailable.')


def _filter_dict(d):
    return dict((k, v) for k, v in d.iteritems() if v)


def map_requests(skywise_requests, raise_on_error=True):
    return SkyWiseResource.map(skywise_requests, raise_on_error=raise_on_error)


def initialization_required(f):
    def wrap(self, *args, **kwargs):
        try:
            self.id
        except:
            msg = 'This resource has not yet been saved.'
            raise SkyWiseResourceNotInitialized(msg)
        return f(self, *args, **kwargs)
    return wrap


class SkyWiseException(Exception):
    pass


class SkyWiseJSONDeserializationException(Exception):
    pass


class SkyWiseJSONSerializationNotImplemented(Exception):
    pass


class SkyWiseResourceNotInitialized(Exception):
    pass


class SkyWiseRequest(object):
    """ A storage object for the request, its resource type, and data it should
        be tagged with after the request has completed. """

    def __init__(self, greq, klass):
        self.greq = greq
        self.klass = klass
        self._tags = {}

    def tag(self, **kwargs):
        for k, v in kwargs.iteritems():
            self._tags[k] = v

    def tags(self):
        return self._tags


class SkyWiseResource(object):

    _session = None
    _headers = None
    _media_type = None
    _content_type = None
    _version = 1
    _site = None
    _user = None
    _password = None
    _args = None
    _map_size = 2
    _use_session_for_async = False
    _hooks = {}

    def save(self, **kwargs):
        raise NotImplementedError()

    @classmethod
    def _unpack_response(self, response):
        raise NotImplementedError()

    @classmethod
    def _s(cls):
        """ Returns the current session for the resource. """
        if not cls._session:
            cls._session = requests.Session()
        if cls.get_user() or cls.get_password():
            cls._session.auth = (cls.get_user(), cls.get_password())
        return cls._session

    @classmethod
    def set_response_hook(cls, hook):
        cls._hooks['response'] = hook

    @classmethod
    def get_session(cls):
        return cls._s()

    @classmethod
    def set_session(cls, session):
        cls._session = session

    @classmethod
    def get_media_type(cls):
        return cls._media_type

    @classmethod
    def set_media_type(cls, media_type):
        cls._media_type = media_type

    @classmethod
    def get_map_size(cls):
        return cls._map_size

    @classmethod
    def set_map_size(cls, map_size):
        cls._map_size = map_size

    @classmethod
    def get_site(cls):
        return cls._site

    @classmethod
    def set_site(cls, site):
        cls._site = site

    @classmethod
    def get_user(cls):
        return cls._user

    @classmethod
    def set_user(cls, username):
        cls._user = username

    @classmethod
    def get_password(cls):
        return cls._password

    @classmethod
    def set_password(cls, password):
        cls._password = password

    @classmethod
    def get_headers(cls):
        headers = cls._headers or {}
        headers['Accept'] = "%s; version=1" % cls._media_type
        headers['Content-Type'] = cls._content_type
        return headers

    @classmethod
    def set_headers(cls, headers):
        cls._headers = headers

    @classmethod
    def set_use_session_for_async(cls, b):
        cls._use_session_for_async = b

    @classmethod
    def get_use_session_for_async(cls):
        return cls._use_session_for_async

    @classmethod
    def _resource_path(cls, resource_id, **kwargs):
        p = cls._path.format(**kwargs)
        return "%s%s/%s" % (cls.get_site(), p, resource_id)

    @classmethod
    def _list_path(cls, **kwargs):
        p = cls._path.format(**kwargs)
        return "%s%s" % (cls.get_site(), p)

    @classmethod
    def _path_args(cls, **kwargs):
        if cls._args and kwargs:
            d = _filter_dict(kwargs)
            cls._args.extra = REMOVE_EXTRA
            return cls._args(d)

    @classmethod
    def find(cls, id_=None, **kwargs):
        r = cls._get(id_, **kwargs) if id_ else cls._get_list(**kwargs)
        return cls._unpack_response(r)

    @classmethod
    def find_by_id_async(cls, resource_id, headers=None):
        if headers:
            _headers = cls.get_headers()
            _headers.update(headers)
            headers = _headers
        else:
            headers = cls.get_headers()
        url = cls._resource_path(resource_id)
        if cls._use_session_for_async:
            greq = grequests.get(url, session=cls._s(), headers=headers)
        else:
            greq = grequests.get(url,
                                 auth=HTTPBasicAuth(cls.get_user(),
                                                    cls.get_password()),
                                 headers=headers,
                                 hooks=cls._hooks)
        return SkyWiseRequest(greq, cls)

    @classmethod
    def find_async(cls, id_=None, headers=None, **kwargs):

        if id_:
            return cls.find_by_id_async(id_, headers=headers, **kwargs)

        if headers:
            _headers = cls.get_headers()
            _headers.update(headers)
            headers = _headers
        else:
            headers = cls.get_headers()

        # Request a list of resources
        url = cls._list_path(**kwargs)
        args = cls._path_args(**kwargs)
        if cls._use_session_for_async:
            r = grequests.get(url,
                              session=cls._s(),
                              headers=headers,
                              params=args,
                              hooks=cls._hooks)
        else:
            r = grequests.get(url,
                              auth=HTTPBasicAuth(cls.get_user(), cls.get_password()),
                              headers=headers,
                              params=args,
                              hooks=cls._hooks)
        return SkyWiseRequest(r, cls)

    def destroy(self, **kwargs):
        url = self._resource_path(self.id, **kwargs)
        res = self._s().delete(url,
                               hooks=self._hooks)
        if res.status_code != 200:
            res.raise_for_status()
        self.id = None

    @classmethod
    def map(cls, skywise_requests, raise_on_error=True):
        """ Takes a list of SkyWise Requests, calls them asynchronously, and
            returns SkyWise Resources. """
        req_list = [sr.greq for sr in skywise_requests]
        results = grequests.map(req_list, size=cls.get_map_size())
        if len(results) != len(skywise_requests):
            raise SkyWiseException("Number results in ansynchronous request not the same as number requests.")

        # Verify All Requests Were Successful
        successful_requests = []
        for i, result in enumerate(results):
            if not result and raise_on_error:
                raise Exception("No result returned.")
            elif result and result.status_code != 200 and raise_on_error:
                result.raise_for_status()
            else:
                successful_requests.append([skywise_requests[i], result])

        skywise_resources = []
        for request in successful_requests:
            skywise_request = request[0]
            response = request[1]

            resource = skywise_request.klass._unpack_response(response)
            if type(resource) is SkyWiseResourceList:
                resources = resource
                resource_list = []
                for resource in resources:
                    for k, v in skywise_request.tags().iteritems():
                        resource.__setattr__(k, v)
                    resource_list.append(resource)
                skywise_resources.append(resource_list)
            else:
                for k, v in skywise_request.tags().iteritems():
                    resource.__setattr__(k, v)
                skywise_resources.append(resource)
        return SkyWiseResourceList(skywise_resources)

    @classmethod
    def _get(cls, id_, headers=None, **kwargs):
        if headers:
            _headers = cls.get_headers()
            _headers.update(headers)
            headers = _headers
        else:
            headers = cls.get_headers()
        url = cls._resource_path(id_, **kwargs)
        args = cls._path_args(**kwargs)
        res = cls._s().get(url, params=args, headers=headers, hooks=cls._hooks)
        if res.status_code != 200:
            try:
                data = json.loads(res.content)
                raise HTTPError(data['message'])
            except ValueError:
                res.raise_for_status()
        return res

    @classmethod
    def _get_list(cls, headers=None, **kwargs):
        if headers:
            _headers = cls.get_headers()
            _headers.update(headers)
            headers = _headers
        else:
            headers = cls.get_headers()
        url = cls._list_path(**kwargs)
        args = cls._path_args(**kwargs)
        res = cls._s().get(url, params=args, headers=headers, hooks=cls._hooks)
        if res.status_code != 200:
            try:
                data = json.loads(res.content)
                raise HTTPError(data['message'])
            except ValueError:
                res.raise_for_status()
        return res


class SkyWiseImage(object):

    def __init__(self):
        self._data = {}

    @classmethod
    def _unpack_response(cls, response):
        # Load Image
        resource = cls()
        resource._r = response
        return resource

    def content(self):
        """ Returns the decoded request body as bytes. """
        try:
            self._r
        except:
            raise Exception("Response not yet received for image resource.")
        return self._r.content

    def close(self):
        """ Closes the current connection to the server. """
        try:
            self._r
        except:
            raise Exception("Response not yet received for image resource.")
        self._r.close()


class SkyWiseJSON(object):

    _deserialize = None
    _serialize = None
    _media_type = 'application/vnd.wdt+json'
    _content_type = 'application/json'

    def __init__(self):
        self._data = {}
        self.id = None
        if self._deserialize:
            self._deserialize.extra = ALLOW_EXTRA
        if self._serialize:
            self._serialize.extra = REMOVE_EXTRA

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            return super(SkyWiseJSON, self).__getattr__(name)
        return self._data[name]

    def __setattr__(self, name, value):
        if name == '_data' or name.startswith('_'):
            super(SkyWiseJSON, self).__setattr__(name, value)
            return
        self._data[name] = value

    def save(self, **kwargs):
        kwargs.update(self._data)
        if not self.id:
            self._post(**kwargs)
        else:
            self._put(**kwargs)
        return self.id

    def destroy(self, **kwargs):
        kwargs.update(self._data)
        url = self._resource_path(self.id, **kwargs)
        res = self._s().delete(url,
                               headers=self.get_headers(),
                               hooks=self._hooks)
        if res.status_code != 200:
            res.raise_for_status()
        self.id = None

    def json(self):
        if self._serialize is None:
            msg = "The resource has not implemented a method to serialize its data to JSON."
            raise SkyWiseJSONSerializationNotImplemented(msg)
        return self._serialize(self._data)

    def _post(self, **kwargs):
        url = self._list_path(**kwargs)
        data = self._data
        if self._serialize:
            self._serialize.extra = REMOVE_EXTRA
            data = self._serialize(data)
        res = self._s().post(url,
                             data=json.dumps(data),
                             headers=self.get_headers(),
                             hooks=self._hooks)
        if res.status_code != 201:
            res.raise_for_status()
        data = res.json()
        if self._deserialize:
            data = self._deserialize(data)
        self._data = data

    def _put(self, **kwargs):
        url = self._resource_path(self.id, **kwargs)
        data = self._data
        if self._serialize:
            self._serialize.extra = REMOVE_EXTRA
            data = self._serialize(data)
        res = self._s().put(url,
                            data=json.dumps(data),
                            headers=self.get_headers(),
                            hooks=self._hooks)
        if res.status_code != 200:
            res.raise_for_status()
        data = res.json()
        if self._deserialize:
            data = self._deserialize(data)
        self._data = data

    @classmethod
    def _unpack_response(cls, response):
        # Load JSON
        data = response.json()

        # Deserialize a single resource
        if isinstance(data, dict):
            resource = cls()
            resource._load_json(data)
            return resource

        # Deserialize a list of resources
        resources = []
        for j in data:
            resource = cls()
            resource._load_json(j)
            resources.append(resource)
        return SkyWiseResourceList(resources)

    def _load_json(self, j):
        if self._deserialize:
            try:
                data = self._deserialize(j)
            except:
                err = "The response for your requested resource returned an invalid format or data value. The response is as follows:  %s"
                err = err % json.dumps(j)
                raise SkyWiseJSONDeserializationException(err)
        self._data = data


class SkyWiseResourceList(object):

    def __init__(self, l=None):
        self._list = l or []

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        return self._list[key]

    def __repr__(self):
        return self._list.__repr__()

    def __str__(self):
        return self._list.__str__()

    def __setitem__(self, key, value):
        self._list[key] = value

    def __delitem__(self, key):
        del self._list[key]

    def __iter__(self):
        return iter(self._list)

    def append(self, value):
        self._list.append(value)

    def extend(self, l):
        self._list.extend(l)

    def insert(self, i, x):
        self._list.insert(i, x)

    def sort(self, cmp=None, key=None, reverse=False):
        self._list.sort(cmp=cmp, key=key, reverse=reverse)

    def reverse(self):
        self._list.reverse()

    def head(self):
        return self._list[0]

    def tail(self):
        return self._list[1:]

    def init(self):
        return self._list[:-1]

    def last(self):
        return self._list[-1]

    def drop(self, n):
        return self._list[n:]

    def take(self, n):
        return self._list[:n]

    def pop(self, i=None):
        if i is None:
            return self._list.pop()
        return self._list.pop(i)

    def _key(self, group, v):
        """ Returns a key function for use in groupby. """
        current_value = v
        parts = group.split('.')
        while parts:
            part = parts.pop(0)
            try:
                current_value = current_value.__getattr__(part)
            except:
                current_value = current_value.__getattribute__(part)
        return current_value

    def _group(self, groups, values):
        data = {}
        group = groups[0]
        groups = groups[1:]
        for v in values:
            key = self._key(group, v)
            if key not in data:
                data[key] = []
            data[key].append(v)
        if groups:
            for k, v in data.iteritems():
                data[k] = self._group(groups, data[k])
        return data

    def group(self, groups):
        """ Function that returns a dictionary of the list's values grouped
            by the specified keys. """

        if not isinstance(groups, list):
            groups = [groups]

        return self._group(groups, self._list)
