#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QStatusBar


class Status(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.timer = QTimer()

        self.original_message = ""

        self.on_timeout()

    def showMessage(self, message, msecs=0):
        super().showMessage(message, msecs)
        if "124" in self.styleSheet():
            self.original_message = message

    def showError(self, message, msecs=3000):

        if msecs == False:
            msecs = 3000
        self.setStyleSheet("background-color:rgb(230,53,65);color:white")
        self.timer.setInterval(msecs)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start()
        self.showMessage(message, msecs)

    def showSuccess(self, message, msecs=3000):

        if msecs == False:
            msecs = 3000
        self.setStyleSheet("background-color:rgb(154,204,75);color:white")
        self.timer.setInterval(msecs)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start()
        self.showMessage(message, msecs)

    def showWarning(self, message, msecs=3000):
        if msecs == False:
            msecs = 3000
        self.setStyleSheet("background-color:rgb(217,159,0);color:white")
        self.timer.setInterval(msecs)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start()
        self.showMessage(message, msecs)

    def on_timeout(self):
        self.setStyleSheet("background-color:rgb(124,124,124);color:white")
        self.timer.stop()
        self.showMessage(self.original_message)
