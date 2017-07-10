import os

from bitfusion.api.base import BaseMixin, CreatableMixin, UpdateableMixin, DeleteableMixin, HealthMixin
from bitfusion.lib import time

def WorkspaceFactory(api_session, host, Gpu):
  ###########################################
  # BEGIN Workspace Class
  ###########################################
  class Workspace(BaseMixin, CreatableMixin, UpdateableMixin, DeleteableMixin, HealthMixin):
    api = api_session
    base_url = '/api/workspace'

    def __str__(self):
      output = '\nWorkspace {id} - {name} - {type} - Using {resources}\n' + \
               '  Status {state} - Created {running} ago\n'

      running = time.str_start_to_str_runtime(self.data['start_date'])

      if self.data.get('gpus'):
        if type(self.data.get('gpus')) == int:
          gpu_count = float(self.data.get('gpus'))/1000
          resources = '{0:0.1f} gpu'.format(gpu_count)
          if gpu_count > 1:
            resources += 's'
        elif type(self.data.get('gpus')) == list:
          gpu_count = len(self.data.get('gpus'))
          resources = '{} gpu'.format(gpu_count)
          if gpu_count > 1:
            resources += 's'
      else:
        resources = 'cpu'


      output = output.format(id=self.data.get('id'),
                             name=self.data.get('name', '(unnamed)'),
                             type=self.data.get('type'),
                             resources=resources,
                             state=self.data.get('state_message'),
                             running=running)

      if self.data.get('state') == 0:
        output += '  Web URL: {}\n'.format(host + self.data.get('url', ''))

      return output


    @classmethod
    def image_metadata(cls, image_type):
      images = cls.api.get(os.path.join(cls.base_url, 'type'))

      for _i in images:
        if _i['type'] == image_type:
          return _i

      return None


    @classmethod
    def images(cls):
      return cls.api.get(os.path.join(cls.base_url, 'type'))


    @classmethod
    def create(cls, ws_type, group, name=None, node_id=None, gpus=None, options=None):
      payload = {
        'type': ws_type,
        'group': group,
        'name': name,
        'gpus': gpus,
        'options': options
      }

      # We are in advanced mode
      if node_id:
        payload['node_id'] = node_id

      return super(Workspace, cls).create(**payload)


    def save(self, tag):
      payload = {
        'tag': tag
      }
      return self.api.post(os.path.join(self.base_url, str(self.id), 'save'), payload)
  ###########################################
  # END Workspace Class
  ###########################################

  return Workspace
