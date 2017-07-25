from opfront.resource import OpfrontResource


class UserResource(OpfrontResource):

    def me(self):
        res_url = '{0}/me'.format(self._endpoint)
        body = self._client.do_request(res_url, 'GET')

        return self._make_model(**body)
