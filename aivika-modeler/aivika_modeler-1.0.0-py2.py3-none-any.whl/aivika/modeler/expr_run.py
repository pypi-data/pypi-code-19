# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.data_type import *
from simulation.aivika.modeler.stream import *

def run_expr_in_start_time(expr):
    """Run the specified expression in start time for performing some side effect."""
    e = expr
    expect_expr(e)
    code = 'runEventInStartTime $ '
    code += e.read('()')
    model = e.get_model()
    model.add_action(code)

def run_expr_in_stop_time(expr):
    """Run the specified expression in stop time for performing some side effect."""
    e = expr
    expect_expr(e)
    code = 'runEventInStartTime $ enqueueEventWithStopTime $ '
    code += e.read('()')
    model = e.get_model()
    model.add_action(code)

def enqueue_expr(time, expr):
    """Run the expression at the specified time for performing some side effect."""
    t = time
    e = expr
    expect_expr(e)
    code = 'runEventInStartTime $ enqueueEvent '
    code += str(time)
    code += ' $ '
    code += e.read('()')
    model = e.get_model()
    model.add_action(code)
