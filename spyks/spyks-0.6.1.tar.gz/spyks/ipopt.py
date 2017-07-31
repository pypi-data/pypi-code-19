# -*- coding: utf-8 -*-
# -*- mode: python -*-
""" Generates equations.txt and parameters.txt for makecode """

import logging
from spyks.core import n_params, n_state, n_forcing
from spyks.codegen import simplify_equations

log = logging.getLogger('spyks')   # root logger


def discretize(model):
