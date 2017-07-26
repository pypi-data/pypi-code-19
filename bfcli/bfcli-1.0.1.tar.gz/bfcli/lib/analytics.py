import analytics

def set_key(key):
  analytics.write_key = key

def init_user(user_email, token):
  try:
    analytics.identify(user_email, {
      'name': data['profile']['name'],
      'email': data['profile']['email'],
      'accountId': token.get('account')
    })

    analytics.group(user_email, token.get('licenseInfo', {}).get('accountId'), {
      'licenseName': token.get('licenseInfo', {}).get('name'),
      'licenseEmail': token.get('licenseInfo', {}).get('email'),
      'licenseOrg': token.get('licenseInfo', {}).get('org'),
      'licenseAccountId': token.get('licenseInfo', {}).get('accountId'),
      'licenseNotBefore': token.get('licenseInfo', {}).get('validity', {}).get('notBefore'),
      'licenseNotAfter': token.get('licenseInfo', {}).get('validity', {}).get('notAfter')
    })

    analytics.track(user_email, 'CURRENT_USER_LOGIN_SUCCESS', {'ui': 'cli'})
  except:
    pass

def track(event, payload):
  from bfcli.lib.api import me
  user = me()

  try:
    analytics.track(user.data['user']['email'], event, payload)
  except:
    pass
