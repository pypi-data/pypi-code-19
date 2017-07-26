#!/usr/bin/python3
# Created by ausk@github.com
# 2017.07.05 19:48:46 CST

import os, sys, re, time
import types
import numpy as np
import struct # ??

# 定义待导出的模块
#__all__ = ["qtlib","QT_LIB","PYQT5","PYSIDE2","isQObjectAlive","QtCore","QtGui","QtWidgets","QtSvg","MatToQImage","QImageToMat","mkARGB","mkQImage","mkQApp","runQApp"]

PYSIDE2 = 'PySide2'
PYQT5 = 'PyQt5'

qtlib = None
QT_LIB = os.getenv('QT_LIB')
#libOrder = [PYQT5, PYSIDE2]
libOrder = [PYSIDE2, PYQT5]

if QT_LIB is None:
    for lib in libOrder:
        if lib in sys.modules:
            QT_LIB = lib
            break

if QT_LIB is None:
    for lib in libOrder:
        try:
            __import__(lib)
            QT_LIB = lib
            break
        except ImportError:
            pass

if QT_LIB is None:
    raise Exception("Requires one of PySide2 or PyQt5.")

if QT_LIB == PYSIDE2:
    from PySide2 import QtGui, QtWidgets, QtCore, QtSvg #, QtOpenGL, QtTest
    import PySide2
    qtlib = PySide2
    try:
        import shiboken2
        isQObjectAlive = shiboken2.isValid
    except ImportError:
        def isQObjectAlive(obj):
            try:
                if hasattr(obj, 'parent'):
                    obj.parent()
                elif hasattr(obj, 'parentItem'):
                    obj.parentItem()
                else:
                    raise Exception("Cannot determine whether Qt object %s is still alive." % obj)
            except RuntimeError:
                return False
            else:
                return True

    VERSION_INFO = 'PySide2 ' + PySide2.__version__
    QtCore.pyqtProperty = QtCore.Property
    QtCore.pyqtSignal = QtCore.Signal
    QtCore.pyqtSlot = QtCore.Slot
    QtCore.QStringListModel = QtGui.QStringListModel

elif QT_LIB == PYQT5:

    from PyQt5 import QtGui, QtCore, QtWidgets,QtSvg, QtOpenGL, uic
    import PyQt5
    qtlib = PyQt5

    import sip
    def isQObjectAlive(obj):
        return not sip.isdeleted(obj)

    QtCore.Property = QtCore.pyqtProperty
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
    QtGui.QStringListModel = QtCore.QStringListModel

    VERSION_INFO = 'PyQt5 ' + QtCore.PYQT_VERSION_STR + ' Qt ' + QtCore.QT_VERSION_STR

else:
    raise ValueError("Invalid Qt lib '%s'" % QT_LIB)


## Make sure we have Qt >= 5.6
USE_PYSIDE2 = QT_LIB == PYSIDE2
USE_PYQT5 = QT_LIB == PYQT5
QtVersion = PySide2.QtCore.__version__ if QT_LIB == PYSIDE2 else QtCore.QT_VERSION_STR
print("Qt Version: {}".format(QtVersion))

def _checkQtVersion():
    versionReq = [5, 6]
    m = re.match(r'(\d+)\.(\d+).*', QtVersion)
    if m is not None and list(map(int, m.groups())) < versionReq:
        print(list(map(int, m.groups())))
        raise Exception('pyqtgraph requires Qt version >= %d.%d  (your version is %s)' % (versionReq[0], versionReq[1], QtVersion))

_checkQtVersion()


QAPP = None
def mkQApp():
    global QAPP
    instance = QtWidgets.QApplication.instance()
    if instance is None:
        QAPP = QtWidgets.QApplication([])
    else:
        QAPP = instance
    return QAPP

def runQApp():
    global QAPP
    if QAPP and isQObjectAlive(QAPP):
        QAPP.exec_()

def mkARGB(data,flag="BGR2ARGB"):
    if data.ndim not in (2,3):
        raise TypeError("image must be 2D or 3D")
    if data.ndim == 3 and data.shape[2] >4:
        raise TypeError("image.shape[2] must __le__(4)")

    orders={
        "BGR2ARGB": [0, 1, 2, 3],
        "RGB2ARGB": [2, 1, 0, 3],
        "BGR2RGBA": [2, 1, 0, 3],
        "RGB2RGBA": [0, 1, 2, 3],
    }

    # RGBA <=> RGBA32， ARGB<=> ARGB32 <=> BGRA
    flags = ("BGR2ARGB", "RGB2ARGB", "BGR2RGBA", "RGB2RGBA")
    flag = flag if flag in flags else "BGR2ARGB"
    order = orders[flag]

    imgData = np.empty(data.shape[:2]+(4,),dtype=np.uint8)

    if data.ndim == 2:
        for i in range(3):
            imgData[...,i] = data
    elif data.shape[2] == 1:
        for i in range(3):
            imgData[...,i] = data[:,:,0]
    else:
        # for color image
        for i in range(0,data.shape[2]):
            imgData[...,i] = data[:,:,order[i]]

    if data.ndim == 2 or data.shape[2] == 3:
        alpha = False
        imgData[...,3] = 255
    else:
        alpha = True

    return imgData, alpha


def mkQImage(argb, alpha=None, trans=False):
    """
    Use the cpoied data of ARGB argb to make QImage and return it.
    argb:  (w,h,3 or 4)  this (bgr/rgb or bgra/rgba).
    alpha: ARGB32 if alpha is True else RGB32 (always be 4).
    trans: if trans is true then x/y axes are transposed.

    In default
    Qt: ARGB (32bpp), (width,height)

    """
    if alpha is None or not isinstance(alpha,bool):
        alpha = (argb.shape[2] == 4)

    if argb.shape[2] == 3:
        tmp = np.empty(argb.shape[:2] + (4,), dtype = argb.dtype)
        tmp[...,:3] = argb
        tmp[...,3] = 255
        argb = tmp

    if alpha:
        imgFormat = QtGui.QImage.Format_ARGB32
    else:
        imgFormat = QtGui.QImage.Format_RGB32

    if trans:
        # (y,x,c) => (x,y,c)
        argb = argb.transpose((1, 0, 2))

    addr = argb.data #addr = memoryview(argb)
    qimg = QtGui.QImage(addr,argb.shape[1],argb.shape[0],imgFormat)

    return qimg

def MatToQImage(mat,swapped=True):
    '''将numpy.ndarray转化为QtGui.QImage，然后化作QPixmap，并显示到QLabel控件上'''
    height, width = mat.shape[:2]
    dim = 1 if mat.ndim == 2 else mat.shape[2]
    bytesPerLine = dim * width
    # 将numpy.ndarray转化为QtGui.QImage，注意交换通道。
    qimage = QtGui.QImage(mat.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
    if swapped:
        qimage = qimage.rgbSwapped()
    return qimage
    #return QPixmap.fromImage(qimg)


def QImageToMat(qimg):
    """RGB888"""
    #qimg = QImage()
    #qimg.load("/home/auss/Pictures/test.png")
    qimg = qimg.convertToFormat(QImage.Format_RGB888)
    qimg = qimg.rgbSwapped()
    #assert(qimg.byteCount() == qimg.width() * qimg.height() * 3)

    ptr = qimg.constBits()
    ptr.setsize(qimg.byteCount())

    mat = np.array(ptr).reshape( qimg.height(), qimg.width(), 3)  #  Copies the data
    return mat


if __name__ == "__main__":
    print(__file__)


