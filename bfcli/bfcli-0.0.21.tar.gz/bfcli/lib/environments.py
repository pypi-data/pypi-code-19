from bfcli.lib.api import API

WS_TYPES = ['tensorflow']

if API:
  try:
    _images = API.Workspace.images()
    WS_TYPES = [_i['type'] for _i in _images]
  except:
    pass
