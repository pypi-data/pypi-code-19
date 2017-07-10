import sys
import os

import requests

from bitfusion import errors

class ApiSession(requests.Session):
  def __init__(self, host_url, auth_handler, timeout, *args, **kwargs):
    super(ApiSession, self).__init__(*args, **kwargs)

    self.host = host_url
    self.auth = auth_handler
    self.timeout = timeout


  def set_cookies(self, cookies):
    self.cookies = requests.cookies.cookiejar_from_dict(cookies)


  def get_cookies(self):
    return self.cookies.get_dict()


  def get(self, suffix):
    res = super(ApiSession, self).get(self._build_url(suffix),
                                      timeout=self.timeout)
    return self._handle_response(res)


  def post(self, suffix, data=None):
    res = super(ApiSession, self).post(self._build_url(suffix),
                                       json=data,
                                       timeout=self.timeout)
    return self._handle_response(res)


  def put(self, suffix, data=None):
    res = super(ApiSession, self).put(self._build_url(suffix),
                                      json=data,
                                      timeout=self.timeout)
    return self._handle_response(res)


  def delete(self, suffix):
    res = super(ApiSession, self).delete(self._build_url(suffix),
                                         timeout=self.timeout)
    return self._handle_response(res)


  def _build_url(self, suffix):
    path = self.host + os.path.join(suffix)
    return path


  def _check_license_error(self, res):
    if not res.headers.get('Bitfusion-License-Error'):
      return

    try:
      data = res.json()
      print('Please go to {} in your browser to activate the Bitfusion Flex Platform'
            .format(data['redirectUrl']))
      sys.exit(1)
    except:
      raise Exception('Failed to parse license error response: {}'.format(res.text))


  def _handle_response(self, res):
    if res.status_code >= 400:
      self._handle_request_error(res)

    try:
      return res.json()
    except ValueError:
      return res.text


  def _handle_request_error(self, res):
    if res.status_code >= 500:
      raise errors.PlatformError(res.text)
    elif res.status_code == 401:
      raise errors.AuthError(res.text)
    elif res.status_code == 403:
      self._check_license_error(res)
      raise errors.PermissionError(res.text)
    elif res.status_code == 404:
      raise errors.NotFoundError(res.text)
    elif res.status_code >= 400:
      raise errors.ClientError(res.text)
    else:
      raise Exception('Unknown error occured. Status: {} Response: {}' \
                      .format(res.status_code, res.text))
