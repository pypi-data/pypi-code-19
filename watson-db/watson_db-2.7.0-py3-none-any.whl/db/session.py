# -*- coding: utf-8 -*-
from sqlalchemy import orm

NAME = 'sqlalchemy_session_{}'


def make_session(**kwargs):
    return orm.scoped_session(orm.sessionmaker(**kwargs))
