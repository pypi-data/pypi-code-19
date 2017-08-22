#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import isfile

from PIL.Image import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QCursor, QColor, QFont, QPainter, QImage
from PyQt5.QtWidgets import QFileDialog, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget
from mtb.qtWidgets.Button import Button

__all__ = ["infoView", "ImageComp"]


class infoView(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.w = 0
        self.h = 0
        self.setStyleSheet("background-color:red")

    def paintEvent(self, event):
        # Get the widget current size
        self.w = self.size().width()
        self.h = self.size().height()

        qp = QPainter()
        qp.begin(self)
        self.drawBackground(event.rect(), qp)
        qp.end()

    def drawBackground(self, rect, qp):
        col = QColor()
        col.setNamedColor('#d4d4d4')
        qp.setPen(col)
        qp.setRenderHint(QPainter.Antialiasing, True)
        rectA = QRect(rect.x(), rect.y(), rect.width(), rect.height())
        qp.setBrush(QColor(0, 0, 200))
        qp.drawRect(rectA)


class ImageComp(QWidget):
    def __init__(self, ctrls=True):
        QWidget.__init__(self)

        self.setStyleSheet("background-color:red")
        self.text = "Image Comparaison\n(widget)"

        self.percent = 50

        self.A = None
        self.B = None

        self.debug = False

        if ctrls:
            self.info = infoView()

            self.bA = Button("A")
            self.bm = Button("-")
            self.bB = Button("B")
            bD = Button("D")
            bS = Button("S")

            self.bA.amount = 100
            self.bm.amount = 50
            self.bB.amount = 0

            self.bA.leftClick.connect(self.ABswitch)
            self.bm.leftClick.connect(self.ABswitch)
            self.bB.leftClick.connect(self.ABswitch)

            bD.leftClick.connect(self.debugSwitch)
            bS.leftClick.connect(self.imageSwitch)

            self.bA.rightClick.connect(self.loadA)
            self.bB.rightClick.connect(self.loadB)

            self.bA.shiftClick.connect(self.imageSwitch)

            self.mlayout = QVBoxLayout()

            self.layout = QVBoxLayout()
            self.layout.addWidget(self.info)
            self.layout.addWidget(self.bA)
            self.layout.addWidget(self.bm)
            self.layout.addWidget(self.bB)
            self.layout.addWidget(bD)
            self.layout.addWidget(bS)

            spacerItem = QSpacerItem(20, 85, QSizePolicy.Maximum,
                                     QSizePolicy.Expanding)
            self.layout.addItem(spacerItem)
            self.layout.setContentsMargins(0, 0, 0, 0)

            self.mlayout.addLayout(self.layout)

            self.setLayout(self.mlayout)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

        self.setFocusPolicy(Qt.StrongFocus)

    def loadA(self):
        f, dummy = QFileDialog.getOpenFileName(None, "Open image file...")
        if f:
            self.A = f

    def loadB(self):
        f, dummy = QFileDialog.getOpenFileName(None, "Open image file...")
        if f:
            self.B = f

    def checkImage(self, image):
        if image:
            if type(image) == QImage or type(image) == ImageQt:
                return image
            elif type(image) == str:
                if isfile(image):
                    return QImage(image)
                else:
                    print("File does not exist")

            elif type(image) == Image:
                return ImageQt(image)
            else:
                print(type(image))
                raise TypeError
        else:
            return False

    @property
    def A(self):
        return self._A

    @A.setter
    def A(self, image):
        try:
            if image != self._A:

                isImage = self.checkImage(image)
                if isImage:

                    self._A = isImage
                    self.repaint()
                else:
                    self._A = None


        except:
            self._A = None

    @property
    def B(self):
        return self._B

    @B.setter
    def B(self, image):

        try:
            if image != self._B:
                isImage = self.checkImage(image)
                if isImage:
                    self._B = isImage
                    self.repaint()

                elif self._B == self.A:
                    pass
                else:
                    self._B = self.A
                    self.repaint()
        except:
            self._B = None

    @property
    def mouse(self):
        relX = self.width() / 100 * self.percent
        return relX

    @property
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, p):

        if p > 98:
            self._percent = 100
        if p < 0:
            self._percent = 0
        else:
            self._percent = p

        self.repaint()

    def flush(self):

        self.A = None
        self.B = None

    def debugSwitch(self):
        if self.debug == False:
            self.debug = True
            try:
                self.sender().cOn = "red"
                self.sender().styleOn()
            except:
                pass
        else:
            self.debug = False
            try:
                self.sender().styleOff()
            except:
                pass
        self.repaint()

    def imageSwitch(self):
        im1 = self.B
        self.B = self.A
        self.A = im1

    def ABswitch(self, amount=None):
        if amount is not None:
            self.percent = amount

        elif self.sender():

            self.percent = self.sender().amount

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)
        self.drawBackground(event.rect(), qp)
        qp.end()

        # Centers the widget
        if self.parent():
            self.move(self.parent().width() / 2 - self.width() / 2, 0)

    def drawDebug(self, qp):

        pImg = self.A.scaled(self.width(), self.height(), Qt.KeepAspectRatio)

        # DRAW DEBUG
        qp.setPen(QColor(255, 255, 255))
        qp.setFont(QFont('Akkurat-Mono', 14))

        fullText = self.text + "\n"
        fullText += "absolute: " + str(QCursor.pos().x())
        fullText += "\n"
        fullText += "relative: " + str(self.mouse)
        fullText += "\n"
        fullText += "percent: " + str(self.percent) + "%"
        fullText += "\n"
        fullText += "image:" + str(pImg.size())

        fullText += "\n"
        fullText += str(self.width()) + "x" + str(self.height())

        rect = QRect(0, 0, self.width(), self.height())
        qp.drawText(rect, Qt.AlignCenter, fullText)
        qp.setPen(QColor(0, 0, 0, 0))

    def drawBackground(self, rect, qp):

        col = QColor(0, 0, 0, 0)
        qp.setPen(col)
        qp.setRenderHint(QPainter.Antialiasing, True)

        # Setup Image Rects:
        rectA = QRect(0, 0, self.mouse, self.height())
        rectB = QRect(self.mouse, 0, self.width() - self.mouse + 1, self.height())

        if self.A:

            pImg = self.A.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding)

            # Cropping Image
            pImg = pImg.copy(rectA)
            qp.drawImage(0, 0, pImg)

        else:
            qp.setBrush(QColor(0, 0, 200))
            qp.drawRect(rectA)

        qp.setBrush(QColor(200, 0, 0, 125))

        if self.B:
            pImg = self.B.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding)
            # CROPPING IMAGE
            pImg = pImg.copy(rectB)
            qp.drawImage(self.mouse, 0, pImg)

        else:
            qp.drawRect(rectB)

        if self.debug:
            if self.A:
                self.drawDebug(qp)

    # EVENTS
    def sizeHint(self):
        return QSize(400, 600)

    def wheelEvent(self, event):
        a = event.angleDelta().y() / 120 * 10
        self.percent += a

    def resizeEvent(self, event):
        # maintaining aspect ratio.
        if self.A:
            new_size = QSize(self.A.size().width(), self.A.size().height())
            new_size.scale(event.size(), Qt.KeepAspectRatioByExpanding)
            self.resize(new_size)

    def keyPressEvent(self, event):
        # A/B/M/D/S
        modifiers = event.modifiers()

        # A
        if event.key() == 65:
            if modifiers == Qt.ShiftModifier:
                self.loadA()
            else:
                self.ABswitch(100)
        # B
        if event.key() == 66:
            if modifiers == Qt.ShiftModifier:
                self.loadB()
            else:
                self.ABswitch(0)
        # M
        if event.key() == 77:
            self.ABswitch(50)
        # D
        if event.key() == 68:
            self.debugSwitch()
        # S
        if event.key() == 83:
            self.imageSwitch()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            relCursor = self.mapFromGlobal(QCursor.pos())
            self.percent = round(relCursor.x() / self.width() * 100)
