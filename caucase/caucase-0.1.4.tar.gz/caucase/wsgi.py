# This file is part of caucase
# Copyright (C) 2017  Nexedi
#     Alain Takoudjou <alain.takoudjou@nexedi.com>
#     Vincent Pelletier <vincent@nexedi.com>
#
# caucase is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caucase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caucase.  If not, see <http://www.gnu.org/licenses/>.


import os
from caucase import app
from caucase.web import parseArguments, configure_flask
from werkzeug.contrib.fixers import ProxyFix

def readConfigFromFile(config_file):
  config_list = []
  with open(config_file) as f:
    for line in f.readlines():
      if not line or line.startswith('#'):
        continue
      line_list = line.strip().split(' ')
      if len(line_list) == 1:
        config_list.append('--%s' % line_list[0].strip())
      elif len(line_list) > 1:
        config_list.append('--%s' % line_list[0].strip())
        config_list.append(' '.join(line_list[1:]))

  return parseArguments(config_list)

def start_wsgi():
  """
    Start entry for wsgi, do not run app.run, read config from file
  """
  if os.environ.has_key('CA_CONFIGURATION_FILE'):
    config_file = os.environ['CA_CONFIGURATION_FILE']
  else:
    config_file = 'ca.conf'

  configure_flask(readConfigFromFile(config_file))

  app.wsgi_app = ProxyFix(app.wsgi_app)
  
  app.logger.info("Certificate Authority server ready...")

if __name__ == 'caucase.wsgi':
  start_wsgi()
