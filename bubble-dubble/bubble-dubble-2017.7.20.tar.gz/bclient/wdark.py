#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtCore, QtWidgets
from .ui.wdark import Ui_WDark
from . import pyqt2bool


class WDark(QtWidgets.QDialog, Ui_WDark):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.setupUi(self)
        self.loadSettings()
        self.params = {'darkSample': '', 'darkBackground': '', 'flood': '', 'spline': '', 'incidence': False}

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WDark/Geometry', self.saveGeometry())
        s.setValue('WDark/folder', self.folder)
        s.setValue('WDark/spline', self.splineLineEdit.text())
        s.setValue('WDark/flood', self.floodLineEdit.text())
        s.setValue('WDark/darkbkg', self.bkgLineEdit.text())
        s.setValue('WDark/darksample', self.sampleLineEdit.text())
        s.setValue('WDark/incidence', self.incidenceCheckBox.isChecked())

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WDark/Geometry', QtCore.QByteArray()))
        self.folder = str(s.value('WDark/folder', ''))
        self.splineLineEdit.setText(str(s.value('WDark/spline', '')))
        self.floodLineEdit.setText(str(s.value('WDark/flood', '')))
        self.sampleLineEdit.setText(str(s.value('WDark/darkbkg', '')))
        self.bkgLineEdit.setText(str(s.value('WDark/darksample', '')))
        self.incidenceCheckBox.setChecked(pyqt2bool(s.value('WDark/incidence', False)))
        self.on_okButton_clicked()

    def closeEvent(self, event):
        self.saveSettings()

    @QtCore.pyqtSlot()
    def on_okButton_clicked(self):
        self.params = {
            'darkSample': [s.strip() for s in str(self.sampleLineEdit.text()).split(';') if s],
            'darkBackground': [s.strip() for s in str(self.bkgLineEdit.text()).split(';') if s],
            'flood': str(self.floodLineEdit.text()),
            'spline': str(self.splineLineEdit.text()),
            'incidence': self.incidenceCheckBox.isChecked(),
        }
        self.close()

    @QtCore.pyqtSlot()
    def on_cancelButton_clicked(self):
        self.bkgLineEdit.setText(';'.join(self.params['darkBackground']))
        self.sampleLineEdit.setText(';'.join(self.params['darkSample']))
        self.close()

    @QtCore.pyqtSlot()
    def on_bkgButton_clicked(self):
        self._openButton_clicked(self.bkgLineEdit, self._getFiles)

    @QtCore.pyqtSlot()
    def on_sampleButton_clicked(self):
        self._openButton_clicked(self.sampleLineEdit, self._getFiles)

    @QtCore.pyqtSlot()
    def on_floodButton_clicked(self):
        self._openButton_clicked(self.floodLineEdit, self._getFile)

    @QtCore.pyqtSlot()
    def on_splineButton_clicked(self):
        self._openButton_clicked(self.splineLineEdit, self._getFile, 'Spline file (*.spline)')

    def _getFile(self, lineEdit, current, mask):
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        files = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', current, mask)[0]
        if files:
            lineEdit.setText(files)
            self.folder = os.path.dirname(files)

    def _getFiles(self, lineEdit, current, mask):
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        files = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select files', current, mask)[0]
        if files:
            lineEdit.setText(';'.join(files))
            self.folder = os.path.dirname(files[0].split(';')[0])

    def _openButton_clicked(self, lineEdit, func, mask='EDF Images (*.edf)'):
        current = lineEdit.text()
        if current:
            current = os.path.dirname(current.split(';')[0])
        else:
            current = self.folder
        func(lineEdit, current, mask)

    @QtCore.pyqtSlot(name='on_bkgClearButton_clicked')
    @QtCore.pyqtSlot(name='on_sampleClearButton_clicked')
    @QtCore.pyqtSlot(name='on_floodClearButton_clicked')
    @QtCore.pyqtSlot(name='on_splineClearButton_clicked')
    def _clearButton_clicked(self):
        self._parent.clearButton_clicked(self)
