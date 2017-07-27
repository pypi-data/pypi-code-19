import urlparse

defaultUrl = 'https://api.teknik.io/v1/'
defaultUsername = ''
defaultToken = ''

def GetAPIUrl(url, service):
  finalUrl = ''
  
  if url is None or url == '':
    url = defaultUrl

  server = service.lower()
  if service == 'upload':
    finalUrl = urlparse.urljoin(url, 'Upload')
  elif service == 'paste':
    finalUrl = urlparse.urljoin(url, 'Paste')
  
  return finalUrl