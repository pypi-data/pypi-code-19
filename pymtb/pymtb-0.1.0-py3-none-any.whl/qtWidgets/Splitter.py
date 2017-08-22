#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtCore import Qt, pyqtSignal, QObject, QEvent, QPoint
from PyQt5.QtGui import QCursor

from PyQt5.QtWidgets import (QWidget, QFrame,
                             QSplitter, QApplication, QVBoxLayout, QGridLayout)
from mtb.qtWidgets.Button import Button
from mtb.utils import percentOf


def grabUI(widget):

    if type(widget) == SplitterView:


        class Filter(QObject):
            tabPressed = pyqtSignal(QWidget)

            def eventFilter(self, obj, event):

                if obj == widget:
                    if obj.mouseOver:
                        obj.grabKeyboard()
                    if event.type() == QEvent.KeyPress:

                        if event.key() == 16777217:
                                self.tabPressed.emit(obj)
                                return True

                return QWidget.eventFilter(self, obj, event)

        filter = Filter(widget)
        widget.installEventFilter(filter)
        return filter.tabPressed
    else:
        raise TypeError

class SplitterView(QWidget):


    def __init__(self, parent=None):
        super(SplitterView, self).__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)


        self.styleA = "background-color:red"
        self.styleB = "background-color:white"
        self.setStyleSheet(self.styleA)

        self.addSide = Button("+")
        self.addBottom = Button("+")

        self.addSide.setFixedSize(16, 16)
        self.addBottom.setFixedSize(16, 16)

        self.fframe = QFrame()
        # self.fframe.setFrameShape(QFrame.StyledPanel)

        layout.addWidget(self.fframe)
        layout.addWidget(self.addSide)
        layout.addWidget(self.addBottom)

        #self.grabKeyboard()
        #self.installEventFilter(self)

    @property
    def mouseOver(self):
        a =self.mapFromGlobal(QCursor.pos())

        if a.x() < 0 or a.x() > self.width() or a.y() < 0 or a.y() > self.height() :
            return False

        return a

    def resizeEvent(self, event):
        self.fitUi()



    def fitUi(self):
        self.addBottom.move(int(self.width() / 2), self.height() - 32)
        self.addSide.move(self.width() - 32, int(self.height() / 2))
        self.fframe.resize(self.width(), self.height())

    def switchStyle(self):

        print (self.styleSheet())
        if self.styleSheet() == self.styleA:
            self.setStyleSheet(self.styleB)

        elif self.styleSheet() == self.styleB:
            self.setStyleSheet(self.styleA)
        self.resize(self.width()+1,self.height()+1)



class Splitter(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.side = 0
        self.bottom = 0

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('mtb_splitter')

    def initUI(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setWindowFlags(Qt.FramelessWindowHint)

        # SPLITTERS
        self.row = QSplitter(Qt.Horizontal)
        self.col = QSplitter(Qt.Vertical)

        # splitter handle style
        self.row.setStyleSheet("QSplitter::handle {background-color: black;}")
        self.row.setHandleWidth(1)

        self.col.setStyleSheet("QSplitter::handle {background-color: black;}")
        self.col.setHandleWidth(1)

        self.offset = QPoint()
        # SPLIT VIEW
        a = self.newView()

        self.P = {
            "top":False,
            "bottom": False,
            "left": False,
            "right":False
        }

        self.row.addWidget(a)
        layout.addWidget(self.row, 0, 0)


    def tabPressed(self,view):
        view.switchStyle()

    def newView(self):
        # SPLIT VIEW
        a = SplitterView(self)



        a.addSide.leftClick.connect(self.newLeftSplitter)
        a.addBottom.leftClick.connect(self.newBottomSplitter)

        grabUI(a).connect(self.tabPressed)




        return a


    def newLeftSplitter(self):
        print("Creating a new splitter")

        a = self.newView()

        self.row.addWidget(a)

        self.side += 1




    def newBottomSplitter(self):


        if self.layout().count() == 1:
            print("Only the row layout is available")
            self.row.addWidget(self.col)


        a = self.newView()
        self.col.addWidget(a)

        self.bottom += 1

        # for w in range(0,self.layout().count()):
        #     print(self.layout().itemAt(w))

    @property
    def left(self):
        return self._left
    @property
    def right(self):
        return self._right
    @property
    def top(self):
        return self._top

    @property
    def bottom(self):
        return self._bottom


    @left.setter
    def left(self,l):
        self._left = l
        self._right = not l


    @right.setter
    def right(self,r):

        self._right = r
        self._left = not r


    @top.setter
    def top(self,t):
        self._top = t
        self._bottom = not t

    @bottom.setter
    def bottom(self,b):

        self._bottom = b
        self._top = not b



    @property
    def anchor(self):
        try:
            locx = percentOf(int(self.offsetP.x()),int(self.width()) )
            locy = percentOf(int(self.offsetP.y()),int(self.height()) )
            if locx > 50:
                self.right = True

            else:
                self.left = True

            if locy > 50:
                self.bottom = True

            else:
                self.top = True



            return (self.left,self.right,self.top,self.bottom)


        except:
            return False
        #return (a[0],a[1])

    def mousePressEvent(self, event):
        self.offsetP = event.pos()
        if event.buttons() & Qt.MidButton:
            self.offsetP = event.pos()
        if event.buttons() & Qt.RightButton:
            self.offsetS = QPoint(self.width(),self.height()) - event.pos()






    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MidButton:
            x = event.globalX()
            y = event.globalY()
            x_w = self.offsetP.x()
            y_w = self.offsetP.y()
            self.move(x - x_w, y - y_w)

        if event.buttons() & Qt.RightButton:

            #x = event.globalX()
            #y = event.globalY()
            xo = self.mapFromGlobal(event.globalPos())
            x = xo.x()
            y = xo.y()
            x_w = self.offsetS.x()
            y_w = self.offsetS.y()

            self.resize(x_w+x,y_w+y)

            t = self.anchor
            if t:
                mx = 0
                my = 0


                if self.top & self.left:
                    mx = self.rect().topRight()
                    print(mx.x(),mx.y())
                    #self.move(mx.x(),mx.y())

    def resizeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = Splitter()
    # ex = SplitterView()
    ex.show()
    sys.exit(app.exec_())
