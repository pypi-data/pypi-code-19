# coding: utf-8
from __future__ import division, absolute_import, unicode_literals
from builtins import *

import atexit
import zmq

from collections import Iterable
from ctypes import *
from enum import Enum
from six import string_types

from . import tecrpc
from .tecrpc.Argument import *
from .tecrpc.ArgumentType import *
from .tecrpc.Header import *
from .tecrpc.Message import *
from .tecrpc.OperationType import *
from .tecrpc.Reply import *
from .tecrpc.Request import *
from .tecrpc.Status import *
import flatbuffers
from flatbuffers import number_types as N

from ..constant import *
from ..exception import *
from .tecutil_rpc import TecUtilRPC, ValueType


def CreateVector(self, element_type, v):
    """Writes a list or array to the buffer, using ctypes arrays."""
    _flags = {
        c_ubyte: N.Uint8Flags,
        c_ushort: N.Uint16Flags,
        c_uint: N.Uint32Flags,
        c_ulong: N.Uint64Flags,
        c_byte: N.Int8Flags,
        c_short: N.Int16Flags,
        c_int: N.Int32Flags,
        c_long: N.Int64Flags,
        c_float: N.Float32Flags,
        c_double: N.Float64Flags,
    }

    self.assertNotNested()
    self.nested = True

    flags = _flags[element_type]
    nelements = len(v)
    nbytes = nelements * flags.bytewidth

    # ensure or cast v to array of element_types
    if not isinstance(v, Array):
        v = (element_type * nelements)(*v)
        p = cast(v, POINTER(element_type))
    elif not isinstance(v, element_type * nelements):
        nbytes = nelements * sizeof(v._type_)
        nelements, r = divmod(nbytes, sizeof(element_type))
        if r:
            raise TypeError('could not cast array to the requested type')
        p = cast(v, POINTER(element_type))
        v = (element_type * nelements)(*[p[i] for i in range(nelements)])

    self.Prep(N.UOffsetTFlags.bytewidth, nbytes * flags.bytewidth)
    self.Place(0, flags)

    l = N.UOffsetTFlags.py_type(nelements)

    self.head = N.UOffsetTFlags.py_type(self.Head() - l)
    self.Bytes[self.Head():self.Head() + l] = v

    return self.EndVector(nelements)

flatbuffers.Builder.CreateVector = CreateVector


def GetVector(self, offset, element_type, j=None):
    o = flatbuffers.number_types.UOffsetTFlags.py_type(self.Offset(offset))
    if o:
        a = self.Vector(o)
        if j is None:
            addr = addressof(cast(self.Bytes, POINTER(c_byte)).contents) + a
            return (element_type * self.VectorLen(o)).from_address(addr)
        else:
            off = a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 1)
            return self.Get(flatbuffers.number_types.Int8Flags, offs)
    else:
        return [] if j is None else 0

flatbuffers.table.Table.GetVector = GetVector


def Int8Array(self, j=None):
    return self._tab.GetVector(30, c_int8, j)


def Uint8Array(self, j=None):
    return self._tab.GetVector(32, c_uint8, j)


def Int16Array(self, j=None):
    return self._tab.GetVector(34, c_int16, j)


def Uint16Array(self, j=None):
    return self._tab.GetVector(36, c_uint16, j)


def Int32Array(self, j=None):
    return self._tab.GetVector(38, c_int32, j)


def Uint32Array(self, j=None):
    return self._tab.GetVector(40, c_uint32, j)


def Int64Array(self, j=None):
    return self._tab.GetVector(42, c_int64, j)


def Uint64Array(self, j=None):
    return self._tab.GetVector(44, c_uint64, j)


def Float32Array(self, j=None):
    return self._tab.GetVector(46, c_float, j)


def Float64Array(self, j=None):
    return self._tab.GetVector(48, c_double, j)

tecrpc.Argument.Argument.Int8Array = Int8Array
tecrpc.Argument.Argument.Uint8Array = Uint8Array
tecrpc.Argument.Argument.Int16Array = Int16Array
tecrpc.Argument.Argument.Uint16Array = Uint16Array
tecrpc.Argument.Argument.Int32Array = Int32Array
tecrpc.Argument.Argument.Uint32Array = Uint32Array
tecrpc.Argument.Argument.Int64Array = Int64Array
tecrpc.Argument.Argument.Uint64Array = Uint64Array
tecrpc.Argument.Argument.Float32Array = Float32Array
tecrpc.Argument.Argument.Float64Array = Float64Array


def build_null_arg(builder):
    ArgumentStart(builder)
    ArgumentAddType(builder, ArgumentType.Null)
    return ArgumentEnd(builder)


def build_scalar_arg(builder, argtype, arg):
    ArgumentStart(builder)
    if argtype is c_bool:
        ArgumentAddBoolean(builder, arg)
    elif argtype is c_int32:
        ArgumentAddInt32Value(builder, arg)
    elif argtype is c_uint32:
        ArgumentAddUint32Value(builder, arg)
    elif argtype is c_int64:
        ArgumentAddInt64Value(builder, arg)
    elif argtype is c_uint64:
        ArgumentAddUint64Value(builder, arg)
    elif argtype is c_float:
        ArgumentAddFloat32Value(builder, arg)
    elif argtype is c_double:
        ArgumentAddFloat64Value(builder, arg)
    else:
        raise TecplotNotImplementedError(argtype, arg)
    return ArgumentEnd(builder)


def build_array_arg(builder, argtype, arg):
    v = builder.CreateVector(argtype, arg)
    ArgumentStart(builder)
    if argtype is c_uint8:
        ArgumentAddUint8Array(builder, v)
    elif argtype is c_uint32:
        ArgumentAddUint32Array(builder, v)
    elif argtype is c_uint64:
        ArgumentAddUint64Array(builder, v)
    elif argtype is c_int32:
        ArgumentAddInt32Array(builder, v)
    elif argtype is c_int64:
        ArgumentAddInt64Array(builder, v)
    elif argtype is c_float:
        ArgumentAddFloat32Array(builder, v)
    elif argtype is c_double:
        ArgumentAddFloat64Array(builder, v)
    else:
        raise TecplotNotImplementedError(argtype, arg, v)
    return ArgumentEnd(builder)


def build_text_arg(builder, arg):
    a = builder.CreateString(arg or '')
    ArgumentStart(builder)
    ArgumentAddText(builder, a)
    return ArgumentEnd(builder)


def build_arbparam_arg(builder, argtype, arg):
    if isinstance(arg, string_types):
        a = builder.CreateString(arg or '')
        ArgumentStart(builder)
        ArgumentAddType(builder, ArgumentType.Text)
        ArgumentAddText(builder, a)
        return ArgumentEnd(builder)
    else:
        ArgumentStart(builder)
        if argtype is POINTER:
            ArgumentAddUint64Value(builder, arg)
        elif argtype is POINTER(c_char_p):
            ArgumentAdd(builder, arg)
        elif isinstance(arg, Enum):
            ArgumentAddInt64Value(builder, arg.value)
        else:
            try:
                ArgumentAddInt64Value(builder, arg.value)
            except AttributeError:
                ArgumentAddInt64Value(builder, arg)
        return ArgumentEnd(builder)


def build_address_arg(builder, argtype, arg):
    assert argtype is c_uint64
    ArgumentStart(builder)
    if arg is None:
        ArgumentAddType(builder, ArgumentType.Null)
    else:
        ArgumentAddUint64Value(builder, arg)
    return ArgumentEnd(builder)


def build_request(builder, tecutil_command, *args, **kwargs):
    lock = kwargs.pop('lock', True)
    opname = builder.CreateString(tecutil_command)

    reqargs = []
    for valtype, argtype, arg in args:
        if arg is None:
            reqargs.append(build_null_arg(builder))
        elif valtype == ValueType.Scalar:
            reqargs.append(build_scalar_arg(builder, argtype, arg))
        elif valtype == ValueType.Array:
            reqargs.append(build_array_arg(builder, argtype, arg))
        elif valtype == ValueType.Text:
            reqargs.append(build_text_arg(builder, arg))
        elif valtype == ValueType.ArbParam:
            reqargs.append(build_arbparam_arg(builder, argtype, arg))
        elif valtype == ValueType.Address:
            reqargs.append(build_address_arg(builder, argtype, arg))
        else:
            raise TecplotNotImplementedError(valtype, argtype, arg)

    RequestStartArgsVector(builder, len(reqargs))
    for arg in reversed(reqargs):
        builder.PrependUOffsetTRelative(arg)
    args = builder.EndVector(len(reqargs))

    RequestStart(builder)
    reqtype = OperationType.TecUtil
    if lock:
        reqtype |= OperationType.LockRequired
    RequestAddType(builder, reqtype)
    RequestAddArgs(builder, args)
    RequestAddOperation(builder, opname)
    request = RequestEnd(builder)

    MessageStart(builder)
    MessageAddRequest(builder, request)
    reqmsg = MessageEnd(builder)

    builder.Finish(reqmsg)


class TecUtilClient(TecUtilRPC):
    def __init__(self):
        self.socket = None

    def connect(self, host='localhost', port=7600):
        # Prepare the ZeroMQ context
        self._context = zmq.Context()

        # Setup the request server socket
        self.socket = self._context.socket(zmq.REQ)

        # Set high water mark for out-going messages.
        # This is the maximum number of messages to
        # store in the out-going queue - send() will
        # block until the HWM is below this limit.
        self.socket.setsockopt(zmq.SNDHWM, 10)

        # Do not linger once socket is closed.
        # Send messages immediately, and possibly
        # fail, but do not attempt to recover.
        self.socket.setsockopt(zmq.LINGER, 0)

        # Connect requester to the reply sever
        self.endpoint = "tcp://{host}:{port}".format(host=host, port=port)
        self.socket.connect(self.endpoint)

        atexit.register(self.disconnect)

    @property
    def connected(self):
        return self.socket is not None

    def disconnect(self):
        atexit.unregister(self.disconnect)
        if self.socket:
            self.socket.disconnect(self.endpoint)
            self.socket = None

    def sndrcv(self, tecutil_command, *args, **kwargs):
        builder = flatbuffers.Builder(0)
        build_request(builder, tecutil_command, *args, **kwargs)
        self.socket.send(builder.Output())
        reply_message = self.socket.recv()
        return Message.GetRootAsMessage(reply_message, 0)

    def chk(self, reply):
        if reply.Status() != Status.Success:
            errmsg = reply.Log()
            raise TecplotSystemError(errmsg)

    def read_arbparam(self, arg):
        T = ArgumentType
        t = arg.Type()
        if t & (T.Unspecified | T.Address):
            return arg.Int64Value()
        elif t & T.Null:
            return None
        elif t & T.Text:
            return arg.Text().decode('utf-8')
        else:
            TecplotNotImplementedError

    def read_text(self, arg):
        T = ArgumentType
        t = arg.Type()
        if t & (T.Unspecified | T.Text):
            txt = arg.Text()
            if not isinstance(txt, string_types):
                txt = txt.decode('utf-8')
            return txt
        elif t & T.Null:
            return None
        else:
            TecplotNotImplementedError

    def read_ptr(self, arg):
        return arg.Uint64Value()

    def read_array(self, arg, argtype):
        _dispatch = {
            c_uint8: arg.Uint8Array,
            c_int8: arg.Int8Array,
        }
        return _dispatch[argtype]()
