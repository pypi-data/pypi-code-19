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

# Configuration is loaded at import time. Do not touch this
import nfq.logwrapper.config

import logging

from tornado.options import options
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text

engine = create_engine(options.dbengine, echo=options.dbdebug)
session = sessionmaker(bind=engine)()
logging.info('DB connected at {}'.format(options.dbengine))
Base = declarative_base()

# Cache for clients.
clients = []


class LogEntry(Base):
    __tablename__ = 'log_entries'

    id = Column(Integer, primary_key=True)
    source = Column(String)
    when = Column(DateTime)
    message = Column(Text)

    def to_dict(self):
        return {'source': self.source,
                'when': self.when.isoformat(),
                'message': self.message}


