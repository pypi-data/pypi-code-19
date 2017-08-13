# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.model import *
from simulation.aivika.modeler.port import *
from simulation.aivika.modeler.expr import *
from simulation.aivika.modeler.transform import *
from simulation.aivika.modeler.queue import *
from simulation.aivika.modeler.resource import *
from simulation.aivika.modeler.data_type import *
from simulation.aivika.modeler.util import *

def empty_stream(model, item_data_type):
    """Return an empty stream by the specified model and item data type."""
    base_comp = model.get_base_comp()
    y = StreamPort(model, item_data_type)
    comp_type = []
    comp_type.append('Simulation')
    if not (base_comp is None):
        comp_type.append(base_comp)
    comp_type.append(y.get_data_type())
    y.bind_to_input()
    y.write('return emptyStream :: ' + encode_data_type(comp_type))
    return y

def singleton_stream(model, item, item_data_type):
    """Return a stream consisting of exactly one element and inifinite tail."""
    base_comp = model.get_base_comp()
    y = StreamPort(model, item_data_type)
    comp_type = []
    comp_type.append('Simulation')
    if not (base_comp is None):
        comp_type.append(base_comp)
    comp_type.append(y.get_data_type())
    code = 'return (singletonStream '
    code += str(item)
    code += ') :: '
    code += encode_data_type(comp_type)
    y.bind_to_input()
    y.write(code)
    return y

def terminate_stream(stream_port):
    """Terminate the stream."""
    s = stream_port
    expect_stream(s)
    model = s.get_model()
    code = 'runProcessInStartTime $ sinkStream ' + s.read()
    s.bind_to_output()
    model.add_action(code)

def delay_stream(delay_item, stream_port):
    """Delay the stream by one step using the specified initial value.."""
    i = delay_item
    s = stream_port
    expect_stream(s)
    model = s.get_model()
    item_data_type = s.get_item_data_type()
    code = 'return $ delayStream '
    code += str(delay_item)
    code += ' '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def split_stream(count, stream_port):
    """Split the stream into the specified number of output streams and return them as a list."""
    s = stream_port
    expect_stream(s)
    model = s.get_model()
    model.add_package_import('array')
    model.add_module_import('import Data.Functor')
    model.add_module_import('import Data.Array')
    item_data_type = s.get_item_data_type()
    code0 = 'splitStream ' + str(count) + ' ' + s.read()
    code0 = 'fmap (listArray (0, ' + str(count) + ' - 1)) $ ' + code0
    ys0 = StreamPort(model, item_data_type)
    ys0.write(code0)
    ys0.bind_to_input()
    s.bind_to_output()
    ys = [ StreamPort(model, item_data_type) for i in range(0, count) ]
    for i in range(0, count):
        y = ys[i]
        code = 'return $ ' + ys0.read() + ' ! ' + str(i)
        y.write(code)
        y.bind_to_input()
    ys0.bind_to_output()
    return ys

def merge_streams(stream_ports):
    """Merge the list of streams in one resulting stream."""
    ps = stream_ports
    if len(ps) == 0:
        raise InvalidPortException('Required at least one port')
    else:
        p0 = ps[0]
        expect_stream(p0)
        expect_same_model(ps)
        expect_same_data_type(ps)
        model = p0.get_model()
        y = StreamPort(model, p0.get_item_data_type())
        for p in ps:
            p.bind_to_output()
        y.bind_to_input()
        code = ', '.join([ p.read() for p in ps ])
        code = '[' + code + ']'
        code = 'return $ concatStreams ' + code
        y.write(code)
        return y

def clone_stream(count, stream_port):
    """Clone the stream for the specified number of times and return the corresponding list."""
    s = stream_port
    expect_stream(s)
    model = s.get_model()
    model.add_package_import('array')
    model.add_module_import('import Data.Functor')
    model.add_module_import('import Data.Array')
    item_data_type = s.get_item_data_type()
    code0 = 'cloneStream ' + str(count) + ' ' + s.read()
    code0 = 'fmap (listArray (0, ' + str(count) + ' - 1)) $ ' + code0
    ys0 = StreamPort(model, item_data_type)
    ys0.write(code0)
    ys0.bind_to_input()
    s.bind_to_output()
    ys = [ StreamPort(model, item_data_type) for i in range(0, count) ]
    for i in range(0, count):
        y = ys[i]
        code = 'return $ ' + ys0.read() + ' ! ' + str(i)
        y.write(code)
        y.bind_to_input()
    ys0.bind_to_output()
    return ys

def test_stream(test_expr, stream_port):
    """Test the stream items and return a tuple of two streams: when the test passes and fails."""
    e = test_expr
    s = stream_port
    expect_expr(e)
    expect_stream(s)
    model = s.get_model()
    base_comp = model.get_base_comp()
    if base_comp is None:
        model.add_module_import('import qualified Simulation.Aivika.Queue.Infinite as IQ')
    else:
        model.add_module_import('import qualified Simulation.Aivika.Trans.Queue.Infinite as IQ')
    item_data_type = s.get_item_data_type()
    trueQ = create_unbounded_queue(model, item_data_type, name = None)
    falseQ = create_unbounded_queue(model, item_data_type, name = None)
    trueS = unbounded_dequeue_stream(trueQ)
    falseS = unbounded_dequeue_stream(falseQ)
    s.bind_to_output()
    code = 'consumeStream (\\a -> liftEvent $ do { f <- ' + e.read('a') + '; '
    code += 'if f then IQ.enqueue ' + trueQ.read() + ' a '
    code += 'else IQ.enqueue ' + falseQ.read() + ' a }) ' + s.read()
    code = 'runProcessInStartTime $ ' + code
    model.add_action(code)
    return (trueS, falseS)

def transform_stream(transform, stream_port):
    """Apply the specified transform to the input stream and return a new stream."""
    t = transform
    s = stream_port
    expect_transform(t)
    expect_stream(s)
    model = s.get_model()
    if model.get_main_model() != t.get_model().get_main_model():
        raise InvalidPortException('Expected both the stream ' + s.get_name() + ' and the transform to belong to the same model')
    item_data_type = s.get_item_data_type()
    code = 'return $ mapStreamM (\\a -> liftEvent '
    code += t.read('a')
    code += ') '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def within_stream(expr, stream_port):
    """Call the specified expression for side effect when processing the input stream within the resulting stream."""
    e = expr
    s = stream_port
    expect_expr(e)
    expect_stream(s)
    model = s.get_model()
    if model.get_main_model() != e.get_model().get_main_model():
        raise InvalidPortException('Expected both the stream ' + s.get_name() + ' and the expression to belong to the same model')
    item_data_type = s.get_item_data_type()
    code = 'return $ mapStreamM (\\a -> liftEvent '
    code += e.read('a')
    code += ' >> return a) '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def hold_stream(expr, stream_port):
    """Hold the process for the time interval specified by the expression when processing each transact from the stream."""
    e = expr
    s = stream_port
    expect_expr(e)
    expect_stream(stream_port)
    model = s.get_model()
    if model.get_main_model() != e.get_model().get_main_model():
        raise InvalidPortException('Expected both the stream ' + s.get_name() + ' and the expression to belong to the same model')
    item_data_type = s.get_item_data_type()
    code = 'return $ mapStreamM (\\a -> do { dt0 <- liftEvent $ '
    code += e.read('a')
    code += '; holdProcess dt0; return a }) '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def prefetch_stream(stream_port):
    """Prefetch the input stream requesting for one more data item in advance while the last received item is not yet fully processed in the chain of streams."""
    s = stream_port
    expect_stream(stream_port)
    model = s.get_model()
    item_data_type = s.get_item_data_type()
    code = 'return $ prefetchStream '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def filter_stream(expr, stream_port):
    """Filter only those data values that satisfy to the specified predicate."""
    e = expr
    s = stream_port
    expect_expr(e)
    expect_stream(stream_port)
    model = s.get_model()
    if model.get_main_model() != e.get_model().get_main_model():
        raise InvalidPortException('Expected both the stream ' + s.get_name() + ' and the expression to belong to the same model')
    item_data_type = s.get_item_data_type()
    code = 'return $ filterStreamM (\\a -> liftEvent $ '
    code += e.read('a')
    code += ') '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def take_stream_while(expr, stream_port):
    """Return the longest prefix of the stream of elements that satisfy the predicate."""
    e = expr
    s = stream_port
    expect_expr(e)
    expect_stream(stream_port)
    model = s.get_model()
    if model.get_main_model() != e.get_model().get_main_model():
        raise InvalidPortException('Expected both the stream ' + s.get_name() + ' and the expression to belong to the same model')
    item_data_type = s.get_item_data_type()
    code = 'return $ takeStreamWhileM (\\a -> liftEvent $ '
    code += e.read('a')
    code += ') '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def drop_stream_while(expr, stream_port):
    """Return the suffix of the stream of elements remaining after *take_stream_while*."""
    e = expr
    s = stream_port
    expect_expr(e)
    expect_stream(stream_port)
    model = s.get_model()
    if model.get_main_model() != e.get_model().get_main_model():
        raise InvalidPortException('Expected both the stream ' + s.get_name() + ' and the expression to belong to the same model')
    item_data_type = s.get_item_data_type()
    code = 'return $ dropStreamWhileM (\\a -> liftEvent $ '
    code += e.read('a')
    code += ') '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def take_stream(count, stream_port):
    """Return the prefix of the stream of the specified length."""
    s = stream_port
    expect_stream(stream_port)
    model = s.get_model()
    item_data_type = s.get_item_data_type()
    code = 'return $ takeStream '
    code += str(count)
    code += ' '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def drop_stream(count, stream_port):
    """Return the suffix of the stream after the specified first elements."""
    s = stream_port
    expect_stream(stream_port)
    model = s.get_model()
    item_data_type = s.get_item_data_type()
    code = 'return $ dropStream '
    code += str(count)
    code += ' '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y

def trace_stream(stream_port, request_message = None, response_message = None):
    """Allows tracing the input stream within the resulting stream."""
    s = stream_port
    expect_stream(stream_port)
    model = s.get_model()
    item_data_type = s.get_item_data_type()
    code = 'return $ traceStream '
    code += encode_maybe(encode_str, request_message)
    code += ' '
    code += encode_maybe(encode_str, response_message)
    code += ' '
    code += s.read()
    y = StreamPort(model, item_data_type)
    y.write(code)
    y.bind_to_input()
    s.bind_to_output()
    return y
