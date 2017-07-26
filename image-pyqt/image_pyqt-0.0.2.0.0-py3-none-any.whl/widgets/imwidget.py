#!/usr/bin/python3
# Created by ausk@github.com
# 2017.06.26 20:53:47 CST

__all__ = ["MyImageWidget", "MyRawImageItem"]

from .. import myQt

from ..myQt import mkQApp, runQApp, mkARGB, mkQImage, MatToQImage
from ..myQt import QtGui, QtWidgets, QtCore

## 不能这样写 ??!
#from myQt import QtWidgets
#from QtWidgets import qApp, QMainWindow, QWidget, QFileDialog, QGraphicsScene, QGraphicsPixmapItem


import time, sys
import numpy as np

class MyRawImageItem(QtWidgets.QWidget):
    sigMouseMoved = QtCore.pyqtSignal(object)
    sigMouseClicked = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding))
        self.opts = None
        self.image = None
        self.qimage = None
        self.pixmap = None

        self.clickEvents = []
        self.dragButtons = []
        self.dragItem = None
        self.lastDrag = None
        self.mouseEnabled = False
        #print("hasMouseTracking(): {}".format(self.hasMouseTracking()))
        self.setMouseTracking(True)

        self.menu = None
        self.removable = True

    def quitApp(self):
        print("quitApp()")
        qApp.quit()

    def setImage(self, mat=None, *args, **kwargs):
        """
        img must be ndarray of shape (x,y), (x,y,3), or (x,y,4).
        """
        print("setImage start!")
        #print(*args,**kwargs)
        self.opts = (mat, args, kwargs)
        if mat is None or self.opts is None:
            return
        if isinstance(mat, np.ndarray):
            self.image = self.opts[0]
            argb, alpha = mkARGB(self.opts[0], *self.opts[1], **self.opts[2])
            self.qimage = mkQImage(argb, alpha)
            self.opts = ()
        elif isinstance(mat, QtGui.QImage):
            self.qimage = mat
            self.opts = ()
        else:
            print("Cannot set Image!")

        print("(w,h)=({},{})".format(self.qimage.width(),self.qimage.height()))
        self.pixmap = QtGui.QPixmap.fromImage(self.qimage)

        print("setImage end!")
        self.setUpdatesEnabled(True)
        self.update()
        #self.repaint()

    def getImage(self):
        return self.image

    def paintEvent(self, ev):
        print("paintEvent()")
        if self.pixmap is None:
            return

        #self.resize(self.qimage.width(),self.qimage.height())
        #print("Image Rect({},{},{},{})".format(self.rect().x(),self.rect().y(),self.rect().width(),self.rect().height() ))

        p = QtGui.QPainter(self)
        p.drawPixmap(self.rect(), self.pixmap)
        p.end()

    def enableMouse(self, b=True):
        self.mouseEnabled = b

    def mouseMoveEvent(self, ev):
        ## TODO: show or hide!
        # print("mouseMoveEvent()+: pos={}, x={}, y={}".format(ev.pos(),ev.x(),ev.y()))
        self.sigMouseMoved.emit(ev.pos())  # event.pos()/scenePos()
        QtWidgets.QWidget.mouseMoveEvent(self, ev)
        if int(ev.buttons()) != 0:
            QtWidgets.QWidget.mouseMoveEvent(self, ev)
            #TODO: Just return
            pass

    def mouseReleaseEvent(self, ev):
        print("mouseReleaseEvent()")

    def mouseDoubleClickEvent(self, ev):
        print("mouseDoubleClickEvent()")


class MyImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MyImageWidget,self).__init__(parent)

        self.imgitem = MyRawImageItem(self)
        self.label = QtWidgets.QLabel(self)
        self.label.setStyleSheet("QLabel { background-color: black; color: gray; }")
        self.setWindowTitle("Widget with Label")
        #self.show()
        self.setMouseTracking(True)
        self.imgitem.sigMouseMoved.connect(self.updateStatus)
        self.menu = None

    def updateStatus(self,pos):
        #pos = QtCore.QPoint(pos)
        #print("Mainframe status: pos={}, x={}, y={}".format(pos,pos.x(),pos.y()))
        x,y = pos.x(), pos.y()
        info = "xy({},{});".format(x,y)
        if self.imgitem.image is not None:
            nbytes = self.imgitem.image.nbytes
            bgr = self.imgitem.image[y,x]
            shape = self.imgitem.image.shape
            dtype = self.imgitem.image.dtype.name
            h,w = self.imgitem.image.shape[:2]
            info += "bgr{};hwc{};{};{:.3f}M".format(bgr,shape,dtype,nbytes/1024/1024)
        ## TODO: show or hide!
        # print(info)
        self.label.setText(info)

    def setImage(self, mat=None):
        if mat is None :
            return

        if isinstance(mat,np.ndarray):
            h,w = mat.shape[:2]
            print("Image shape: {}".format(mat.shape))
            self.imgitem.setGeometry(0,0,w,h)
            self.imgitem.setImage(mat=mat)
        elif isinstance(mat,QtGui.QImage):
            h = mat.height()
            w = mat.width()
            self.imgitem.setGeometry(0,0,w,h)
            self.imgitem.setImage(mat)
        else:
            print("Cannot setImage() in MyImageWidget!")

        #self.label.setGeometry(0,h,w,30)
        self.label.resize(w,20)
        self.label.move(0,h)
        #self.label.setPixmap(QtGui.QPixmap("/home/auss/Pictures/test.png"))
        frmsz = (self.imgitem.size().width(),self.imgitem.size().height()+self.label.size().height())
        self.setGeometry(100, 100, frmsz[0], frmsz[1])
        self.move(100, 100)
        self.setFixedSize(frmsz[0], frmsz[1])

    def getImage(self):
        return self.imgitem.getImage()

    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QtCore.QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                recursive_set(child)
        QtWidgets.QWidget.setMouseTracking(self, flag)
        recursive_set(self)
        pass


_images = []
def run():
    title="Test MyImageWidget"
    qApp = mkQApp()
    if QtWidgets.QApplication.instance() is None:
        raise Exception("Must create an QApplication instance!")
    import cv2 ,os
    #imagename = os.path.abspath(os.path.join(os.path.dirname(__filename__),"../data/test.png"))
    imagename = "/home/auss/Pictures/test.png"
    img = cv2.imread(imagename)

    win = MyImageWidget()
    win.setImage(img)
    win.setWindowTitle(title)
    win.show()
    _images.append(win)

    runQApp()

if __name__ == "__main__":
    run()
