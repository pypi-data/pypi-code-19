#!/usr/bin/env python
# encoding: utf-8

from flask_restplus import Api

from .tribes import api as tribes_nsp
from .evals import api as evals_nsp
from .students import api as students_nsp

api = Api(
        title="Apis warpup"
        )

api.add_namespace(tribes_nsp, path="/api/tribes")
api.add_namespace(evals_nsp, path="/api/evals")
api.add_namespace(students_nsp, path="/api/students")

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
