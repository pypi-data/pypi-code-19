#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtNetwork
import auxygen
from ..controller.config import Config


class Pilatus(QtCore.QObject):
    sigScanStepReady = QtCore.pyqtSignal()
    sigExperimentFinished = QtCore.pyqtSignal()
    sigError = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.logger = auxygen.devices.logger.Logger('Dectris')
        self.scanCbfName = ''
        self.guiStarted = False
        self.createSocket()

    def setGuiStarted(self):
        self.guiStarted = True

    # noinspection PyUnresolvedReferences
    def createSocket(self):
        self.socket = QtNetwork.QTcpSocket(self)
        self.socket.setProxy(QtNetwork.QNetworkProxy(QtNetwork.QNetworkProxy.NoProxy))
        self.socket.connected.connect(self.sendFirstRequest)
        self.socket.readyRead.connect(self.readResponse)
        self.socket.disconnected.connect(self.serverHasStopped)
        self.socket.error.connect(self.serverHasError)

    def setConfig(self):
        self.separator = chr(int(Config.Separator)).encode('ascii')
        self.readout1 = float(Config.Readout1)
        self.readout2 = float(Config.Readout2)

    def connectDetector(self):
        self.stop()
        self.createSocket()
        host, port = Config.DetAddress.split(':')
        self.socket.connectToHost(host, int(port))

    def serverHasError(self):
        msg = self.socket.errorString()
        self.logger.error(f'Cannot connect to Pilatus. Message: {msg}')
        self.socket.disconnectFromHost()

    def send(self, cmd):
        if not self.guiStarted:
            return
        if self.isConnected():
            self.socket.write(f'{cmd}\n'.encode(encoding='ascii', errors='ignore'))
        else:
            self.sigError.emit('Pilatus error: detector is not connected, check camserver')

    def readResponse(self):
        data = self.socket.readAll()
        for s in bytes(data).split(self.separator):
            s = s.strip().decode(errors='ignore')
            if not s:
                continue
            self.logger.info(s)
            if self.scanCbfName and self.scanCbfName in s:
                self.scanCbfName = ''
                self.sigScanStepReady.emit()
            if '7 OK' in s:
                self.sigExperimentFinished.emit()

    def serverHasStopped(self):
        self.logger.warn('Dectris Pilatus server has been stopped')
        self.socket.close()

    def sendFirstRequest(self):
        self.send(f'Imgpath {Config.ServerDir}')
        self.logger.info('Connected to the Dectris Pilatus camera')
        self.emptyExposure()

    def abort(self):
        self.send('K')

    def stop(self):
        self.socket.close()

    def adjust(self, energy):
        self.setEnergy(energy)
        self.emptyExposure()

    def emptyExposure(self):
        self.initExperiment(0.1, 1)
        self.shot('_empty.cbf')

    def setEnergy(self, energy):
        self.send(f'SetEnergy {energy * 1e3}')

    def initExperiment(self, expPeriod, nframes, settings=''):
        readoutTime = self.readout2 if nframes > 1 and expPeriod > 15 else self.readout1
        self.send(f'ExpTime {expPeriod - readoutTime:f}')
        self.send(f'ExpPeriod {expPeriod:f}')
        self.send(f'NImages {nframes:d}')
        self.send(f'MXSettings {settings}')

    def exposure(self, cbfName):
        self.send(f'ExtMTrigger {cbfName}')

    def shot(self, cbfName):
        self.send(f'Exposure {cbfName}')

    def scanShot(self, cbfName=''):
        if cbfName:
            self.shot(cbfName)
        self.scanCbfName = cbfName

    def isConnected(self):
        return self.socket.state() == self.socket.ConnectedState
