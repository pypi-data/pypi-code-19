"""This file is part of libqrencode python ctypes bindings.

Copyright (C) 2012 Matthew Baker <mu.beta.06@gmail.com>

This is free software: you can redistribute it and/or modify
it under the terms of the LGNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the LGNU Lesser General Public License
along with this software.  If not, see <http://www.gnu.org/licenses/>."""


from ctypes import *


try:
    _library = CDLL('/usr/local/lib/libqrencode.so')
except OSError:
    _library = CDLL('/usr/lib/arm-linux-gnueabihf/libqrencode.so')


QR_ECLEVEL_H = 3
QR_MODE_FNC1FIRST = 6
QR_MODE_KANJI = 3
QR_ECLEVEL_Q = 2
QR_MODE_NUM = 0
QR_MODE_ECI = 5
QR_MODE_8 = 2
QR_MODE_AN = 1
QR_ECLEVEL_L = 0
QR_MODE_FNC1SECOND = 7
QR_ECLEVEL_M = 1
QR_MODE_STRUCTURE = 4
QR_MODE_NUL = -1

# values for enumeration 'QRencodeMode'
QRencodeMode = c_int # enum

# values for enumeration 'QRecLevel'
QRecLevel = c_int # enum
class _QRinput(Structure):
    pass
QRinput = _QRinput
_QRinput._fields_ = [
]
QRinput_new = _library.QRinput_new
QRinput_new.restype = POINTER(QRinput)
QRinput_new.argtypes = []
QRinput_new2 = _library.QRinput_new2
QRinput_new2.restype = POINTER(QRinput)
QRinput_new2.argtypes = [c_int, QRecLevel]
QRinput_newMQR = _library.QRinput_newMQR
QRinput_newMQR.restype = POINTER(QRinput)
QRinput_newMQR.argtypes = [c_int, QRecLevel]
QRinput_append = _library.QRinput_append
QRinput_append.restype = c_int
QRinput_append.argtypes = [POINTER(QRinput), QRencodeMode, c_int, POINTER(c_ubyte)]
QRinput_appendECIheader = _library.QRinput_appendECIheader
QRinput_appendECIheader.restype = c_int
QRinput_appendECIheader.argtypes = [POINTER(QRinput), c_uint]
QRinput_getVersion = _library.QRinput_getVersion
QRinput_getVersion.restype = c_int
QRinput_getVersion.argtypes = [POINTER(QRinput)]
QRinput_setVersion = _library.QRinput_setVersion
QRinput_setVersion.restype = c_int
QRinput_setVersion.argtypes = [POINTER(QRinput), c_int]
QRinput_getErrorCorrectionLevel = _library.QRinput_getErrorCorrectionLevel
QRinput_getErrorCorrectionLevel.restype = QRecLevel
QRinput_getErrorCorrectionLevel.argtypes = [POINTER(QRinput)]
QRinput_setErrorCorrectionLevel = _library.QRinput_setErrorCorrectionLevel
QRinput_setErrorCorrectionLevel.restype = c_int
QRinput_setErrorCorrectionLevel.argtypes = [POINTER(QRinput), QRecLevel]
QRinput_setVersionAndErrorCorrectionLevel = _library.QRinput_setVersionAndErrorCorrectionLevel
QRinput_setVersionAndErrorCorrectionLevel.restype = c_int
QRinput_setVersionAndErrorCorrectionLevel.argtypes = [POINTER(QRinput), c_int, QRecLevel]
QRinput_free = _library.QRinput_free
QRinput_free.restype = None
QRinput_free.argtypes = [POINTER(QRinput)]
QRinput_check = _library.QRinput_check
QRinput_check.restype = c_int
QRinput_check.argtypes = [QRencodeMode, c_int, POINTER(c_ubyte)]
class _QRinput_Struct(Structure):
    pass
QRinput_Struct = _QRinput_Struct
_QRinput_Struct._fields_ = [
]
QRinput_Struct_new = _library.QRinput_Struct_new
QRinput_Struct_new.restype = POINTER(QRinput_Struct)
QRinput_Struct_new.argtypes = []
QRinput_Struct_setParity = _library.QRinput_Struct_setParity
QRinput_Struct_setParity.restype = None
QRinput_Struct_setParity.argtypes = [POINTER(QRinput_Struct), c_ubyte]
QRinput_Struct_appendInput = _library.QRinput_Struct_appendInput
QRinput_Struct_appendInput.restype = c_int
QRinput_Struct_appendInput.argtypes = [POINTER(QRinput_Struct), POINTER(QRinput)]
QRinput_Struct_free = _library.QRinput_Struct_free
QRinput_Struct_free.restype = None
QRinput_Struct_free.argtypes = [POINTER(QRinput_Struct)]
QRinput_splitQRinputToStruct = _library.QRinput_splitQRinputToStruct
QRinput_splitQRinputToStruct.restype = POINTER(QRinput_Struct)
QRinput_splitQRinputToStruct.argtypes = [POINTER(QRinput)]
QRinput_Struct_insertStructuredAppendHeaders = _library.QRinput_Struct_insertStructuredAppendHeaders
QRinput_Struct_insertStructuredAppendHeaders.restype = c_int
QRinput_Struct_insertStructuredAppendHeaders.argtypes = [POINTER(QRinput_Struct)]
QRinput_setFNC1First = _library.QRinput_setFNC1First
QRinput_setFNC1First.restype = c_int
QRinput_setFNC1First.argtypes = [POINTER(QRinput)]
QRinput_setFNC1Second = _library.QRinput_setFNC1Second
QRinput_setFNC1Second.restype = c_int
QRinput_setFNC1Second.argtypes = [POINTER(QRinput), c_ubyte]
class QRcode(Structure):
    pass
QRcode._fields_ = [
    ('version', c_int),
    ('width', c_int),
    ('data', POINTER(c_ubyte)),
]
class _QRcode_List(Structure):
    pass
QRcode_List = _QRcode_List
_QRcode_List._fields_ = [
    ('code', POINTER(QRcode)),
    ('next', POINTER(QRcode_List)),
]
QRcode_encodeInput = _library.QRcode_encodeInput
QRcode_encodeInput.restype = POINTER(QRcode)
QRcode_encodeInput.argtypes = [POINTER(QRinput)]
QRcode_encodeString = _library.QRcode_encodeString
QRcode_encodeString.restype = POINTER(QRcode)
QRcode_encodeString.argtypes = [c_char_p, c_int, QRecLevel, QRencodeMode, c_int]
QRcode_encodeString8bit = _library.QRcode_encodeString8bit
QRcode_encodeString8bit.restype = POINTER(QRcode)
QRcode_encodeString8bit.argtypes = [c_char_p, c_int, QRecLevel]
QRcode_encodeStringMQR = _library.QRcode_encodeStringMQR
QRcode_encodeStringMQR.restype = POINTER(QRcode)
QRcode_encodeStringMQR.argtypes = [c_char_p, c_int, QRecLevel, QRencodeMode, c_int]
QRcode_encodeString8bitMQR = _library.QRcode_encodeString8bitMQR
QRcode_encodeString8bitMQR.restype = POINTER(QRcode)
QRcode_encodeString8bitMQR.argtypes = [c_char_p, c_int, QRecLevel]
QRcode_encodeData = _library.QRcode_encodeData
QRcode_encodeData.restype = POINTER(QRcode)
QRcode_encodeData.argtypes = [c_int, POINTER(c_ubyte), c_int, QRecLevel]
QRcode_encodeDataMQR = _library.QRcode_encodeDataMQR
QRcode_encodeDataMQR.restype = POINTER(QRcode)
QRcode_encodeDataMQR.argtypes = [c_int, POINTER(c_ubyte), c_int, QRecLevel]
QRcode_free = _library.QRcode_free
QRcode_free.restype = None
QRcode_free.argtypes = [POINTER(QRcode)]
QRcode_encodeInputStructured = _library.QRcode_encodeInputStructured
QRcode_encodeInputStructured.restype = POINTER(QRcode_List)
QRcode_encodeInputStructured.argtypes = [POINTER(QRinput_Struct)]
QRcode_encodeStringStructured = _library.QRcode_encodeStringStructured
QRcode_encodeStringStructured.restype = POINTER(QRcode_List)
QRcode_encodeStringStructured.argtypes = [c_char_p, c_int, QRecLevel, QRencodeMode, c_int]
QRcode_encodeString8bitStructured = _library.QRcode_encodeString8bitStructured
QRcode_encodeString8bitStructured.restype = POINTER(QRcode_List)
QRcode_encodeString8bitStructured.argtypes = [c_char_p, c_int, QRecLevel]
QRcode_encodeDataStructured = _library.QRcode_encodeDataStructured
QRcode_encodeDataStructured.restype = POINTER(QRcode_List)
QRcode_encodeDataStructured.argtypes = [c_int, POINTER(c_ubyte), c_int, QRecLevel]
QRcode_List_size = _library.QRcode_List_size
QRcode_List_size.restype = c_int
QRcode_List_size.argtypes = [POINTER(QRcode_List)]
QRcode_List_free = _library.QRcode_List_free
QRcode_List_free.restype = None
QRcode_List_free.argtypes = [POINTER(QRcode_List)]
QRcode_APIVersion = _library.QRcode_APIVersion
QRcode_APIVersion.restype = None
QRcode_APIVersion.argtypes = [POINTER(c_int), POINTER(c_int), POINTER(c_int)]
QRcode_APIVersionString = _library.QRcode_APIVersionString
QRcode_APIVersionString.restype = c_char_p
QRcode_APIVersionString.argtypes = []
QRcode_clearCache = _library.QRcode_clearCache
QRcode_clearCache.restype = None
QRcode_clearCache.argtypes = []
MQRSPEC_VERSION_MAX = 4 # Variable c_int '4'
QRSPEC_VERSION_MAX = 40 # Variable c_int '40'
__all__ = ['QRcode_clearCache', 'QRinput_setFNC1Second',
           'QRcode_List_size', 'QRinput_append', 'QRcode_List',
           'QR_MODE_8', 'QR_MODE_KANJI', 'QRcode_encodeStringMQR',
           'QR_MODE_FNC1FIRST', '_QRcode_List',
           'QRcode_encodeString8bit', 'QRcode', 'QRcode_encodeString',
           'QR_MODE_ECI', 'QRcode_encodeString8bitMQR', 'QR_MODE_NUL',
           'QR_MODE_NUM', 'QRcode_encodeString8bitStructured',
           'QR_ECLEVEL_Q', 'QRcode_encodeInputStructured',
           'QRinput_splitQRinputToStruct', 'QRinput_Struct',
           'QRinput_getVersion', 'QRcode_List_free',
           'QRcode_encodeDataMQR', 'QRinput_Struct_setParity',
           'QRinput_setVersion', 'QRinput_setErrorCorrectionLevel',
           'QRcode_encodeStringStructured', 'QRinput_check',
           'QRinput_Struct_free', 'QRinput_Struct_new',
           'QR_ECLEVEL_M', 'QR_ECLEVEL_L', 'QRcode_APIVersion',
           'QR_MODE_STRUCTURE', 'QRinput_appendECIheader',
           'QR_MODE_FNC1SECOND',
           'QRinput_Struct_insertStructuredAppendHeaders',
           'QRcode_encodeData', 'QRinput', 'QRinput_new2',
           'QRSPEC_VERSION_MAX', 'QRecLevel', '_QRinput',
           'QRcode_encodeInput', 'QRinput_getErrorCorrectionLevel',
           'QRcode_encodeDataStructured', 'QRencodeMode',
           'MQRSPEC_VERSION_MAX', '_QRinput_Struct', 'QRinput_free',
           'QRinput_setVersionAndErrorCorrectionLevel',
           'QRinput_Struct_appendInput', 'QR_MODE_AN',
           'QRcode_APIVersionString', 'QRinput_newMQR', 'QRinput_new',
           'QRcode_free', 'QR_ECLEVEL_H', 'QRinput_setFNC1First']
