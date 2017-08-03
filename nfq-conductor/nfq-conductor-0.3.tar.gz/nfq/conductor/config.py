# NFQ Logwrapper. A tool for centralizing and visualizing logs.
# Copyright (C) 2017 Guillem Borrell Nogueras
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tornado.options import define, options
from tornado import template
import os


# Parse all options at import time.
define("port", default=8888, help="Port for the web an websockets service")
define("collector",
       default="tcp://127.0.0.1:5555",
       help="TCP address of the collector socket")
define("dbengine",
       default="sqlite:///:memory:",
       help="SQLAlchemy connection string. Defaults to a volatile sqlite DB.")
define("dbdebug",
       default=False,
       help="Set to True to see SQLAlchemy logs")
define("config",
       default=None,
       help="Server config file")

options.parse_command_line()

if options.config:
    options.parse_config_file(options.config)

root_path = os.path.abspath(os.path.join(os.path.realpath(__file__), os.path.pardir))
loader = template.Loader(os.path.join(root_path, 'templates'))
