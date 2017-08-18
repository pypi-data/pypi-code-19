#!/usr/bin/env python
# encoding: utf-8

from flask_restplus import Api

from .tribes import api as tribes_nsp
from .evals import api as evals_nsp
from .students import api as students_nsp
from .exercises import api as exercises_nsp
from .questions import api as questions_nsp
from .scores import api as scores_nsp

api = Api(
        title="Apis warpup"
        )

api.add_namespace(tribes_nsp, path="/api/tribes")
api.add_namespace(evals_nsp, path="/api/evals")
api.add_namespace(students_nsp, path="/api/students")
api.add_namespace(exercises_nsp, path="/api/exercises")
api.add_namespace(questions_nsp, path="/api/questions")
api.add_namespace(scores_nsp, path="/api/scores")

__all__ = ["api"]

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
