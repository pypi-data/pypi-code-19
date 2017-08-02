#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

recopytex = Flask(__name__)
recopytex.config.from_object('config')

# https://stackoverflow.com/questions/22181384/javascript-no-access-control-allow-origin-header-is-present-on-the-requested
@recopytex.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

db = SQLAlchemy(recopytex)

from Recopytex.apis import api
from Recopytex import models, views

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
