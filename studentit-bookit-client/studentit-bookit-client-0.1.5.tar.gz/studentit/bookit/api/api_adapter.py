import logging
import re
import time

import requests

from studentit.bookit.api.exceptions import BookItLoginFailedError


class ApiAdapter(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.logger = logging.getLogger(__name__)

        self._logged_in = False

        self._session = requests.Session()
        if self.username and self.password:
            self._do_login()

    def _do_login(self):
        login_string = f'<Login><username>{self.username}</username><password>{self.password}</password>' \
                       f'<rememberMe>false</rememberMe><rememberView>-</rememberView></Login>'
        login_res = self.post(endpoint='cire/login.aspx', data=login_string)
        assert login_res.status_code == 200

        match = re.search("\'http://bookit.unimelb.edu.au/(.*)\'", login_res.text)
        if not match:
            raise BookItLoginFailedError(username=self.username)
        verify_url = match.group(1)
        verify_res = self.get(endpoint=verify_url)
        assert verify_res.status_code == 200

        self._logged_in = True

    def post(self, endpoint, *args, **kwargs):
        return self._request(method=self._session.post, endpoint=endpoint, *args, **kwargs)

    def get(self, endpoint, *args, **kwargs):
        res = self._request(method=self._session.get, endpoint=endpoint, *args, **kwargs)
        wait = 0.25
        cur_try = 0
        max_tries = 5
        while 'exception' in res.text.lower() and cur_try < max_tries:
            cur_try += 1
            self.logger.error(
                'Exception in API call to {endpoint}. Retrying [{cur_try}/{max_tries}]'.format(endpoint=endpoint,
                                                                                               cur_try=cur_try,
                                                                                               max_tries=max_tries))
            time.sleep(wait * cur_try)
            res = self._request(method=self._session.get, endpoint=endpoint, *args, **kwargs)
        return res

    def _request(self, endpoint, method, *args, **kwargs):
        res = method(self._get_url(endpoint), *args, **kwargs)

        if self._logged_in and "location.href = 'http://834S-MYPC/cire/login.aspx'" in res.text:
            self._logged_in = False
            self.logger.error('Session expired. Reauthenticating...')
            self._do_login()
            res = method(self._get_url(endpoint), *args, **kwargs)

        return res

    def _get_url(self, endpoint):
        return 'https://bookit.unimelb.edu.au/{}'.format(endpoint)
