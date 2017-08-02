#!/usr/bin/env python
# encoding: utf-8

from flask import render_template
from Recopytex import recopytex

@recopytex.route("/")
def tribes():
    return render_template('index.html')


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
