import json
import os

from bitfusion import errors

class BaseMixin(object):
  def __init__(self, **kwargs):
    self.load(kwargs)


  def load(self, api_data):
    self.id = api_data.get('id')
    self.data = api_data


  def reload(self):
    if not self.id:
      raise Exception('Cannot reload an object that has no ID')

    self.load(self.get_data_by_id(self.id))


  def json(self):
    return json.dumps(self.data)


  @classmethod
  def _not_found_error(cls, data_id):
    msg = 'Could not find {} by ID {}'.format(cls.__name__, data_id)
    raise errors.NotFoundError(msg)


  @classmethod
  def set_base_url(cls, base_url):
    cls.base_url = base_url


  @classmethod
  def get(cls, data_id):
    return cls(**cls.get_data_by_id(data_id))


  @classmethod
  def get_all(cls):
    raw_data = cls.api.get(cls.base_url)
    instance_list = []

    for d in raw_data:
      instance_list.append(cls(**d))

    return instance_list


  @classmethod
  def get_data_by_id(cls, data_id):
    try:
      return cls.api.get(os.path.join(cls.base_url, str(data_id)))
    except errors.NotFoundError as e:
      cls._not_found_error(data_id)


class CreatableMixin(object):
  @classmethod
  def create(cls, **kwargs):
    return cls(**cls.api.post(cls.base_url, kwargs))


class UpdateableMixin(object):
  def update(self, **kwargs):
    if not self.id:
      raise Exception('Cannot update without an ID')

    self.load(self.api.put(os.path.join(self.base_url, str(self.id)), kwargs))


class DeleteableMixin(object):
  def delete(self):
    if not self.id:
      raise Exception('Cannot delete without an ID')

    return self.api.delete(os.path.join(self.base_url, str(self.id)))


class HealthMixin(object):
  def set_health(self, health_status, health_message):
    self.update(state=health_status, health_message=health_message)
