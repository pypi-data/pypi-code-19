#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from PyQt5 import QtCore, QtGui, QtWidgets
from .ui.wsaxsparams import Ui_WSaxsParams


class WSaxsParams(QtWidgets.QDialog, Ui_WSaxsParams):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        validator = QtGui.QDoubleValidator()
        self.concentrationLineEdit.setValidator(validator)
        self.thicknessLineEdit.setValidator(validator)
        self.calibrationLineEdit.setValidator(validator)
        self.loadSettings()
        self.showEvent(None)

    @QtCore.pyqtSlot()
    def on_cancelButton_clicked(self):
        self.close()

    def closeEvent(self, event):
        self.saveSettings()

    def showEvent(self, event):
        self.concentrationLineEdit.setText(str(self.params['concentration']))
        self.thicknessLineEdit.setText(str(self.params['thickness']))
        self.calibrationLineEdit.setText(str(self.params['calibration']))

    @QtCore.pyqtSlot()
    def on_okButton_clicked(self):
        self.params = {
            'concentration': float(self.concentrationLineEdit.text()),
            'thickness': float(self.thicknessLineEdit.text()),
            'calibration': float(self.calibrationLineEdit.text()),
        }
        self.close()

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WSaxsParams/Geometry', self.saveGeometry())
        s.setValue('WSaxsParams/params', json.dumps(self.params))

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WSaxsParams/Geometry', QtCore.QByteArray()))
        params = s.value('WSaxsParams/params', '')
        if params:
            self.params = json.loads(params)
        else:
            self.params = {
                'concentration': 0,
                'thickness': 1,
                'calibration': 1e6,
            }
