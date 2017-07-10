import datetime
import os

from dateutil import parser as dt_parser

from bitfusion.api.base import BaseMixin, CreatableMixin, DeleteableMixin
from bitfusion.lib import time

def get_resource_string(resources):
  def _serialize(res):
    device = res.get('type', '')
    device_label = res.get('deviceType')

    device_str = device_label + '_' + device if device_label else device
    device_str += '=' + str(res.get('value'))

    return device_str

  if not resources:
    return ''

  transformed_r_array = [_serialize(_r) for _r in resources]
  return ','.join(transformed_r_array)


def JobFactory(api_session):
  ###########################################
  # BEGIN Job Class
  ###########################################
  class Job(BaseMixin, CreatableMixin, DeleteableMixin):
    api = api_session
    base_url = '/api/jobs'

    def __str__(self):
      output = 'Job {id} - ' + self.get_state_string()
      output = output.format(id=self.data.get('id'))
      return output


    def get_state_string(self):
      if self.data.get('stoppedAt'):
        stopped_time = time.str_start_to_str_runtime(self.data.get('stoppedAt'))
        return 'Stopped {stopped} ago'.format(stopped=stopped_time)
      elif self.data.get('startedAt'):
        runtime = time.str_start_to_str_runtime(self.data.get('startedAt'))
        return 'Started {runtime} ago'.format(runtime=runtime)
      elif self.data.get('createdAt'):
        created_time = time.str_start_to_str_runtime(self.data.get('createdAt'))
        return 'Created {created} ago'.format(created=created_time)


    def logs(self):
      return self.api.get(os.path.join(self.base_url, self.id, 'logs'))


    def get_table_row(self):
      resource_str = get_resource_string(self.data.get('resources'))
      durstr = time.get_duration_string(self.data.get('startedAt'), self.data.get('stoppedAt'))

      return [
        self.data.get('id'),
        self.data.get('project', {}).get('name'),
        time.str_start_to_str_runtime(self.data.get('createdAt')) + ' ago',
        self.data.get('status'),
        durstr,
        resource_str
      ]


    @staticmethod
    def get_table_headers():
      return ['ID', 'Project', 'Created', 'Status', 'Duration', 'Resources']


    @classmethod
    def create(cls, project, code_id, group, env, data_ids, resources, command):
      if isinstance(command, str):
        command = command.split(' ')
      elif not isinstance(command, list):
        raise Exception('command must be a string or a list')

      payload = {
        'groupId': group,
        'project': project,
        'cmd': command,
        'runEnv': env,
        'codeset': code_id,
        'dataset': data_ids,
        'resources': resources,
      }

      return super(Job, cls).create(**payload)
  ###########################################
  # END Job Class
  ###########################################

  return Job
