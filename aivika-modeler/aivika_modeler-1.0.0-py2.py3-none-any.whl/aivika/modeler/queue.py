# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.model import *
from simulation.aivika.modeler.port import *
from simulation.aivika.modeler.queue_strategy import *
from simulation.aivika.modeler.expr import *
from simulation.aivika.modeler.data_type import *

def create_unbounded_queue(model, item_data_type, name, descr = None, storing_queue_strategy = 'FCFS', output_queue_strategy = 'FCFS'):
    """Return a new unbounded queue by the specified model, item data type, name and optional description.

       You can also specify the strategies that will be applied when storing and extracting the items
       from the queue.
    """
    expect_queue_strategy(storing_queue_strategy)
    expect_queue_strategy(output_queue_strategy)
    base_comp = model.get_base_comp()
    y = UnboundedQueuePort(model, item_data_type, storing_queue_strategy, output_queue_strategy, name = name, descr = descr)
    comp_type = []
    comp_type.append('Simulation')
    if not (base_comp is None):
        comp_type.append(base_comp)
    comp_type.append(y.get_data_type())
    code = 'IQ.newQueue ' + storing_queue_strategy + ' ' + output_queue_strategy
    code = '(runEventInStartTime $ ' + code + ') :: ' + encode_data_type (comp_type)
    y.write(code)
    return y

def create_queue(model, item_data_type, capacity, name, descr = None, input_queue_strategy = 'FCFS', storing_queue_strategy = 'FCFS', output_queue_strategy = 'FCFS'):
    """Return a new bounded queue by the specified model, item data type, capacity, name and optional description.

       You can also specify the strategies that will be applied when adding, storing and extracting the items
       from the queue.
    """
    expect_queue_strategy(input_queue_strategy)
    expect_queue_strategy(storing_queue_strategy)
    expect_queue_strategy(output_queue_strategy)
    base_comp = model.get_base_comp()
    y = QueuePort(model, item_data_type, capacity, input_queue_strategy, storing_queue_strategy, output_queue_strategy, name = name, descr = descr)
    comp_type = []
    comp_type.append('Simulation')
    if not (base_comp is None):
        comp_type.append(base_comp)
    comp_type.append(y.get_data_type())
    code = 'Q.newQueue ' + input_queue_strategy + ' ' + storing_queue_strategy + ' ' + output_queue_strategy + ' ' + str(capacity)
    code = '(runEventInStartTime $ ' + code + ') :: ' + encode_data_type (comp_type)
    y.write(code)
    return y

def unbounded_enqueue_stream(unbounded_queue_port, stream_port):
    """Add the items from the specified stream to the given unbounded queue."""
    q = unbounded_queue_port
    s = stream_port
    expect_unbounded_queue(q)
    expect_stream(s)
    expect_same_model([q, s])
    model = q.get_model()
    code = 'consumeStream (\\a -> liftEvent $ IQ.enqueue ' + q.read() + ' a) ' + s.read()
    code = 'runProcessInStartTime $ ' + code
    s.bind_to_output()
    model.add_action(code)

def enqueue_stream(queue_port, stream_port):
    """Add the items from the specified stream to the given bounded queue."""
    q = queue_port
    s = stream_port
    expect_queue(q)
    expect_stream(s)
    expect_same_model([q, s])
    model = q.get_model()
    code = 'consumeStream (Q.enqueue ' + q.read() + ') ' + s.read()
    code = 'runProcessInStartTime $ ' + code
    s.bind_to_output()
    model.add_action(code)

def unbounded_dequeue_stream(unbounded_queue_port):
    """Return a stream of items extracted from the unbounded queue."""
    q = unbounded_queue_port
    expect_unbounded_queue(q)
    model = q.get_model()
    item_data_type = q.get_item_data_type()
    code = 'return $ repeatProcess (IQ.dequeue ' + q.read() + ')'
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    return y

def dequeue_stream(queue_port):
    """Return a stream of items extracted from the bounded queue."""
    q = queue_port
    expect_queue(q)
    model = q.get_model()
    item_data_type = q.get_item_data_type()
    code = 'return $ repeatProcess (Q.dequeue ' + q.read() + ')'
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    return y

def unbounded_queue_size(unbounded_queue_port):
    """Return an expression that evaluates to the unbounded queue size."""
    q = unbounded_queue_port
    expect_unbounded_queue(q)
    model = q.get_model()
    code = '(\\a -> liftEvent $ IQ.queueCount ' + q.read() + ')'
    return Expr(model, code)

def enqueue_stream_or_remove_item(queue_port, stream_port):
    """Add the items from the specified stream to the given bounded queue when there is a free capacity; otherwise, remove the items."""
    q = queue_port
    s = stream_port
    expect_queue(q)
    expect_stream(s)
    expect_same_model([q, s])
    model = q.get_model()
    code = 'consumeStream (liftEvent . Q.enqueueOrLost_ ' + q.read() + ') ' + s.read()
    code = 'runProcessInStartTime $ ' + code
    s.bind_to_output()
    model.add_action(code)

def queue_capacity(queue_port):
    """Return an expression that evaluates to the bounded queue capacity."""
    q = queue_port
    expect_queue(q)
    model = q.get_model()
    code = '(\\a -> return $ Q.queueMaxCount ' + q.read() + ')'
    return Expr(model, code)

def queue_size(queue_port):
    """Return an expression that evaluates to the bounded queue size."""
    q = queue_port
    expect_queue(q)
    model = q.get_model()
    code = '(\\a -> liftEvent $ Q.queueCount ' + q.read() + ')'
    return Expr(model, code)

def reset_unbounded_queue(unbounded_queue_port, reset_time):
    """Reset the unbounded queue statistics at the specified modeling time."""
    q = unbounded_queue_port
    expect_unbounded_queue(q)
    model = q.get_model()
    code = 'runEventInStartTime $ enqueueEvent ' + str(reset_time)
    code += ' $ IQ.resetQueue ' + q.read()
    model.add_action(code)

def reset_queue(queue_port, reset_time):
    """Reset the bounded queue statistics at the specified modeling time."""
    q = queue_port
    expect_queue(q)
    model = q.get_model()
    code = 'runEventInStartTime $ enqueueEvent ' + str(reset_time)
    code += ' $ Q.resetQueue ' + q.read()
    model.add_action(code)
