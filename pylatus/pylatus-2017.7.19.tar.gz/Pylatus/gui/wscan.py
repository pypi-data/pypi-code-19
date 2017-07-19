#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
import auxygen
from .ui.ui_wscan import Ui_WScan
from .gutils import GUtils
from ..controller.config import Config


class WScan(QtWidgets.QMainWindow, Ui_WScan):
    sigClosed = QtCore.pyqtSignal()
    sigRun = QtCore.pyqtSignal(dict)
    sigAbort = QtCore.pyqtSignal()
    sigMoveMotor = QtCore.pyqtSignal(str, float)
    sigUpdateMotorViews = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.currentMotor = ''
        self.motors = []
        self.setupUi(self)
        self.loadSettings()

    def showMotors(self):
        self.motors.sort()
        self.axisComboBox.clear()
        self.axisComboBox.addItems(self.motors)
        self.rootMode = False

    @auxygen.utils.split_motor_name
    def addMotor(self, name):
        if name not in self.motors:
            self.motors.append(name)
        self.showMotors()

    def addMotors(self, motors):
        for motor in motors:
            self.addMotor(motor)

    @auxygen.utils.split_motor_name
    def removeMotor(self, name):
        if name in self.motors:
            self.motors.remove(name)
        self.showMotors()

    def setConfig(self):
        self.filterSpinBox.setMaximum(int(Config.NumberOfFilters))

    def setupUi(self, win):
        Ui_WScan.setupUi(self, win)
        dock1 = QtWidgets.QDockWidget(self)
        dock1.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        dock1.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        dock1.setWidget(self.controlsGroupBox)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock1)
        dock2 = QtWidgets.QDockWidget(self)
        dock2.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        dock2.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        dock2.setWidget(self.plot)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock2)
        self.setCentralWidget(dock2)
        plotItem = self.plot.getPlotItem()

        def mouseMoved(evt):
            pos = evt[0]
            if plotItem.sceneBoundingRect().contains(pos):
                mousePoint = plotItem.vb.mapSceneToView(pos)
                self.xposLabel.setText(f'{mousePoint.x():.6f}')
                self.yposLabel.setText(f'{mousePoint.y():.6f}')

        self.proxy = pg.SignalProxy(plotItem.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

    def showEvent(self, event):
        self.axisComboBox.setDisabled(True)
        self.fromSpinBox.setDisabled(True)
        self.toSpinBox.setDisabled(True)
        self.stepSpinBox.setDisabled(True)
        self.exposureSpinBox.setDisabled(True)
        self.shotButton.setDisabled(True)
        self.stopButton.setDisabled(True)
        self.filterSpinBox.setDisabled(True)
        self.rootMode = False
        self.axisComboBox.setCurrentIndex(self.axisComboBox.findText('mirror4'))

    @QtCore.pyqtSlot()
    def on_rootButton_clicked(self):
        if not GUtils.askPass(self):
            return
        self.axisComboBox.setEnabled(True)
        self.fromSpinBox.setEnabled(True)
        self.toSpinBox.setEnabled(True)
        self.stepSpinBox.setEnabled(True)
        self.exposureSpinBox.setEnabled(True)
        self.shotButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.filterSpinBox.setEnabled(True)
        self.rootMode = True

    def closeEvent(self, event):
        self.on_stopButton_clicked()
        self.hide()
        self.saveSettings()
        self.sigClosed.emit()

    def saveSettings(self):
        s = Config.Settings
        s.setValue('WScan/Geometry', self.saveGeometry())
        s.setValue('WScan/from', self.fromSpinBox.value())
        s.setValue('WScan/to', self.toSpinBox.value())
        s.setValue('WScan/step', self.stepSpinBox.value())
        s.setValue('WScan/exposure', self.exposureSpinBox.value())
        s.setValue('WScan/filter', self.filterSpinBox.value())

    def loadSettings(self):
        s = Config.Settings
        self.restoreGeometry(s.value('WScan/Geometry', Config.QBA))
        self.fromSpinBox.setValue(float(s.value('WScan/from', 0)))
        self.toSpinBox.setValue(float(s.value('WScan/to', 0)))
        self.stepSpinBox.setValue(float(s.value('WScan/step', 0)))
        self.exposureSpinBox.setValue(float(s.value('WScan/exposure', 1)))
        self.filterSpinBox.setValue(int(s.value('WScan/filter', 7)))

    def startScan(self, params):
        self.x, self.y = [], []
        self.startButton.setDisabled(True)
        self.shotButton.setDisabled(True)
        self.stopButton.setEnabled(True)
        self.sigRun.emit(params)

    def scanFinished(self):
        self.startButton.setEnabled(True)
        self.shotButton.setEnabled(True)
        self.stopButton.setDisabled(True)

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        self.sigAbort.emit()

    @QtCore.pyqtSlot(str)
    def on_axisComboBox_currentIndexChanged(self, motor):
        if self.axisComboBox.currentIndex() > -1 and motor in self.motors:
            self.currentMotor = motor
            self.sigUpdateMotorViews.emit()

    @QtCore.pyqtSlot()
    def on_shotButton_clicked(self):
        pos = self.fromSpinBox.value()
        axis = self.axisComboBox.currentText()
        self.sigMoveMotor.emit(axis, pos)

    @QtCore.pyqtSlot()
    def on_startButton_clicked(self):
        if self.rootMode:
            params = {
                'axis': self.axisComboBox.currentText(),
                'expPeriod': self.exposureSpinBox.value(),
                'start': self.fromSpinBox.value(),
                'stop': self.toSpinBox.value(),
                'step': self.stepSpinBox.value(),
                'nfilter': self.filterSpinBox.value(),
                'auto': False,
            }
            self.startScan(params)
        else:
            self.startScan({})

    def plotCurve(self, x, y):
        self.plot.plot(x, y, pen='g', clear=True)

    def plotGauss(self, x, y, xc):
        text = pg.TextItem(html=f'<div style="text-align: center"><span style="color: #FF0; font-size: 16pt;">'
                                f'Xc = {xc:f}</span></div>', anchor=(-0.3, 1.3), border='w', fill=(0, 0, 255, 100))
        self.plot.addItem(text)
        text.setPos(xc, y.max())
        self.plot.plot(x, y, pen='r', clear=False)

    def updateMotorPosition(self, name, position):
        if name == self.currentMotor:
            self.currentPositionLabel.setText(f'{position:.5f}')
