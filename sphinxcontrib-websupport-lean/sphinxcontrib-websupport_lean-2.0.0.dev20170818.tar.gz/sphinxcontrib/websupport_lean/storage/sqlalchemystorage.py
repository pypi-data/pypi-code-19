# -*- coding: utf-8 -*-
"""
    sphinxcontrib.websupport.storage.sqlalchemystorage
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An SQLAlchemy storage backend.

    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import sqlalchemy
from sphinxcontrib.websupport_lean.storage import StorageBackend
from sphinxcontrib.websupport_lean.storage.sqlalchemy_db import Base, Node, \
    Session

if sqlalchemy.__version__[:3] < '0.5':  # type: ignore
    raise ImportError('SQLAlchemy version 0.5 or greater is required for this '
                      'storage backend; you have version %s' % sqlalchemy.__version__)


class SQLAlchemyStorage(StorageBackend):
    """
    A :class:`.StorageBackend` using SQLAlchemy.
    """

    def __init__(self, uri):
        self.engine = sqlalchemy.create_engine(uri)
        Base.metadata.bind = self.engine
        Base.metadata.create_all()
        Session.configure(bind=self.engine)

    def pre_build(self):
        self.build_session = Session()

    def has_node(self, id):
        session = Session()
        node = session.query(Node).filter(Node.id == id).first()
        session.close()
        return bool(node)

    def add_node(self, id, document, source):
        node = Node(id, document, source)
        self.build_session.add(node)
        self.build_session.flush()

    def post_build(self):
        self.build_session.commit()
        self.build_session.close()
