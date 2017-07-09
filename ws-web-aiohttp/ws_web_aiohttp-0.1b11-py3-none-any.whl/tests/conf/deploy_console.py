import ssl

from ws_web_aiohttp.tests.conf.simple import *

LOGGING['loggers']['__main__']['handlers'] = ['console']
LOGGING['loggers']['ws_sheets_server']['handlers'] = ['console']
LOGGING['loggers']['ws_web_aiohttp']['handlers'] = ['console']
       
SSL_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
SSL_CONTEXT.load_cert_chain(certfile, keyfile)

SCHEME = 'https'
SCHEME_WS = 'wss'

PORT = 443



