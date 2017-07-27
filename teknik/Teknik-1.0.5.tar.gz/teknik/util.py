from urllib.parse import urljoin

defaultUrl = 'https://api.teknik.io/v1/'
defaultUsername = ''
defaultToken = ''

def GetUrl(url, service):
  finalUrl = ''
  
  if url is None or url == '':
    url = defaultUrl

  server = service.lower()
  if service == 'upload':
    finalUrl = urljoin(url, 'Upload')
  elif service == 'paste':
    finalUrl = urljoin(url, 'Paste')
  
  return finalUrl