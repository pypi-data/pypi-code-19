import os

from bitfusion.lib import files, time

class Data(object):
  base_url = '/api/data'

  def __init__(self, api_session):
    self.api = api_session


  def _get_signed_url(self, filename, path, group_id, account_id):
    payload = {
      'fileName': filename,
      'path': path,
      'groupId': group_id,
      'accountId': account_id
    }

    res = self.api.post(self.base_url, payload)
    return res['location'], res['id']


  def upload_complete_notification(self, data_id):
    self.api.put(os.path.join(self.base_url, data_id, 'status/uploaded'))


  def upload(self, src_path, dst_path, group_id=None, account_id=None, callback=None):
    tar_name = files.create_tar(src_path)

    try:
      url, data_id = self._get_signed_url(tar_name, dst_path, group_id, account_id)
      files.upload_to_s3(url, tar_name, callback)
    finally:
      os.remove(tar_name)

    self.upload_complete_notification(data_id)
    return data_id


  def get(self, data_id):
    return self.api.get(os.path.join(self.base_url, data_id))


  def list(self):
    return self.api.get(self.base_url)


  def delete(self, data_id):
    return self.api.delete(os.path.join(self.base_url, data_id))


  @classmethod
  def get_table(cls, data_list):
    table = [cls.get_table_headers()]

    for _d in data_list:
      table.append([_d.get('id'), _d.get('name'), time.pretty_date(_d.get('createdAt'))])

    return table


  @staticmethod
  def get_table_headers():
    return ['ID', 'Name', 'Created']
