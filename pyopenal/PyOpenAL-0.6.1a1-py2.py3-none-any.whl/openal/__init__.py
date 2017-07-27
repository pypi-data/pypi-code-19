from ._al import *
from ._alc import *

import ctypes

import os, sys

import traceback ## remove later

try:
    from pyogg import *
    PYOGG_AVAIL = True
except ImportError:
    PYOGG_AVAIL = False

try:
    import wave
    WAVE_AVAIL = True
except:
    WAVE_AVAIL = False

try:
    long
except:
    long = int

OAL_DONT_AUTO_INIT = False

OAL_STREAM_BUFFER_COUNT = 2

WAVE_STREAM_BUFFER_SIZE = 4096*4

MAX_FLOAT = sys.float_info.max

_items = []

class OalError(Exception):
    pass

def _err(msg):
    raise OalError(msg)

class _vec6:
    def __init__(self, *args):
        self.__truediv__ = self.__div__
        if len(args) == 6:
            self.x = float(args[0])
            self.y = float(args[1])
            self.z = float(args[2])
            self.a = float(args[3])
            self.b = float(args[4])
            self.c = float(args[5])
            
        elif len(args) == 1 and type(args[0]) in (ctypes.c_float*6, ctypes.c_int*6, tuple, list):
            self.x = args[0][0]
            self.y = args[0][1]
            self.z = args[0][2]
            self.a = args[0][3]
            self.b = args[0][4]
            self.c = args[0][5]
        elif len(args) == 1:
            self.x = args[0].x
            self.y = args[0].y
            self.z = args[0].z
            self.a = args[0].a
            self.b = args[0].b
            self.c = args[0].c
        else:
            self.x = self.y = self.z = self.a = self.b = self.c = 0.
    def __add__(self, *args):
        x = self.x
        y = self.y
        z = self.z
        a = self.a
        b = self.b
        c = self.c
        if len(args) == 6:
            x += float(args[0])
            y += float(args[1])
            z += float(args[2])
            a += float(args[3])
            b += float(args[4])
            c += float(args[5])
            
        elif len(args) == 1 and type(args[0]) in (ctypes.c_float*6, ctypes.c_int*6, tuple, list):
            x += args[0][0]
            y += args[0][1]
            z += args[0][2]
            a += args[0][3]
            b += args[0][4]
            c += args[0][5]
        elif len(args) == 1 and type(args[0]) in (int, float):
            x += args[0]
            y += args[0]
            z += args[0]
            a += args[0]
            b += args[0]
            c += args[0]
        else:
            x += args[0].x
            y += args[0].y
            z += args[0].z
            a += args[0].a
            b += args[0].b
            c += args[0].c
        return (x,y,z, a, b, c)
    def __mul__(self, *args):
        x = self.x
        y = self.y
        z = self.z
        a = self.a
        b = self.b
        c = self.c
        if len(args) == 6:
            x *= float(args[0])
            y *= float(args[1])
            z *= float(args[2])
            a *= float(args[3])
            b *= float(args[4])
            c *= float(args[5])
            
        elif len(args) == 1 and type(args[0]) in (ctypes.c_float*6, ctypes.c_int*6, tuple, list):
            x *= args[0][0]
            y *= args[0][1]
            z *= args[0][2]
            a *= args[0][3]
            b *= args[0][4]
            c *= args[0][5]
        elif len(args) == 1 and type(args[0]) in (int, float):
            x *= args[0]
            y *= args[0]
            z *= args[0]
            a *= args[0]
            b *= args[0]
            c *= args[0]
        else:
            x *= args[0].x
            y *= args[0].y
            z *= args[0].z
            a *= args[0].a
            b *= args[0].b
            c *= args[0].c
        return (x,y,z, a, b, c)
    def __sub__(self, *args):
        x = self.x
        y = self.y
        z = self.z
        a = self.a
        b = self.b
        c = self.c
        if len(args) == 6:
            x -= float(args[0])
            y -= float(args[1])
            z -= float(args[2])
            a -= float(args[3])
            b -= float(args[4])
            c -= float(args[5])
            
        elif len(args) == 1 and type(args[0]) in (ctypes.c_float*6, ctypes.c_int*6, tuple, list):
            x -= args[0][0]
            y -= args[0][1]
            z -= args[0][2]
            a -= args[0][3]
            b -= args[0][4]
            c -= args[0][5]
        elif len(args) == 1 and type(args[0]) in (int, float):
            x -= args[0]
            y -= args[0]
            z -= args[0]
            a -= args[0]
            b -= args[0]
            c -= args[0]
        else:
            x -= args[0].x
            y -= args[0].y
            z -= args[0].z
            a -= args[0].a
            b -= args[0].b
            c -= args[0].c
        return (x,y,z)
    def __div__(self, *args):
        x = self.x
        y = self.y
        z = self.z
        a = self.a
        b = self.b
        c = self.c
        if len(args) == 6:
            x /= float(args[0])
            y /= float(args[1])
            z /= float(args[2])
            a /= float(args[3])
            b /= float(args[4])
            c /= float(args[5])
            
        elif len(args) == 1 and type(args[0]) in (ctypes.c_float*6, ctypes.c_int*6, tuple, list):
            x /= args[0][0]
            y /= args[0][1]
            z /= args[0][2]
            a /= args[0][3]
            b /= args[0][4]
            c /= args[0][5]
        elif len(args) == 1 and type(args[0]) in (int, float):
            x /= args[0]
            y /= args[0]
            z /= args[0]
            a /= args[0]
            b /= args[0]
            c /= args[0]
        else:
            x /= args[0].x
            y /= args[0].y
            z /= args[0].z
            a /= args[0].a
            b /= args[0].b
            c /= args[0].c
        return (x,y,z,a,b,c)
    def __iadd__(self, *args):
        self.x, self.y, self.z, self.a, self.b, self.c = self.__add__(*args)
        return self
    def __isub__(self, *args):
        self.x, self.y, self.z, self.a, self.b, self.c = self.__sub__(*args)
        return self
    def __imul__(self, *args):
        self.x, self.y, self.z, self.a, self.b, self.c = self.__mul__(*args)
        return self
    def __idiv__(self, *args):
        self.x, self.y, self.z, self.a, self.b, self.c = self.__div__(*args)
        return self
    def __str__(self):
        return "vec6( {} , {} , {} , {} , {} , {})".format(self.x, self.y, self.z, self.a, self.b, self.c)

    def __repr__(self):
        return self.__str__()

    def asTuple(self):
        return (self.x, self.y, self.z, self.a, self.b, self.c )

    def asCTuple(self):
        return (ctypes.c_float*6)(*self.asTuple())

class _vec3:
    def __init__(self, *args):
        self.__truediv__ = self.__div__
        if len(args) == 3:
            self.x = float(args[0])
            self.y = float(args[1])
            self.z = float(args[2])
            
        elif len(args) == 1 and type(args[0]) in (ctypes.c_float*3, ctypes.c_int*3, tuple, list):
            self.x = args[0][0]
            self.y = args[0][1]
            self.z = args[0][2]
        elif len(args) == 1:
            self.x = args[0].x
            self.y = args[0].y
            self.z = args[0].z
        else:
            self.x = self.y = self.z = 0.
    def __add__(self, *args):
        x = self.x
        y = self.y
        z = self.z
        if len(args) == 3:
            x += float(args[0])
            y += float(args[1])
            z += float(args[2])
            
        elif len(args) == 1 and type(args[0]) in (ctypes.c_float*3, ctypes.c_int*3, tuple, list):
            x += args[0][0]
            y += args[0][1]
            z += args[0][2]
        elif len(args) == 1 and type(args[0]) in (int, float):
            x += args[0]
            y += args[0]
            z += args[0]
        else:
            x += args[0].x
            y += args[0].y
            z += args[0].z
        return (x,y,z)
    def __mul__(self, *args):
        x = self.x
        y = self.y
        z = self.z
        if len(args) == 3:
            x *= float(args[0])
            y *= float(args[1])
            z *= float(args[2])
            
        elif len(args) == 1 and type(args[0]) in (ctypes.c_float*3, ctypes.c_int*3, tuple, list):
            x *= args[0][0]
            y *= args[0][1]
            z *= args[0][2]
        elif len(args) == 1 and type(args[0]) in (int, float):
            x *= args[0]
            y *= args[0]
            z *= args[0]
        else:
            x *= args[0].x
            y *= args[0].y
            z *= args[0].z
        return (x,y,z)
    def __sub__(self, *args):
        x = self.x
        y = self.y
        z = self.z
        if len(args) == 3:
            x -= float(args[0])
            y -= float(args[1])
            z -= float(args[2])
            
        elif len(args) == 1 and type(args[0]) in (ctypes.c_float*3, ctypes.c_int*3, tuple, list):
            x -= args[0][0]
            y -= args[0][1]
            z -= args[0][2]
        elif len(args) == 1 and type(args[0]) in (int, float):
            x -= args[0]
            y -= args[0]
            z -= args[0]
        else:
            x -= args[0].x
            y -= args[0].y
            z -= args[0].z
        return (x,y,z)
    def __div__(self, *args):
        x = self.x
        y = self.y
        z = self.z
        if len(args) == 3:
            x /= float(args[0])
            y /= float(args[1])
            z /= float(args[2])
            
        elif len(args) == 1 and type(args[0]) in (ctypes.c_float*3, ctypes.c_int*3, tuple, list):
            x /= args[0][0]
            y /= args[0][1]
            z /= args[0][2]
        elif len(args) == 1 and type(args[0]) in (int, float):
            x /= args[0]
            y /= args[0]
            z /= args[0]
        else:
            x /= args[0].x
            y /= args[0].y
            z /= args[0].z
        return (x,y,z)
    def __iadd__(self, *args):
        self.x, self.y, self.z = self.__add__(*args)
        return self
    def __isub__(self, *args):
        self.x, self.y, self.z = self.__sub__(*args)
        return self
    def __imul__(self, *args):
        self.x, self.y, self.z = self.__mul__(*args)
        return self
    def __idiv__(self, *args):
        self.x, self.y, self.z = self.__div__(*args)
        return self
    def __str__(self):
        return "vec3( {} , {} , {} )".format(self.x,self.y,self.z)

    def __repr__(self):
        return self.__str__()

    def asTuple(self):
        return (self.x,self.y,self.z)

    def asCTuple(self):
        return (ctypes.c_float*3)(*self.asTuple())

_oaldevice = None

_oalcontext = None

def oalInit(device_specifier=None, context_attr_list=None):
    """Sets up OpenAL device and context (if not yet created)"""
    global _oaldevice, _oalcontext
    
    if not _oaldevice:
        _oaldevice = alcOpenDevice(device_specifier)
        
    if not _oaldevice:
        raise OalError("Default OpenAL device couldn't be opened")

    if not _oalcontext:
        _oalcontext = alcCreateContext(_oaldevice, context_attr_list)
        
    if not _oalcontext:
        raise OalError("OpenAL context couldn't be created")

    alcMakeContextCurrent(_oalcontext)

def oalGetDevice():
    """Returns the OpenAL device oal is using"""
    global _oaldevice
    return _oaldevice

def oalGetContext():
    """Returns the OpenAL context oal is using"""
    global _oalcontext
    return _oalcontext

def oalGetInit():
    global _oaldevice, _oalcontext

    return bool(_oaldevice) and bool(_oalcontext)

def _nlError():
    _err("PyOpenAL wasn't loaded yet, please run oalInit() first")

def _check():
    if not oalGetInit():
        if OAL_DONT_AUTO_INIT:
            _nlError()
        else:
            oalInit()

def _no_pyogg_error(*args, **kw):
    _err("You have to set up pyogg in order to use this function. Go to https://github.com/Zuzu-Typ/PyOgg to get it")

if WAVE_AVAIL:
    class WaveFile:
        def __init__(self,path):
            self.file_ = wave.open(path)

            self.channels = self.file_.getnchannels()

            self.frequency = self.file_.getframerate()
            
            self.buffer = b""

            change = 1

            while change:
                new_buf = self.file_.readframes(4096*8)
                change = len(new_buf)
                self.buffer += new_buf

            self.buffer_length = len(self.buffer)

            self.file_.close()

    class WaveFileStream:
        def __init__(self, path):
            self.file_ = wave.open(path)

            self.channels = self.file_.getnchannels()

            self.frequency = self.file_.getframerate()

            self.exists = True

        def clean_up(self):
            self.file_.close()

            self.exists = False

        def get_buffer(self):
            """get_buffer() -> bytesBuffer, bufferLength"""
            if not self.exists:
                return None
            buffer = b""
            
            while True:
                new_bytes = self.file_.readframes(WAVE_STREAM_BUFFER_SIZE*self.channels)
                
                if buffer:
                    buffer += new_bytes
                else:
                    buffer = new_bytes

                if len(new_bytes) == 0 or len(buffer) >= WAVE_STREAM_BUFFER_SIZE*self.channels:
                    break

            if len(buffer) == 0:
                self.clean_up()
                return(None)

            return(buffer, len(buffer))
else:
    class WaveFile:
        def __init__(*args, **kw):
            _err("Wave seems top be unavailable (maybe your Python version doesn't support it...?")
        
class Listener:
    def __init__(self):
        self.gain = 0.
        self.position = _vec3(0.,0.,0.)
        self.orientation = _vec6(0.,0.,-1.,0.,1.,0.)
        self.velocity = _vec3(0.,0.,0.)

    def _setPos(self):
        _check()
        alListenerfv(AL_POSITION, self.position.asCTuple())

    def _setGain(self):
        _check()
        alListenerf(AL_GAIN, ctypes.c_float(self.gain))

    def _setOrientation(self):
        _check()
        alListenerfv(AL_ORIENTATION, self.orientation.asCTuple())

    def _setVelocity(self):
        _check()
        alListenerfv(AL_VELOCITY, self.velocity.asCTuple())

    def move(self, v):
        try:
            self.position += v
            self._setPos()
        except:
            raise OalError("Unsupported argument for move: {}".format(v))

    def move_to(self, v):
        try:
            self.position = _vec3(v)
            self._setPos()
        except:
            raise OalError("Unsupported argument for move_to: {}".format(v))

    def set_position(self,v):
        try:
            self.position = _vec3(v)
            self._setPos()
        except:
            raise OalError("Unsupported argument for set_position: {}".format(v))

    def set_orientation(self,v):
        try:
            self.orientation = _vec6(v)
            self._setOrientation()
        except:
            raise OalError("Unsupported argument for set_orientation: {}".format(v))

    def set_velocity(self, v):
        try:
            self.velocity = _vec3(v)
            self._setVelocity()
        except:
            raise OalError("Unsupported argument for set_velocity: {}".format(v))

    def set_gain(self, value):
        try:
            self.gain = value
            self._setGain()
        except:
            raise OalError("Unsupported argument for set_gain: {}".format(value))

_listener = Listener()

def _to_int(i):
    if type(i) in (int, long):
        return i
    elif type(i) in (ctypes.c_int, ctypes.c_char):
        return i.value

def _to_c_int(i):
    if type(i) in (int, long):
        return ctypes.c_int(i)
    elif type(i) in (ctypes.c_uint, ctypes.c_char):
        return ctypes.c_int(i.value)

def _to_c_uint(i):
    if type(i) in (int, long):
        return ctypes.c_uint(i)
    elif type(i) in (ctypes.c_int, ctypes.c_char):
        return ctypes.c_uint(i.value)

def _channels_to_al(ch):
    if ch == 1:
        return(ctypes.c_int(AL_FORMAT_MONO16))
    elif ch == 2:
        return(ctypes.c_int(AL_FORMAT_STEREO16))

class Buffer:
    def __init__(self, *args):
        _check()
        self._exitsts = True
        self.id = ctypes.c_uint()
        alGenBuffers(1, ctypes.pointer(self.id))

        self.fill(*args)

    def geti(self):
        return ctypes.c_int(self.id.value)

    def getui(self):
        return self.id

    def destroy(self):
        if self._exitsts:
            alDeleteBuffers(1, ctypes.pointer(self.id))
            self._exitsts = False

    def fill(self, *args):
        if len(args) == 1:
            file_ = args[0]
            alBufferData(self.getui(), _channels_to_al(file_.channels), file_.buffer, _to_c_int(file_.buffer_length), _to_c_int(file_.frequency))
        else:
            alBufferData(self.getui(), _to_int(args[0]), args[1], _to_int(args[2]), _to_int(args[3]))

class StreamBuffer:
    def __init__(self, stream, count):
        self.buffer_ids = (ctypes.c_uint * count)()

        alGenBuffers(count, ctypes.cast(ctypes.pointer(self.buffer_ids), ctypes.POINTER(ctypes.c_uint)))

        self.stream = stream

        self._count = count

        self._exitsts = True

        for id_ in range(count):
            self.fill_buffer(id_)

        self.last_buffer = count - 1

    def destroy(self):
        if self._exitsts:
            alDeleteBuffers(self._count, ctypes.cast(ctypes.pointer(self.buffer_ids), ctypes.POINTER(ctypes.c_uint)))
            self._exitsts = False

    def fill_buffer(self, id_):
        if self._exitsts:
            buffer_info = self.stream.get_buffer()
            if buffer_info:
                buffer_, buffer_size = buffer_info
                alBufferData(_to_c_uint(self.buffer_ids[id_]),  _channels_to_al(self.stream.channels), buffer_, _to_c_int(buffer_size), _to_c_int(self.stream.frequency))
                return True
            else:
                return False

class Source:
    def __init__(self, buffer_ = None):
        global _items
        _check()
        self.id = ctypes.c_uint()
        alGenSources(1, ctypes.pointer(self.id))

        self._exitsts = True

        self.pitch = 1.

        self.gain = 1.

        self.max_distance = MAX_FLOAT

        self.rolloff_factor = 1.

        self.reference_distance = 1.

        self.min_gain = 0.

        self.max_gain = 1.

        self.cone_outer_gain = 0.

        self.cone_inner_angle = 360.

        self.cone_outer_angle = 360.

        self.position = _vec3(0.,0.,0.)

        self.velocity = _vec3(0.,0.,0.)

        self.looping = False

        self.direction = _vec3(0.,0.,0.)

        self.source_relative = False

        self.source_type = AL_UNDETERMINED

        self._state = AL_INITIAL

        if buffer_:
            self.set_buffer(buffer_)

        _items.append(self)

    def _set(self, enum, value):
        if type(value) in (float,):
            alSourcef(self.id, ctypes.c_int(enum), ctypes.c_float(value))
        elif type(value) in (int, bool):
            alSourcei(self.id, ctypes.c_int(enum), ctypes.c_int(value))
        elif type(value) in (_vec3, _vec6):
            alSourcefv(self.id, ctypes.c_int(enum), value.asCTuple())
        elif type(value) in (ctypes.c_float*3, ctypes.c_float*6):
            alSourcefv(self.id,ctypes.c_int(enum), value)
        elif type(value) in (tuple, list):
            if len(value) == 3:
                alSourcefv(self.id, ctypes.c_int(enum), _vec3(value).asCTuple())
            elif len(value) == 6:
                alSourcefv(self.id, ctypes.c_int(enum), _vec6(value).asCTuple())

    def _to_val(self,value):
        if type(value) in (float, bool, _vec3, _vec6):
            return value
        elif type(value) in (int,):
            return float(value)
        elif type(value) in (ctypes.c_float*3,):
            return _vec3(value)
        elif type(value) in (ctypes.c_float*6,):
            return _vec6(value)
        elif type(value) in (tuple, list):
            if len(value) == 3:
                return _vec3(value)
            elif len(value) == 6:
                return _vec6(value)

    def destroy(self):
        if self.get_state() == AL_PLAYING:
            self.stop()
        try:
            self.buffer.destroy()
        except:
            pass
        if self._exitsts:
            alDeleteSources(1, ctypes.pointer(self.id))
            self._exitsts = False

    def set_pitch(self, value):
        self._set(AL_PITCH, value)
        self.pitch = self._to_val(value)

    def set_gain(self, value):
        self._set(AL_GAIN, value)
        self.gain = self._to_val(value)

    def set_max_distance(self, value):
        self._set(AL_MAX_DISTANCE, value)
        self.max_distance = self._to_val(value)

    def set_rolloff_factor(self, value):
        self._set(AL_ROLLOFF_FACTOR, value)
        self.rolloff_factor = self._to_val(value)

    def set_reference_distance(self, value):
        self._set(AL_REFERENCE_DISTANCE, value)
        self.reference_distance = self._to_val(value)

    def set_min_gain(self,value):
        self._set(AL_MIN_GAIN, )
        self.min_gain = self._to_val(value)

    def set_max_gain(self,value):
        self._set(AL_MAX_GAIN, )
        self.max_gain = self._to_val(value)

    def set_cone_outer_gain(self, value):
        self._set(AL_CONE_OUTER_GAIN, value)
        self.cone_outer_gain = self._to_val(value)

    def set_cone_inner_angle(self, value):
        self._set(AL_CONE_INNER_ANGLE, value)
        self.cone_inner_angle = self._to_val(value)

    def set_cone_outer_angle(self, value):
        self._set(AL_CONE_OUTER_ANGLE, value)
        self.cone_outer_angle = self._to_val(value)

    def set_position(self, value):
        self._set(AL_POSITION, value)
        self.position = self._to_val(value)

    def set_velocity(self, value):
        self._set(AL_VELOCITY, value)
        self.velocity = self._to_val(value)

    def set_looping(self, value):
        self._set(AL_LOOPING, value)
        self.looping = self._to_val(value)

    def set_direction(self, value):
        self._set(AL_DIRECTION, value)
        self.direction = self._to_val(value)

    def set_source_relative(self, value):
        self._set(AL_SOURCE_RELATIVE, value)
        self.source_relative = self._to_val(value)

    def set_source_type(self, value):
        self._set(AL_SOURCE_TYPE, value)
        self.source_type = self._to_val(value)

    def geti(self):
        return ctypes.c_int(self.id.value)

    def getui(self):
        return self.id

    def set_buffer(self, buffer_):
        self.buffer = buffer_

        alSourcei(self.id, AL_BUFFER, self.buffer.geti())

    def get_state(self):
        value = ctypes.c_int()
        alGetSourcei(self.id, AL_SOURCE_STATE, value)
        return value.value

    def play(self):
        alSourcePlay(self.id)
        self._state = AL_PLAYING

    def stop(self):
        alSourceStop(self.id)
        self._state = AL_STOPPED

    def pause(self):
        alSourcePause(self.id)
        self._state = AL_PAUSED

    def rewind(self):
        alSourceRewind(self.id)

class SourceStream(Source):
    def __init__(self, stream):
        global _items
        _check()
        self.id = ctypes.c_uint()
        alGenSources(1, ctypes.pointer(self.id))

        self._exitsts = True

        self.pitch = 1.

        self.gain = 1.

        self.max_distance = MAX_FLOAT

        self.rolloff_factor = 1.

        self.reference_distance = 1.

        self.min_gain = 0.

        self.max_gain = 1.

        self.cone_outer_gain = 0.

        self.cone_inner_angle = 360.

        self.cone_outer_angle = 360.

        self.position = _vec3(0.,0.,0.)

        self.velocity = _vec3(0.,0.,0.)

        self.looping = False

        self.direction = _vec3(0.,0.,0.)

        self.source_relative = False

        self.source_type = AL_UNDETERMINED

        self.buffer = StreamBuffer(stream, OAL_STREAM_BUFFER_COUNT)

        self._continue = True

        alSourceQueueBuffers(self.id, OAL_STREAM_BUFFER_COUNT, self.buffer.buffer_ids)

    def update(self):
        if self._state != AL_PLAYING:
            return
        if self.get_state() == AL_STOPPED:
            self._continue = False
        if self._continue:
            buffers_processed = ctypes.c_int()

            alGetSourcei(self.id, AL_BUFFERS_PROCESSED, ctypes.pointer(buffers_processed))

            for buf_id in range(buffers_processed.value):
                unqueue = self.buffer.last_buffer + 1
                if unqueue >= OAL_STREAM_BUFFER_COUNT:
                    unqueue = 0

                alSourceUnqueueBuffers(self.id, 1, ctypes.pointer(_to_c_uint(self.buffer.buffer_ids[unqueue])))

                buffer_filled = self.buffer.fill_buffer(unqueue)

                if buffer_filled:
                    alSourceQueueBuffers(self.id, 1, ctypes.pointer(_to_c_uint(self.buffer.buffer_ids[unqueue])))

                    self.buffer.last_buffer += 1

                    if self.buffer.last_buffer >= OAL_STREAM_BUFFER_COUNT:
                        self.buffer.last_buffer = 0
                else:
                    self._continue = False

        else:
            buffers_processed = ctypes.c_int()
            alGetSourcei(self.id, AL_BUFFERS_QUEUED, ctypes.pointer(buffers_processed))

            for buf_id in range(buffers_processed.value):
                unqueue = self.buffer.last_buffer + 1
                if unqueue >= OAL_STREAM_BUFFER_COUNT:
                    unqueue = 0
                try:
                    alSourceUnqueueBuffers(self.id, 1, ctypes.pointer(_to_c_uint(self.buffer.buffer_ids[unqueue])))
                except:
                    pass
                self.buffer.last_buffer += 1
                
        return self._continue

def oalGetListener():
    global _listener
    return _listener

def oalQuit():
    global _oaldevice, _oalcontext, _items
    for item in _items:
        item.destroy()
    if _oalcontext:
        alcDestroyContext(_oalcontext)
    if _oaldevice:
        alcCloseDevice(_oaldevice)
    _oalcontext = _oaldevice = None
    _items = []

if PYOGG_AVAIL or WAVE_AVAIL:
    def oalLoadFile(path, ext_hint=None):
        """oalLoadFile(filepath [, extension_hint]) -> Source
        loads an ogg file to a source and returns it.
        You can use ext_hint to suggest the file type,
        in case the file extension is not ogg, vorbis or opus"""
        _check()
        if not ext_hint:
            ext_hint = os.path.splitext(path)[1]
        ext_hint = ext_hint.lower()
        if ext_hint in ("ogg", "vorbis", ".ogg", ".vorbis"):
            if not PYOGG_AVAIL:
                _no_pyogg_error()
                return
            file_ = VorbisFile(path)
        elif ext_hint in ("opus", ".opus"):
            if not PYOGG_AVAIL:
                _no_pyogg_error()
                return
            file_ = OpusFile(path)
        elif ext_hint in ("wav", ".wav", ".wave", "wave"):
            if not WAVE_AVAIL:
                _err("Wave seems top be unavailable (maybe your Python version doesn't support it...?")
                return
            file_ = WaveFile(path)
        else:
            _err("Unsupported file extension {}. You might want to consider using the ext_hint parameter to pass the file format".format(ext_hint))
            
        buffer_ = Buffer(file_)

        source = Source(buffer_)

        return source

    def oalStreamFile(path, ext_hint=None):
        """oalStreamFile(filepath [, extension_hint]) -> SourceStream
        loads an ogg file to a source-stream and returns it.
        You can use ext_hint to suggest the file type,
        in case the file extension is not ogg, vorbis or opus"""
        _check()
        if not ext_hint:
            ext_hint = os.path.splitext(path)[1]
        ext_hint = ext_hint.lower()

        if ext_hint in ("ogg", "vorbis", ".ogg", ".vorbis"):
            if not PYOGG_AVAIL:
                _no_pyogg_error()
                return
            stream = VorbisFileStream(path)
        elif ext_hint in ("opus", ".opus"):
            if not PYOGG_AVAIL:
                _no_pyogg_error()
                return
            stream = OpusFileStream(path)
        elif ext_hint in ("wav", ".wav", "wave", ".wave"):
            if not WAVE_AVAIL:
                _err("Wave seems top be unavailable (maybe your Python version doesn't support it...?")
                return
            stream = WaveFileStream(path)
        else:
            _err("Unsupported file extension {}. You might want to consider using the ext_hint parameter to pass the file format".format(ext_hint))

        return SourceStream(stream)
else:
    oalLoadFile = _no_pyogg_error
    oalStreamFile = _no_pyogg_error

def oalSetAutoInit(val):
    global OAL_STREAM_BUFFER_COUNT
    OAL_STREAM_BUFFER_COUNT = val

def oalSetStreamBufferCount(val):
    global OAL_STREAM_BUFFER_COUNT
    OAL_STREAM_BUFFER_COUNT = val

def waveSetStreamBufferSize(val):
    global WAVE_STREAM_BUFFER_SIZE
    WAVE_STREAM_BUFFER_SIZE = val
