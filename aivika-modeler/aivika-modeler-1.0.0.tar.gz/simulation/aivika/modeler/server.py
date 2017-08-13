# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.model import *
from simulation.aivika.modeler.port import *
from simulation.aivika.modeler.stream import *
from simulation.aivika.modeler.data_type import *

def server_stream(server_port, stream_port):
    """Return a new stream after processing the input stream by the specified server."""
    s1 = server_port
    s2 = stream_port
    expect_server(s1)
    expect_stream(s2)
    expect_same_model([s1, s2])
    if encode_data_type(s1.get_input_data_type()) != encode_data_type(s2.get_item_data_type()):
        raise InvalidPortException('Expected the input of server ' + s1.get_name() + ' and the item type of stream ' + s2.get_name() + ' to be the same')
    model = s1.get_model()
    code = 'return $ runProcessor (serverProcessor ' + s1.read() + ') ' + s2.read()
    y = StreamPort(model, s1.get_output_data_type())
    y.bind_to_input()
    y.write(code)
    s2.bind_to_output()
    return y

def hold_server(transact_type, expr, preemptible = False, name = None, descr = None):
    """Create a server that holds the process for the time interval specified by the expression when processing each transact from the input stream."""
    tp = transact_type
    e = expr
    expect_transact_type(tp)
    expect_expr(e)
    expect_same_model([tp, e])
    model = tp.get_model()
    code = 'newPreemptibleServer ' + str(preemptible) + ' $ \\a -> '
    code += 'do { dt <- liftEvent $ ' + e.read('a') + '; holdProcess dt; return a }'
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def reset_server(server_port, reset_time):
    """Reset the server statistics at the specified modeling time."""
    s = server_port
    expect_server(s)
    model = s.get_model()
    code = 'runEventInStartTime $ enqueueEvent ' + str(reset_time)
    code += ' $ resetServer ' + s.read()
    model.add_action(code)
