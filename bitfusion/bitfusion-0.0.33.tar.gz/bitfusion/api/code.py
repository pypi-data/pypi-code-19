import os

from bitfusion.api.data import Data
from bitfusion.lib import files

class Code(object):
  base_url = '/api/projects/{pid}/code'

  def __init__(self, api_session, project_id):
    self.api = api_session
    self.base_url = self.base_url.format(pid=project_id)


  def _get_signed_url(self, filename, path, group_id, account_id):
    payload = {
      'fileName': filename,
      'path': path,
      'groupId': group_id,
      'accountId': account_id
    }

    res = self.api.post(self.base_url, payload)
    return res['location'], res['id']


  def upload_complete_notification(self, code_id):
    self.api.put(os.path.join(Data.base_url, code_id, 'status/uploaded'))


  def upload(self, src_path, dst_path, group_id, account_id, callback=None):
    tar_name = files.create_tar(src_path)

    try:
      url, code_id = self._get_signed_url(tar_name, dst_path, group_id, account_id)
      files.upload_to_s3(url, tar_name, callback)
    finally:
      os.remove(tar_name)

    self.upload_complete_notification(code_id)
    return code_id
