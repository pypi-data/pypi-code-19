from hudai import HudAiError

class Resource(object):
    def __init__(self, client, base_path=''):
        """
        :param client: API client
        """

        if client is None:
            raise HudAiError('client required', 'initialization_error')

        self._client = client
        self._base_path = base_path


    def request(self, params):
        """
        Abstracted request method, request config is defined in the resource itself
        :param params:
        :return:
        """
        method = params.get('method', 'get').lower()
        query_params = params.get('params', {})
        url = params.get('url', '')
        data = params.get('data', {})

        path = self._build_path(url, query_params)

        if method == 'get':
            response = self._client.get(path, params=query_params, data=data)

        elif method == 'post':
            response = self._client.post(path, params=query_params, data=data)

        elif method == 'put':
            response = self._client.put(path, params=query_params, data=data)

        elif method == 'patch':
            response = self._client.patch(path, params=query_params, data=data)

        elif method == 'delete':
            response = self._client.delete(path, params=query_params, data=data)

        else:
            raise ValueError('method.invalid:{}'.format(method))

        return response.json()


    def _build_path(self, url, query_params):
        """
        Build the url path string
        :return url:
        """
        path = "{}{}".format(self._base_path, url)

        if query_params is None:
            return path

        return path.format(**query_params)
