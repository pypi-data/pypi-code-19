from bitfusion.api.base import BaseMixin, CreatableMixin, DeleteableMixin
from bitfusion.api.code import Code
from bitfusion.lib import time

def ProjectFactory(api_session, Job):
  ###########################################
  # BEGIN Project Class
  ###########################################
  class Project(BaseMixin, CreatableMixin, DeleteableMixin):
    api = api_session
    base_url = '/api/projects'

    def __init__(self, **kwargs):
      super(Project, self).__init__(**kwargs)
      self.code = Code(self.api, self.id)

    def __str__(self):
      output = 'Project {name} {id}'
      output = output.format(name=self.data.get('name'),
                             id=self.id)
      return output


    def upload_code(self, path, callback=None):
      return self.code.upload(path,
                              '/',
                              self.data['groupId'],
                              self.data['accountId'],
                              callback=callback)


    def get_table_row(self):
      return [self.data.get('id'),
              self.data.get('name'),
              time.pretty_date(self.data.get('createdAt'))]


    @classmethod
    def create(cls, name):
      payload = {
        'name': name
      }

      return super(Project, cls).create(**payload)


    @staticmethod
    def get_table_headers():
      return ['ID', 'Name', 'Created']
  ###########################################
  # END Project Class
  ###########################################

  return Project
