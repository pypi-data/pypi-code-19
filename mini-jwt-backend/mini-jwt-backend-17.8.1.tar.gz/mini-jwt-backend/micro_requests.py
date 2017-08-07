import requests


class RequestFactory(object):
    jwt_token = None
    basic_auth = None

    def __init__(self, jwt_token=None, basic_auth=None):
        self.jwt_token = jwt_token
        self.basic_auth = basic_auth
        super().__init__()

    def get(self, *args, **kwargs):
        if self.jwt_token is not None:
            result = self._get_using_jwt(*args, **kwargs)
            if result is not None:
                return result

        if self.basic_auth is not None:
            result = self._get_using_basic_auth(*args, **kwargs)
            if result is not None:
                return result

        result = self._get_no_auth(*args, **kwargs)
        if result is not None:
            return result

        # I'm not even sure it's possible to ever get here, but it's good to cover all bases.
        raise RuntimeError('Unable to obtain a result. No gets were got.')

    def _get_using_jwt(self, *args, **kwargs):
        headers = kwargs.get('headers', dict())
        headers['Authorization'] = 'JWT ' + self.jwt_token
        kwargs['headers'] = headers
        return requests.get(*args, **kwargs)

    def _get_using_basic_auth(self, *args, **kwargs):
        headers = kwargs.get('headers', dict())
        headers['Authorization'] = 'Basic ' + self.basic_auth
        kwargs['headers'] = headers
        return requests.get(*args, **kwargs)

    def _get_no_auth(self, *args, **kwargs):
        return requests.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.jwt_token is not None:
            result = self._post_using_jwt(*args, **kwargs)
            if result is not None:
                return result

        if self.basic_auth is not None:
            result = self._post_using_basic_auth(*args, **kwargs)
            if result is not None:
                return result

        result = self._post_no_auth(*args, **kwargs)
        if result is not None:
            return result

        # I'm not even sure it's possible to ever get here, but it's good to cover all bases.
        raise RuntimeError('Unable to obtain a result. No posts were posted.')

    def _post_using_jwt(self, *args, **kwargs):
        headers = kwargs.get('headers', dict())
        headers['Authorization'] = 'JWT ' + self.jwt_token
        kwargs['headers'] = headers
        return requests.post(*args, **kwargs)

    def _post_using_basic_auth(self, *args, **kwargs):
        headers = kwargs.get('headers', dict())
        headers['Authorization'] = 'Basic ' + self.basic_auth
        kwargs['headers'] = headers
        return requests.post(*args, **kwargs)

    def _post_no_auth(self, *args, **kwargs):
        return requests.post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.jwt_token is not None:
            result = self._delete_using_jwt(*args, **kwargs)
            if result is not None:
                return result

        if self.basic_auth is not None:
            result = self._delete_using_basic_auth(*args, **kwargs)
            if result is not None:
                return result

        result = self._delete_no_auth(*args, **kwargs)
        if result is not None:
            return result

        # I'm not even sure it's possible to ever get here, but it's good to cover all bases.
        raise RuntimeError('Unable to obtain a result. No deletes were deleted.')

    def _delete_using_jwt(self, *args, **kwargs):
        headers = kwargs.get('headers', dict())
        headers['Authorization'] = 'JWT ' + self.jwt_token
        kwargs['headers'] = headers
        return requests.delete(*args, **kwargs)

    def _delete_using_basic_auth(self, *args, **kwargs):
        headers = kwargs.get('headers', dict())
        headers['Authorization'] = 'Basic ' + self.basic_auth
        kwargs['headers'] = headers
        return requests.delete(*args, **kwargs)

    def _delete_no_auth(self, *args, **kwargs):
        return requests.delete(*args, **kwargs)
