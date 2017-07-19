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
        method = params.get('method', 'GET')
        query_params = params.get('params', {})
        url = params.get('url', '')
        data = params.get('data', {})

        path = self._build_path(url, query_params)

        return self._client.make_request(method, path, query_params, data)

    def _build_path(self, url, query_params):
        """
        Build the url path string
        :return url:
        """
        path = "{}{}".format(self._base_path, url)

        if query_params is None:
            return path

        return path.format(**query_params)
