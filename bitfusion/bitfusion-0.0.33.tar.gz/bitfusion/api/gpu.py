from bitfusion.api.base import BaseMixin

def GpuFactory(api_session):
  ###########################################
  # BEGIN Gpu Class
  ###########################################
  class Gpu(BaseMixin):
    api = api_session
    base_url = '/gpu'

    def __str__(self):
      output = 'GPU {id} - {type} - {mem} MB Memory - {state}'
      output = output.format(id=self.data.get('id'),
                             type=self.data.get('type'),
                             mem=self.data.get('memory', '???'),
                             state=self.data.get('state'))

      return output
  ###########################################
  # END Gpu Class
  ###########################################

  return Gpu
