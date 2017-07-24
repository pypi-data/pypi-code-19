from bitfusion.api.base import BaseMixin, CreatableMixin, UpdateableMixin, DeleteableMixin

def VolumeFactory(api_session):
  class Volume(BaseMixin, CreatableMixin, UpdateableMixin, DeleteableMixin):
  ###########################################
  # BEGIN Volume Class
  ###########################################
    api = api_session
    base_url = '/api/volume'

    def __str__(self):
      output = '\nVolume {id} - {name}\nHost: {host_path}\nContainer: {container_path}'
      output = output.format(id=self.data.get('id'),
                             name=self.data.get('name'),
                             host_path=self.data.get('host_path'),
                             container_path=self.data.get('container_path'))

      return output + '\n'
  ###########################################
  # END Volume Class
  ###########################################

  return Volume
