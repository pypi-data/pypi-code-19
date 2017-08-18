#!/usr/bin/env python
# encoding: utf-8

from recopytex.app import recopytex

recopytex.config['BUNDLE_ERRORS'] = True
recopytex.run(host="localhost", debug=True)

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
