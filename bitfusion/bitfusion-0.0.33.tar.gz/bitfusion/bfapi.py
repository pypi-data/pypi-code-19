import os

import requests

from bitfusion import api
from bitfusion.lib.session import ApiSession

class BFApi():
  def __init__(self, host='http://localhost', api_base_url=None,
               auth=None, timeout=5, cookies=None, username=None,
               password=None, verify=True):

    self._session = ApiSession(host, auth, timeout)
    self._session.verify = verify

    # Set the API data controllers
    self.data = api.Data(self._session)
    self.Gpu = api.GpuFactory(self._session)
    self.Node = api.NodeFactory(self._session, self.Gpu)
    self.Volume = api.VolumeFactory(self._session)
    self.Workspace = api.WorkspaceFactory(self._session, host, self.Gpu)
    self.Resource = api.ResourceFactory(self._session)
    self.User = api.UserFactory(self._session)
    self.Job = api.JobFactory(self._session)
    self.Project = api.ProjectFactory(self._session, self.Job)

    if api_base_url:
      self.set_api_base_url(api_base_url)

    if cookies:
      self.set_cookies(cookies)
    elif username and password:
      self.login(username, password)


  def login(self, username, password):
    payload = {
      'email': username,
      'password': password
    }

    self._session.cookies.clear()

    data = self._session.post('/auth/login', payload)
    return data


  def is_paas_enabled(self):
    try:
      data = self._session.get('/config/public/manager.json')
      if data.get('paas_enabled') == 'true':
        return True
    except:
      pass

    return False


  def get_segment_write_key(self):
    try:
      data = self._session.get('/config/public/manager.json')
      return data.get('segment', {}).get('write_key')
    except:
      return None


  def set_cookies(self, cookies):
    self._session.set_cookies(cookies)
    return self._session.get_cookies()


  def get_cookies(self):
    return self._session.get_cookies()


  def set_api_base_url(self, base_path):
    self.Node.base_url = os.path.join(base_path, 'node')
    self.Volume.base_url = os.path.join(base_path, 'volume')
    self.Workspace.base_url = os.path.join(base_path, 'workspace')
    self.Resource.base_url = os.path.join(base_path, 'resource')
    self.User.base_url = os.path.join(base_path, 'users')
    self.data.base_url =  os.path.join(base_path, 'data')
    self.Job.base_url = os.path.join(base_path, 'jobs')
    self.Project.base_url = os.path.join(base_path, 'projects')


  def set_auth(self, auth):
    self._session.auth = auth
