#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import aspic
from ..controller.config import Config


class Monitor(QtCore.QObject):
    sigConnected = QtCore.pyqtSignal(str)
    sigValue = QtCore.pyqtSignal(int)
    sigError = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.ready = False
        self.countTime = 0
        self.running = False
        self.oldConnection = ''
        self.sec = None
        self.mon = None
        self.mult = 1
        self.timescan = 0
        self.secName = 'sec'
        self.measTime = 0
        self.userTime = 0

    def run(self, countTime):
        self.userTime = countTime
        if self.timescan:
            self.countTime = self.timescan
        elif self.measTime:
            self.countTime = self.measTime
        else:
            self.countTime = countTime
        self.running = True
        self.count()

    def abort(self):
        self.running = False

    def setConfig(self):
        self.mult = float(Config.MonitorMult) if Config.MonitorMult else 1
        self.timescan = float(Config.Timescan) if Config.Timescan else 0
        self.secName = Config.MonSecName
        self.measTime = float(Config.MonMeasTime) if Config.MonMeasTime else 0
        if self.oldConnection and self.oldConnection != Config.MonitorSpec:
            self.connectToSpec()

    def connectToSpec(self):
        if Config.MonitorSpec and self.secName:
            self.oldConnection = Config.MonitorSpec
            host, spec, counter = Config.MonitorSpec.split(':')
            self.sec = aspic.Qounter((host, spec), self.secName)
            self.mon = aspic.Qounter((host, spec), counter)
            self.sec.sigValueChanged.connect(self.monChanged)
            self.mon.sigValueChanged.connect(self.monChanged)
            self.mon.sigConnected.connect(self.sigConnected.emit)
            self.mon.sigError.connect(self.sigError.emit)
        else:
            self.running = False
            self.sec = None
            self.mon = None

    def monChanged(self, name, counts):
        if self.running and self.secName:
            if name == self.secName and counts >= self.countTime:
                self.ready = True
            elif name == self.mon.name() and self.ready:
                self.ready = False
                counts *= self.mult
                if self.measTime and not self.timescan:
                    counts *= self.userTime / self.measTime
                self.sigValue.emit(int(counts))
                self.count()

    def count(self):
        if self.timescan:
            return
        if self.running and self.sec and self.sec.isConnected() and self.mon and self.mon.isConnected():
            self.mon.count(self.countTime)
