# -*- coding: utf-8 -*-
"""
    sphinxcontrib.websupport.storage.sqlalchemy_db
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    SQLAlchemy table and mapper definitions used by the
    :class:`sphinxcontrib.websupport.storage.sqlalchemystorage.SQLAlchemyStorage`.

    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from sqlalchemy import Column, Text, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

if False:
    # For type annotation
    from typing import List  # NOQA

Base = declarative_base()
Session = sessionmaker()

db_prefix = 'sphinx_'


class Node(Base):  # type: ignore
    """Data about a Node in a doctree."""
    __tablename__ = db_prefix + 'nodes'

    id = Column(String(32), primary_key=True)
    document = Column(String(256), nullable=False)
    source = Column(Text, nullable=False)

    def __init__(self, id, document, source):
        self.id = id
        self.document = document
        self.source = source
