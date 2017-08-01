from pydash import omit

from .error import HudAiError


class Resource(object):
    def __init__(self, client, base_path=''):
        """
        :param client: API client
        """

        if client is None:
            raise HudAiError('client required', 'initialization_error')

        self._client = client
        self._base_path = base_path


    # Standard HTTP Verbs with url params injected into the given paths


    def get(self, path, request_params):
        full_path = self._build_path(path, request_params.get('params'))

        client_params = omit(request_params, 'params')

        return self._client.get(full_path, **client_params).json()


    def post(self, path, request_params):
        full_path = self._build_path(path, request_params.get('params'))

        client_params = omit(request_params, 'params')

        return self._client.post(full_path, **client_params).json()


    def put(self, path, request_params):
        full_path = self._build_path(path, request_params.get('params'))

        client_params = omit(request_params, 'params')

        return self._client.put(full_path, **client_params).json()


    def patch(self, path, request_params):
        full_path = self._build_path(path, request_params.get('params'))

        client_params = omit(request_params, 'params')

        return self._client.patch(full_path, **client_params).json()


    def delete(self, path, request_params):
        full_path = self._build_path(path, request_params.get('params'))

        client_params = omit(request_params, 'params')

        return self._client.delete(full_path, **client_params).json()


    # CRUD actions common to many endpoints


    def _list(self, **query_params):
        return self.get('/', { 'query_params': query_params })

    def _create(self, **data):
        return self.post('/', { 'data': data })

    def _get(self, id):
        return self.get('/{id}', { 'params': {'id': id} })

    def _update(self, id, **data):
        return self.put('/{id}', { 'params': {'id': id}, 'data': data })

    def _delete(self, id):
        return self.delete('/{id}', { 'params': {'id': id} })


    # Helper functions


    def _build_path(self, url, query_params):
        """
        Build the url path string
        :return url:
        """
        path = "{}{}".format(self._base_path, url)

        if not query_params:
            return path

        return path.format(**query_params)
