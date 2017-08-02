#!/usr/bin/env python
# encoding: utf-8

from Recopytex import recopytex

from Recopytex import api
api.init_app(recopytex)
recopytex.config['BUNDLE_ERRORS'] = True


recopytex.run(host="localhost", debug=True)

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
