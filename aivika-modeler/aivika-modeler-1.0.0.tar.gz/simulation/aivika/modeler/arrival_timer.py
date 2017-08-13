# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.model import *
from simulation.aivika.modeler.port import *

def create_arrival_timer(model, name, descr = None):
    """Return a new timer that allows measuring the processing time of transacts."""
    y = ArrivalTimerPort(model, name = name, descr = descr)
    code = 'newArrivalTimer'
    y.write(code)
    return y

def arrival_timer_stream(arrival_timer_port, stream_port):
    """Measure the processing time of transacts from the specified stream within the resulting stream."""
    t = arrival_timer_port
    s = stream_port
    expect_arrival_timer(t)
    expect_stream(s)
    expect_same_model([t, s])
    model = t.get_model()
    item_data_type = s.get_item_data_type()
    code = 'return $ runProcessor (arrivalTimerProcessor ' + t.read() + ') ' + s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def reset_arrival_timer(arrival_timer_port, reset_time):
    """Reset the arrival timer statistics at the specified modeling time."""
    t = arrival_timer_port
    expect_arrival_timer(t)
    model = t.get_model()
    code = 'runEventInStartTime $ enqueueEvent ' + str(reset_time)
    code += ' $ resetArrivalTimer ' + t.read()
    model.add_action(code)
