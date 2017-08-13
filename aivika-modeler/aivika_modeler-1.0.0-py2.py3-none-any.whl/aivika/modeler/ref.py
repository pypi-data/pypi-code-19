# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.model import *
from simulation.aivika.modeler.port import *
from simulation.aivika.modeler.queue_strategy import *
from simulation.aivika.modeler.expr import *
from simulation.aivika.modeler.data_type import *

def create_ref(model, init_value, item_data_type, name, descr = None):
    """Return a new reference by the specified model, initial value, item data type, name and optional description."""
    base_comp = model.get_base_comp()
    y = RefPort(model, item_data_type, name = name, descr = descr)
    comp_type = []
    comp_type.append('Simulation')
    if not (base_comp is None):
        comp_type.append(base_comp)
    comp_type.append(y.get_data_type())
    code = 'newRef (' + str(init_value) + ') :: ' + encode_data_type(comp_type)
    y.write(code)
    return y

def read_ref(ref_port):
    """Return an expression that evaluates to the specified reference contents."""
    r = ref_port
    expect_ref(r)
    model = r.get_model()
    code = '(\\a -> readRef ' + r.read() + ')'
    return Expr(model, code)

def write_ref(ref_port, expr):
    """Return an expression that writes a new refernce value by the provided expression."""
    r = ref_port
    e = expr
    expect_ref(r)
    expect_expr(e)
    if r.get_model().get_main_model() != e.get_model().get_main_model():
        raise InvalidPortException('Expected both the reference ' + r.get_name() + ' and the expression to belong to the same model')
    model = r.get_model()
    code = '(\\a -> ' + e.read('a') + ' >>= writeRef ' + r.read() + ')'
    return Expr(model, code)

def inc_ref(ref_port, increment_expr = 1):
    """Return an expression that increases the reference contents."""
    r = ref_port
    n = increment_expr
    expect_ref(r)
    model = r.get_model()
    return write_ref(r, binary_expr(read_ref(r), '+', n))

def dec_ref(ref_port, decrement_expr = 1):
    """Return an expression that decreases the reference contents."""
    r = ref_port
    n = decrement_expr
    expect_ref(r)
    model = r.get_model()
    return write_ref(r, binary_expr(read_ref(r), '-', n))
