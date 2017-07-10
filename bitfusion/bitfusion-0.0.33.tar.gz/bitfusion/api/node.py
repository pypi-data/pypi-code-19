import os

from bitfusion.api.base import BaseMixin, UpdateableMixin, DeleteableMixin, HealthMixin

def NodeFactory(api_session, Gpu):
  ###########################################
  # BEGIN Node Class
  ###########################################
  class Node(BaseMixin, UpdateableMixin, DeleteableMixin, HealthMixin):
    api = api_session
    base_url = '/api/node'

    def __str__(self):
      output = '\nNode {id} @ {ip} - {mem} MB Memory - {type}\n'

      output = output.format(id=self.data.get('id'),
                             ip=self.data.get('ip_address'),
                             mem=self.data.get('memory'),
                             type=self.data.get('type', '').upper())

      for g in self.data.get('gpus', []):
        gpu = Gpu(**g)
        output += '  ' + str(gpu) + '\n'

      return output


    def activate(self):
      self.load(self.api.post(os.path.join(self.base_url, str(self.id), 'activate')))


    def deactivate(self):
      self.load(self.api.post(os.path.join(self.base_url, str(self.id), 'deactivate')))


    @classmethod
    def add_by_ip(cls, ip):
      return cls.api.post(os.path.join(cls.base_url, 'add', ip))
  ###########################################
  # END Node Class
  ###########################################

  return Node
