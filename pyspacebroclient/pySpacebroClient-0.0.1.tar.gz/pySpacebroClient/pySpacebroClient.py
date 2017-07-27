from socketIO_client import SocketIO, LoggingNamespace,SocketIONamespace, TRANSPORTS


class SpacebroClient(SocketIO):
  def __init__(
      self,
      spacebro_settings={
          'host': 'spacebro.space',
          'port': 3333,
          'channelName': 'spacebro',
          'client': {
              'name': 'pySpacebroClient'
          }
      },
      Namespace=SocketIONamespace,
      wait_for_connection=True, transports=TRANSPORTS,
      resource='socket.io', hurry_interval_in_seconds=1, **kw):
    if spacebro_settings['verbose'] == True:
      Namespace=LoggingNamespace
      import logging
      logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
      logging.basicConfig()
    self.settings = spacebro_settings
    super(SpacebroClient, self).__init__(
        spacebro_settings['host'], spacebro_settings['port'], Namespace, wait_for_connection, transports,
        resource, hurry_interval_in_seconds, **kw)
    super(SpacebroClient, self).on('connect', self.register)
    super(SpacebroClient, self).on('reconnect', self.register)

  def register(self):
    print('socketio connect')
    self.emit('register', {
        'client': self.settings['client'],
        'channelName': self.settings['channelName']
    })
    if ('connection' in self.settings):
        self.emit('addConnections', self.settings['connection'])

  def emit(self, event, *args, **kw):
    if (len(args) == 1):
      args = args[0]
      if (type(args) is not dict):
          args = {
            'data': args,
            'altered': True
          }
      args['_from'] = self.settings['client']['name']
      args['_to'] = None
    super(SpacebroClient, self).emit(event, args, kw)

  def on(self, event, callback):
    if event == 'connect':
      print('WARN: `connect` event doesn\'t do anything, use `newClient`')
    else:
      super(SpacebroClient, self).on(event, callback)

