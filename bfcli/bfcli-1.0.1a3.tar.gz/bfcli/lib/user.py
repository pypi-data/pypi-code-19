from bfcli.lib.api import API, me

def is_admin():
  try:
    user = me()
    admin = False
    for g in user.data['groups']:
      if g.get('admin'):
        admin = True
  except Exception as e:
    admin = True

  return admin


def show_resources():
  try:
    public_config = API.public_config()
  except:
    public_config = {}
  
  if 'allow_nodes_view_non_admin' in public_config:
    if public_config['allow_nodes_view_non_admin'].lower() == 'true':
      return True
    elif is_admin():
      return True
  else:
    return True

  return False
