#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget
from mtb.Image.image import mImage

__all__ = ["ImageViewer"]


class ImageViewer(QWidget):
    def __init__(self, img=None):
        QWidget.__init__(self)

        self.img = mImage(img)

    def setImage(self, im):

        self.img.path = im

    def paintEvent(self, event):

        # Get the widget current size
        qp = QPainter()
        qp.begin(self)
        self.drawBackground(event.rect(), qp)
        qp.end()

    def drawBackground(self, rect, qp):

        qp.setRenderHint(QPainter.Antialiasing, True)

        if self.img:
            pImg = self.img.qImage.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding)

            qp.drawImage(0, 0, pImg)

    def sizeHint(self):
        return QSize(800, 600)

    def resizeEvent(self, event):
        # maintaining aspect ratio.
        if self.img:
            try:
                new_size = QSize(self.img.pil.width, self.img.pil.height)
                new_size.scale(event.size(), Qt.KeepAspectRatio)
                self.resize(new_size)
            except:
                pass
