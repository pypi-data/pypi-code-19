#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QPushButton

__all__ = ["Button"]


class Button(QPushButton):
    """
    Simple button with custom signals

    Signals:
        leftClick
        rightClick
        shiftClick

    Args:
        label(str): The Button text label.
    """
    # creation du signal emetteur (emet rien pour le moment)
    leftClick = pyqtSignal()
    rightClick = pyqtSignal()

    shiftClick = pyqtSignal()

    def __init__(self, label):
        QPushButton.__init__(self, label)

        self.mainStyle = "font-family:Akkurat-Mono;color:white"
        self.setMinimumWidth(5)

        self.setFlat(True)
        self.amount = 0

        self.cOn = "cyan"
        self.cOff = "black"

        self.setStyleSheet(self.cOff)

    @property
    def cOn(self):
        return self._cOn

    @cOn.setter
    def cOn(self, color):
        self._cOn = "background-color:" + color + ";border:none;border-radius:5px;" + self.mainStyle

    @property
    def cOff(self):
        return self._cOff

    @cOff.setter
    def cOff(self, color):
        self._cOff = "background-color:" + color + ";border:none;border-radius:5px;" + self.mainStyle

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            if event.modifiers() != Qt.ShiftModifier:
                self.leftClick.emit()
                return

        if event.button() == Qt.RightButton:
            self.rightClick.emit()
            return

        if event.modifiers() == Qt.ShiftModifier:
            self.shiftClick.emit()
            return
