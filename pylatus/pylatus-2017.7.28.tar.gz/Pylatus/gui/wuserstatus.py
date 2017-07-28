#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from .qmotordialog import QMotorDialog
from .ui.ui_wuserstatus import Ui_WUserStatus
from ..controller.config import Config


class WUserStatus(QMotorDialog, Ui_WUserStatus):
    sigShowRelativeWindow = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent, 'SpinBox')
        self.setupUi(self)
        self.filterSpinBox.setMinimumWidth(self.pldistdSpinBox.width())

    def closeEvent(self, event):
        self.hide()
        self.saveSettings()
        self.sigClosed.emit()

    def saveSettings(self):
        s = Config.Settings
        s.setValue('WUserStatus/Geometry', self.saveGeometry())

    def loadSettings(self):
        s = Config.Settings
        self.restoreGeometry(s.value('WUserStatus/Geometry', Config.QBA))

    @QtCore.pyqtSlot()
    def on_relativeButton_clicked(self):
        self.sigShowRelativeWindow.emit()

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        self.sigStopAllMotors.emit()

    def setKappa(self, isKappa):
        self.phiSpinBox.setEnabled(isKappa)
        self.kappaSpinBox.setEnabled(isKappa)
        self.omegaSpinBox.setEnabled(isKappa)
        self.prphiSpinBox.setDisabled(isKappa)

    def setOmegaPhi(self):
        self.setKappa(True)

    def setPrphi(self):
        self.setKappa(False)

    def setWavelength(self, wavelength, energy):
        self.energyLabel.setText(f'{energy:.5f}')
        self.waveLengthLabel.setText(f'{wavelength:.5f}')

    def showMonitor(self, counts):
        self.monitorLabel.setText(f'{counts:d}')
