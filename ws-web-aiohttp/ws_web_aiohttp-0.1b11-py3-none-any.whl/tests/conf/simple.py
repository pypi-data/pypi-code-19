import os
import modconf
import ssl

from ws_web_aiohttp.tests.conf.log import *
from ws_web_aiohttp.tests.conf.web import *

google_oauth2 = modconf.import_conf('google_oauth2', os.path.join(os.environ['HOME'], 'config'))

PG = modconf.import_conf('postgresql', os.path.join(os.environ['HOME'], 'config'))

ws_sheets_server = modconf.import_conf('ws_sheets_server.tests.conf.simple')



