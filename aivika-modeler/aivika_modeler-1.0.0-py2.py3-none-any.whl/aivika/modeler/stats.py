# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.model import *
from simulation.aivika.modeler.expr import *

INT_SAMPLING_STATS = ['SamplingStats', 'Int']

INT_TIMING_STATS = ['TimingStats', 'Int']

DOUBLE_SAMPLING_STATS = ['SamplingStats', 'Double']

DOUBLE_TIMING_STATS = ['TimingStats', 'Double']

EMPTY_SAMPLING_STATS = 'emptySamplingStats'

EMPTY_TIMING_STATS = 'emptyTimingStats'

def add_sampling_stats(value_expr, stats_expr):
    """Return an expression that adds the value to the specified observation based statistics."""
    v = value_expr
    s = stats_expr
    expect_expr(v)
    expect_expr(s)
    model = v.get_model()
    if model.get_main_model() != s.get_model().get_main_model():
        raise InvalidExprException('Expected the both expressions to belong to the same model')
    code = '(\\a -> do { v <- '
    code += v.read('a')
    code += '; stats <- '
    code += s.read('a')
    code += '; return $ addSamplingStats v stats })'
    return Expr(model, code)

def add_timing_stats(value_expr, stats_expr):
    """Return an expression that adds the value to the specified time-persistent statistics."""
    v = value_expr
    s = stats_expr
    expect_expr(v)
    expect_expr(s)
    model = v.get_model()
    if model.get_main_model() != s.get_model().get_main_model():
        raise InvalidExprException('Expected the both expressions to belong to the same model')
    code = '(\\a -> do { t <- liftDynamics time; v <- '
    code += v.read('a')
    code += '; stats <- '
    code += s.read('a')
    code += '; return $ addTimingStats t v stats })'
    return Expr(model, code)
