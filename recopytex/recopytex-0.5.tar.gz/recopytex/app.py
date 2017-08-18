#!/usr/bin/env python
# encoding: utf-8

__all__ = ["recopytex"]

import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


recopytex = Flask(__name__)
#recopytex.config.from_object('config')
basedir = os.path.abspath(os.path.dirname("./"))

recopytex.config.update(dict(
    SQLALCHEMY_DATABASE_NAME = 'recopytex.db',
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,  'recopytex.db'),
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///sqlalch_data.db',
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ))
db = SQLAlchemy(recopytex)

# https://stackoverflow.com/questions/22181384/javascript-no-access-control-allow-origin-header-is-present-on-the-requested
@recopytex.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@recopytex.route("/")
def tribes():
    return render_template('index.html')

from .apis import api
from recopytex import models
api.init_app(recopytex)
db.create_all()

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
