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
from caucase import app, db
from flask_alchemydumps import AlchemyDumps, AlchemyDumpsCommand
from flask_script  import Manager, Command


app.config.update(
  DEBUG=False,
  CSRF_ENABLED=True,
  TESTING=False,
  SQLALCHEMY_DATABASE_URI='sqlite:///%sca.db' % os.environ.get('CAUCASE_DIR', '')
)

manager = Manager(app)

# init Alchemy Dumps
alchemydumps = AlchemyDumps(app, db)
manager.add_command('database', AlchemyDumpsCommand)

@manager.command
def housekeep():
  """
    Start Storage housekeep method to cleanup garbages
  """
  from caucase.storage import Storage
  storage = Storage(db)
  storage.housekeep()

def main():
  manager.run()
