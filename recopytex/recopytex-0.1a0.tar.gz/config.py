#!/usr/bin/env python
# encoding: utf-8

import os
basedir = os.path.abspath(os.path.dirname(__file__))


SQLALCHEMY_DATABASE_NAME = 'sqlalch_data.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, SQLALCHEMY_DATABASE_NAME)
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
