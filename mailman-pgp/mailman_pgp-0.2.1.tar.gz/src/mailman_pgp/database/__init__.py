# Copyright (C) 2017 Jan Jancar
#
# This file is a part of the Mailman PGP plugin.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""Common database functions and class."""
import logging
from contextlib import contextmanager

from mailman.database.transaction import transaction as mailman_transaction
from public import public
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from mailman_pgp.config import config
from mailman_pgp.model.base import Base

log = logging.getLogger('mailman.plugin.pgp.database')


@public
class Database:
    """A SQLAlchemy database."""

    def __init__(self):
        self._url = config.get_value('db', 'url')
        log.debug('Creating database at {}'.format(self._url))
        self.engine = create_engine(self._url)
        self.scoped_session = scoped_session(sessionmaker(bind=self.engine))
        Base.metadata.create_all(self.engine)
        self.session.commit()
        log.debug('Database successfully created.')

    @property
    def session(self):
        """
        Get a scoped_session.

        :return: A scoped session.
        :rtype: scoped_session
        """
        return self.scoped_session()


@public
@contextmanager
def transaction():
    """
    A transaction context manager.

    :return: A session for convenience.
    :rtype: scoped_session
    """
    try:
        yield config.db.session
    except:
        config.db.session.rollback()
        raise
    else:
        config.db.session.commit()


@public
def query(cls):
    """
    A query helper.

    :param cls: Class to query.
    :return: A query on the class.
    :rtype: sqlalchemy.orm.query.Query
    """
    return config.db.session.query(cls)


mm_transaction = mailman_transaction
public(mm_transaction=mm_transaction)
