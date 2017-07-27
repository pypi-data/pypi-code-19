#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg
from .. import utils
from ..utils import pyqt2bool as _
from .ui.ui_wlakeshore import Ui_WLakeshore
from .ui.ui_lakeshore_sensors import Ui_widgetSensors
from .ui.ui_lakeshore_widget import Ui_widgetSettings


class WLakeshore(QtWidgets.QDialog, Ui_WLakeshore):
    sigClosed = QtCore.pyqtSignal()
    sigConnect = QtCore.pyqtSignal(str, int)
    sigDisconnect = QtCore.pyqtSignal()
    sigReadSensor = QtCore.pyqtSignal(str, bool)
    sigReadOutput = QtCore.pyqtSignal(int, bool)
    sigSetPID = QtCore.pyqtSignal(int, str)
    sigSetRange = QtCore.pyqtSignal(int, int)
    sigSetManual = QtCore.pyqtSignal(int, float)
    sigSetPoint = QtCore.pyqtSignal(int, float)
    sigStoreSensor = QtCore.pyqtSignal(str)
    sigCreateSeqAction = QtCore.pyqtSignal(dict, object, bool)
    sigShowSeqAction = QtCore.pyqtSignal(dict, object)
    HeaterRange = 'Off', 'Low', 'Medium', 'High'

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.store = 'A'
        self.sensor = {}
        self.holdTemp = 0
        self.signalOnHold = None
        self.tempError = utils.DEFAULT_ERROR
        self.setUI()
        self.connectSignals()
        self.stopButton.hide()

    def setUI(self):
        self.setupUi(self)
        self.out1 = LakeshoreSettings(1)
        self.out2 = LakeshoreSettings(2)
        self.sensors = LakeshoreSensors()
        layout1 = QtWidgets.QVBoxLayout()
        layout1.addWidget(self.out1)
        layout1.addWidget(self.out2)
        widget1 = QtWidgets.QWidget()
        widget1.setLayout(layout1)
        layout2 = QtWidgets.QVBoxLayout()
        layout2.addWidget(widget1)
        layout2.addWidget(self.sensors)
        layout2.addStretch(0)
        widget2 = QtWidgets.QWidget()
        widget2.setLayout(layout2)
        self.plot = pg.PlotWidget()
        self.plot.plotItem.addLegend()
        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(widget2)
        self.splitter.addWidget(self.plot)
        layout3 = QtWidgets.QVBoxLayout()
        layout3.addWidget(self.splitter)
        self.tabStatus.setLayout(layout3)
        self.editTempError.setValidator(QtGui.QDoubleValidator())
        self.groupStoreSensor.setId(self.radioA, 0)
        self.groupStoreSensor.setId(self.radioB, 1)
        self.groupStoreSensor.setId(self.radioC, 2)
        self.groupStoreSensor.setId(self.radioD, 3)
        self.editTimeout.setValidator(QtGui.QIntValidator())

    def connectSignals(self):
        self.sigShowSeqAction.connect(self.showSeqAction)
        self.sensors.checkBoxA.toggled.connect(lambda _: self.sigReadSensor.emit('A', _))
        self.sensors.checkBoxB.toggled.connect(lambda _: self.sigReadSensor.emit('B', _))
        self.sensors.checkBoxC.toggled.connect(lambda _: self.sigReadSensor.emit('C', _))
        self.sensors.checkBoxD.toggled.connect(lambda _: self.sigReadSensor.emit('D', _))
        self.out1.checkBoxOutput.toggled.connect(lambda _: self.sigReadOutput.emit(1, _))
        self.out2.checkBoxOutput.toggled.connect(lambda _: self.sigReadOutput.emit(2, _))
        self.out1.buttonPID.clicked.connect(lambda: self.sigSetPID.emit(1, self.out1.editPID.text()))
        self.out2.buttonPID.clicked.connect(lambda: self.sigSetPID.emit(2, self.out2.editPID.text()))
        self.out1.buttonRange.clicked.connect(lambda: self.sigSetRange.emit(1, self.out1.comboRange.currentIndex()))
        self.out2.buttonRange.clicked.connect(lambda: self.sigSetRange.emit(2, self.out2.comboRange.currentIndex()))
        self.out1.buttonManual.clicked.connect(lambda: self.sigSetManual.emit(1, self.out1.spinManual.value()))
        self.out2.buttonManual.clicked.connect(lambda: self.sigSetManual.emit(2, self.out2.spinManual.value()))
        self.out1.buttonSetpoint.clicked.connect(lambda: self.sigSetPoint.emit(1, self.out1.spinSetpoint.value()))
        self.out2.buttonSetpoint.clicked.connect(lambda: self.sigSetPoint.emit(2, self.out2.spinSetpoint.value()))
        self.sigReadSensor.connect(self.setSensor)
        self.out1.buttonMacroManual.clicked.connect(lambda: self.setScriptManual(1, self.out1.spinManual.value()))
        self.out2.buttonMacroManual.clicked.connect(lambda: self.setScriptManual(2, self.out1.spinManual.value()))
        self.out1.buttonMacroPID.clicked.connect(lambda: self.setScriptPID(1, *self.out1.getPID()))
        self.out2.buttonMacroPID.clicked.connect(lambda: self.setScriptPID(2, *self.out2.getPID()))
        self.out1.buttonMacroRange.clicked.connect(lambda: self.setScriptRange(1, self.out1.comboRange.currentIndex()))
        self.out2.buttonMacroRange.clicked.connect(lambda: self.setScriptRange(2, self.out2.comboRange.currentIndex()))
        self.out1.buttonMacroSetpoint.clicked.connect(lambda: self.setScriptSetpoint(1, self.out1.spinSetpoint.value()))
        self.out2.buttonMacroSetpoint.clicked.connect(lambda: self.setScriptSetpoint(2, self.out2.spinSetpoint.value()))
        self.sigStoreSensor.connect(self.setStoreSensor)

    def setSensor(self, sensor, read):
        self.on_clearButton_clicked()
        if read:
            self.sensor[sensor] = {'c': color.color, 'v': []}
            self.updateTemperature(legend=sensor)
        else:
            if sensor in self.sensor:
                del self.sensor[sensor]
                self.plot.plotItem.legend.removeItem(sensor)

    def closeEvent(self, event):
        self.hide()
        self.on_stopButton_clicked()
        self.saveSettings()
        self.sigClosed.emit()

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WLakeshore/Geometry', self.saveGeometry())
        s.setValue('WLakeshore/SplitterGeometry', self.splitter.saveGeometry())
        s.setValue('WLakeshore/SplitterState', self.splitter.saveState())
        s.setValue('WLakeshore/address', self.editAddress.text())
        s.setValue('WLakeshore/temperror', self.editTempError.text())
        s.setValue('WLakeshore/timeout', self.editTimeout.text())
        s.setValue('WLakeshore/storeSensor', self.groupStoreSensor.checkedId())
        self.out1.saveSettings()
        self.out2.saveSettings()
        self.sensors.saveSettings()

    def loadSettings(self):
        s = QtCore.QSettings()
        qba = QtCore.QByteArray()
        self.restoreGeometry(s.value('WLakeshore/Geometry', qba))
        self.splitter.restoreGeometry(s.value('WLakeshore/SplitterGeometry', qba))
        self.splitter.restoreState(s.value('WLakeshore/SplitterState', qba))
        self.editAddress.setText(s.value('WLakeshore/address', 'host:7777'))
        self.editTimeout.setText(s.value('WLakeshore/timeout', str(utils.DEFAULT_TIMEOUT)))
        self.editTempError.setText(s.value('WLakeshore/temperror', f'{self.tempError}'))
        checkedButton = self.groupStoreSensor.button(int(s.value('WLakeshore/storeSensor', '0')))
        checkedButton.setChecked(True)
        self.sigStoreSensor.emit(checkedButton.text().strip('&'))
        self.sensors.loadSettings()
        self.out1.loadSettings()
        self.out2.loadSettings()

    @QtCore.pyqtSlot(QtWidgets.QAbstractButton)
    def on_groupStoreSensor_buttonClicked(self, button):
        self.sigStoreSensor.emit(button.text().strip('&'))

    def setStoreSensor(self, sensor):
        self.storeSensor = sensor

    def updateTemperature(self, sensor=None, value=None, legend=None):
        if sensor is not None and value is not None:
            self.sensors.setValue(sensor, value)
        if sensor in self.sensor and value is not None:
            self.sensor[sensor]['v'].append(value)
        if self.sensor:
            self.plot.plotItem.clear()
            for s in self.sensor:
                item = self.plot.plotItem.plot(self.sensor[s]['v'], pen=self.sensor[s]['c'])
                if legend == s:
                    self.plot.plotItem.legend.addItem(item, s)
        if self.signalOnHold and value and self.storeSensor == sensor and abs(self.holdTemp - value) <= self.tempError:
            signal = self.signalOnHold
            self.signalOnHold = None
            signal.emit()

    @QtCore.pyqtSlot(str)
    def on_editTempError_textChanged(self, text):
        try:
            self.tempError = float(text)
        except ValueError:
            pass

    def updateHeater(self, output, value, setter=False):
        {1: self.out1.setHeater, 2: self.out2.setHeater}[output](value, setter)

    def updateRange(self, output, value, setter=False):
        {1: self.out1.setRange, 2: self.out2.setRange}[output](value, setter)

    def updatePID(self, output, p, i, d, setter=False):
        {1: self.out1.setPID, 2: self.out2.setPID}[output](p, i, d, setter)

    def updateSetpoint(self, output, value, setter=False):
        {1: self.out1.setSetP, 2: self.out2.setSetP}[output](value, setter)

    @QtCore.pyqtSlot()
    def on_startButton_clicked(self):
        address = self.editAddress.text()
        try:
            host, port = address.split(':')
            port = int(port)
        except (ValueError, IndexError):
            self.lakeshoreError('Lakeshore is incorrect. It should be in the form host:port')
        else:
            self.connected()
            self.sigConnect.emit(host, port)

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        self.disconnected()
        self.sigDisconnect.emit()

    def connected(self):
        self.startButton.hide()
        self.stopButton.show()

    def disconnected(self):
        self.stopButton.hide()
        self.startButton.show()

    @QtCore.pyqtSlot()
    def on_clearButton_clicked(self):
        for s in self.sensor:
            self.sensor[s]['v'] = []
        self.plot.plotItem.clear()

    def setSignalOnHold(self, action, signal):
        if signal:
            self.lakeshoreAction = action
            try:
                timeout = int(self.editTimeout.text())
            except ValueError:
                timeout = utils.DEFAULT_TIMEOUT
            QtCore.QTimer.singleShot(timeout, lambda: setattr(self, 'signalOnHold', signal))

    def lakeshoreError(self, msg):
        QtWidgets.QMessageBox.critical(self, 'Lakeshore error', msg)
        self.on_stopButton_clicked()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            pass
        else:
            super().keyPressEvent(event)

    def showSeqAction(self, action, signal):
        for out in action:
            p = {}
            for value in action[out].values():
                key, val = value.split('=')
                p[key] = float(val)
            output = int(p['output'])
            if 'PID' in out:
                self.updatePID(output, p['p'], p['i'], p['d'], True)
                button = getattr(self, f'out{output:d}').buttonPID
            elif 'manual' in out:
                self.updateHeater(output, p['value'], True)
                button = getattr(self, f'out{output:d}').buttonManual
            elif 'point' in out:
                self.updateSetpoint(output, p['value'], True)
                button = getattr(self, f'out{output:d}').buttonSetpoint
                self.holdTemp = p['value']
            elif 'range' in out:
                self.updateRange(output, int(p['value']), True)
                button = getattr(self, f'out{output:d}').buttonRange
            else:
                return
            if signal:
                button.click()
                signal.emit()

    def setScriptPID(self, output, p, i, d, now=False):
        d = {
            f'Set PID of output {output} to {p:.0f} {i:.0f} {d:.0f}':
                {
                    f'Output: {output:d}': f'output={output:d}',
                    f'P: {p:.0f}': f'p={p:.0f}',
                    f'I: {i:.0f}': f'i={i:.0f}',
                    f'D: {d:.0f}': f'd={d:.0f}',
                },
        }
        self.sigCreateSeqAction.emit(d, self.sigShowSeqAction, now)

    def setScriptManual(self, output, value, now=False):
        d = {
            f'Set heater {output} manual output to {value:.2f}':
                {
                    f'Output: {output:d}': f'output={output:d}',
                    f'Value: {value:.2f}': f'value={value:.2f}',
                },
        }
        self.sigCreateSeqAction.emit(d, self.sigShowSeqAction, now)

    def setScriptRange(self, output, value, now=False):
        d = {
            f'Set heater {output} range to {value:d}':
                {
                    f'Output: {output:d}': f'output={output:d}',
                    f'Value: {value:d}': f'value={value:d}',
                },
        }
        self.sigCreateSeqAction.emit(d, self.sigShowSeqAction, now)

    def setScriptSetpoint(self, output, value, now=False):
        d = {
            f'Set setpoint of output {output} to {value:.2f}':
                {
                    f'Output: {output:d}': f'output={output:d}',
                    f'Value: {value:.2f}': f'value={value:.2f}',
                },
        }
        self.sigCreateSeqAction.emit(d, self.sigShowSeqAction, now)


class LakeshoreSettings(QtWidgets.QWidget, Ui_widgetSettings):
    def __init__(self, num):
        super().__init__()
        self.num = num
        self.widgets = (QtWidgets.QLabel, QtWidgets.QPushButton, QtWidgets.QAbstractSpinBox,
                        QtWidgets.QComboBox, QtWidgets.QLineEdit)
        self.setupUi(self)
        self.checkBoxOutput.setText(f'Output {self.num}')
        self.editPID.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('^[\d ]*$')))
        self.on_checkBoxOutput_toggled(False)

    def loadSettings(self):
        s = QtCore.QSettings()
        self.checkBoxOutput.setChecked(_(s.value(f'WLakeshoreSettings{self.num}/checked', 'false')))
        self.editPID.setText(s.value(f'WLakeshoreSettings{self.num}/PID', '150 20 0'))
        self.comboRange.setCurrentIndex(int(s.value(f'WLakeshoreSettings{self.num}/range', '0')))
        self.spinManual.setValue(float(s.value(f'WLakeshoreSettings{self.num}/manual', '0')))
        self.spinSetpoint.setValue(float(s.value(f'WLakeshoreSettings{self.num}/setpoint', '300')))

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue(f'WLakeshoreSettings{self.num}/checked', self.checkBoxOutput.isChecked())
        s.setValue(f'WLakeshoreSettings{self.num}/PID', self.editPID.text())
        s.setValue(f'WLakeshoreSettings{self.num}/range', self.comboRange.currentIndex())
        s.setValue(f'WLakeshoreSettings{self.num}/manual', self.spinManual.value())
        s.setValue(f'WLakeshoreSettings{self.num}/setpoint', self.spinSetpoint.value())

    @QtCore.pyqtSlot(bool)
    def on_checkBoxOutput_toggled(self, checked):
        for widget in self.__dict__.values():
            if isinstance(widget, self.widgets):
                widget.setEnabled(checked)

    def setHeater(self, value, setter):
        if setter:
            self.spinManual.setValue(value)
        else:
            self.labelHeater.setText(f'Heater: {value:.2f} %')

    def setRange(self, value, setter):
        if setter:
            self.comboRange.setCurrentIndex(value)
        else:
            self.labelRange.setText(f'Range: {WLakeshore.HeaterRange[value]}')

    def setPID(self, p, i, d, setter):
        if setter:
            self.editPID.setText(f'{p:.0f} {i:.0f} {d:.0f}')
        else:
            self.labelPID.setText(f'PID: {p:.0f} {i:.0f} {d:.0f}')

    def setSetP(self, value, setter):
        if setter:
            self.spinSetpoint.setValue(value)
        else:
            self.labelSetpoint.setText(f'Setpoint: {value:.2f} K')

    def getPID(self):
        return [float(i) for i in self.editPID.text().split()]


class LakeshoreSensors(QtWidgets.QWidget, Ui_widgetSensors):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def loadSettings(self):
        s = QtCore.QSettings()
        self.checkBoxA.setChecked(_(s.value('WLakeshoreSensors/checkedA', 'false')))
        self.checkBoxB.setChecked(_(s.value('WLakeshoreSensors/checkedB', 'false')))
        self.checkBoxC.setChecked(_(s.value('WLakeshoreSensors/checkedC', 'false')))
        self.checkBoxD.setChecked(_(s.value('WLakeshoreSensors/checkedD', 'false')))

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WLakeshoreSensors/checkedA', self.checkBoxA.isChecked())
        s.setValue('WLakeshoreSensors/checkedB', self.checkBoxB.isChecked())
        s.setValue('WLakeshoreSensors/checkedC', self.checkBoxC.isChecked())
        s.setValue('WLakeshoreSensors/checkedD', self.checkBoxD.isChecked())

    def setValue(self, sensor, value):
        name = f'label{sensor}'
        if name in self.__dict__:
            label = self.__dict__[name]
            label.setText(f'{value:3.2f} K')


class Color:
    def __init__(self):
        self._colors = 'g', 'r', 'c', 'm', 'y', 'w', 'b'
        self._cur = 0

    @property
    def color(self):
        c = self._colors[self._cur]
        self._cur += 1
        if self._cur >= len(self._colors):
            self._cur = 0
        return c


color = Color()
