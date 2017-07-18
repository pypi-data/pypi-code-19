#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtGui, QtCore, QtWidgets
from .ui.wbubble import Ui_WBubble
from ..bcommon import default
from . import connector, pyqt2bool, wplot, wsaxsparams, wmask, wdark, wabout


class WBubble(QtWidgets.QDialog, Ui_WBubble):
    killServerSignal = QtCore.pyqtSignal()
    startServerSignal = QtCore.pyqtSignal(str, int)
    disconnectFromServerSignal = QtCore.pyqtSignal()
    runSignal = QtCore.pyqtSignal(dict, str)
    beamlineToggledSignal = QtCore.pyqtSignal(str)
    stopConnectorThread = QtCore.pyqtSignal()
    applyWaxsDarkSignal = QtCore.pyqtSignal()
    applySaxsDarkSignal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.multiplyLineEdit.setValidator(QtGui.QDoubleValidator())
        self.editNormMax.setValidator(QtGui.QDoubleValidator())
        self.editNormMin.setValidator(QtGui.QDoubleValidator())
        self.connectorThread = QtCore.QThread()
        self.connector = connector.Connector()
        self.connector.moveToThread(self.connectorThread)
        self.setVisibleWidgets()
        self.wabout = wabout.WAboutBubble()
        self.wSaxsMask = wmask.WMask(self.saxsMaskLineEdit, 'saxs', self)
        self.wWaxsMask = wmask.WMask(self.waxsMaskLineEdit, 'waxs', self)
        self.waxsPlot = wplot.WPlot('WAXS', self.waxsPlotButton, self)
        self.saxsPlot = wplot.WPlot('SAXS', self.saxsPlotButton, self)
        self.saxsPlot.plot1DView.setLogMode(x=True, y=True)
        self.wSaxsParams = wsaxsparams.WSaxsParams(self)
        self.wSaxsDark = wdark.WDark(self)
        self.wWaxsDark = wdark.WDark(self)
        self.connectSignals()
        self.loadSettings()
        self.connectorThread.start()
        self.startServerSignal.emit(self.hostLineEdit.text(), self.portSpinBox.value())
        self.saveFolder = ''

    def setVisibleWidgets(self):
        self.stopServerButton.hide()
        self.runServerButton.show()
        self.killServerButton.hide()
        self.stopWaxsButton.hide()
        self.stopSaxsButton.hide()

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.connector.serverStateSignal.connect(self.showServerState)
        self.connector.errorsSignal.connect(self.showServerErrors)
        self.connector.warningsSignal.connect(self.showServerWarnings)
        self.killServerSignal.connect(self.connector.killServer)
        self.connector.waxsStateSignal.connect(self.showWaxsState)
        self.connector.saxsStateSignal.connect(self.showSaxsState)
        self.connector.waxsPlotSignal.connect(self.waxsPlot.plot)
        self.connector.saxsPlotSignal.connect(self.saxsPlot.plot)
        self.runSignal.connect(self.connector.runSaxsWaxs)
        self.connectorThread.started.connect(self.connector.run)
        self.connectorThread.finished.connect(self.connector.disconnectFromServer)
        self.startServerSignal.connect(self.connector.tryServer)
        self.disconnectFromServerSignal.connect(self.connector.disconnectFromServer)
        self.beamlineToggledSignal.connect(self.wWaxsMask.changeBeamline)
        self.beamlineToggledSignal.connect(self.wSaxsMask.changeBeamline)
        self.beamlineToggledSignal.connect(self.connector.setBeamline)
        self.stopConnectorThread.connect(self.connector.stop)
        self.applySaxsDarkSignal.connect(self.wSaxsDark.on_okButton_clicked)
        self.applyWaxsDarkSignal.connect(self.wWaxsDark.on_okButton_clicked)

    def closeEvent(self, event):
        self.disconnectFromServerSignal.emit()
        self.stopConnectorThread.emit()
        self.waxsPlot.close()
        self.saxsPlot.close()
        self.wSaxsMask.close()
        self.wWaxsMask.close()
        self.saveSettings()
        self.connectorThread.wait()

    def saveSettings(self, s=None):
        s = s or QtCore.QSettings()
        s.setValue('WBubble/Geometry', self.saveGeometry())
        s.setValue('WBubble/host', self.hostLineEdit.text())
        s.setValue('WBubble/port', self.portSpinBox.value())
        s.setValue('WBubble/localServer', self.localCheckBox.isChecked())
        s.setValue('WBubble/speed', self.speedCheckBox.isChecked())
        s.setValue('WBubble/sspeed', self.sspeedCheckBox.isChecked())
        s.setValue('WBubble/waxspath', self.waxsDirLineEdit.text())
        s.setValue('WBubble/waxsPoniPath', self.waxsPoniLineEdit.text())
        s.setValue('WBubble/waxsBkgPath', self.waxsBkgLineEdit.text())
        s.setValue('WBubble/waxsBkgCoef', self.waxsBkgCoefSpinBox.value())
        s.setValue('WBubble/saxspath', self.saxsDirLineEdit.text())
        s.setValue('WBubble/saxsPoniPath', self.saxsPoniLineEdit.text())
        s.setValue('WBubble/saxsMaskPath', self.saxsMaskLineEdit.text())
        s.setValue('WBubble/waxsMaskPath', self.waxsMaskLineEdit.text())
        s.setValue('WBubble/saxsBkgPath', self.saxsBkgLineEdit.text())
        s.setValue('WBubble/saxsBkgCoef', self.saxsBkgCoefSpinBox.value())
        s.setValue('WBubble/saxsAziStart', self.saxsAziStartSpinBox.value())
        s.setValue('WBubble/saxsAziStop', self.saxsAziStopSpinBox.value())
        s.setValue('WBubble/multiply', self.multiplyLineEdit.text())
        s.setValue('WBubble/beamline', self.getBeamlineRadio())
        s.setValue('WBubble/outUnits', self.getUnitsRadio())
        s.setValue('WBubble/waxsNormalization', self.getNormalizationRadio())
        s.setValue('WBubble/extCheckbox', self.extCheckBox.isChecked())
        s.setValue('WBubble/saxsDetector', self.saxsDetectorComboBox.currentText())
        s.setValue('WBubble/waxsDetector', self.waxsDetectorComboBox.currentText())
        s.setValue('WBubble/subdirCheckbox', self.subdirCheckBox.isChecked())
        s.setValue('WBubble/ext', self.extEdit.text())
        s.setValue('WBubble/subdir', self.subdirEdit.text())
        s.setValue('WBubble/saveFolder', self.saveFolder)
        s.setValue('WBubble/multicolumn', self.multiCheckBox.isChecked())
        s.setValue('WBubble/multicolumnName', self.multiEdit.text())
        s.setValue('WBubble/saveEdf', self.edfCheckBox.isChecked())
        s.setValue('WBubble/waxsAzimuth', self.waxsAzimuthCheckBox.isChecked())
        s.setValue('WBubble/waxsAzimuthStart', self.waxsAziStartSpinBox.value())
        s.setValue('WBubble/waxsAzimuthStop', self.waxsAziStopSpinBox.value())
        s.setValue('WBubble/waxsAzimuthSlices', self.waxsSlicesCheckBox.isChecked())
        s.setValue('WBubble/saxsAzimuth', self.saxsAzimuthCheckBox.isChecked())
        s.setValue('WBubble/saxsAzimuthSlices', self.saxsSlicesCheckBox.isChecked())
        s.setValue('WBubble/waxsRadial', self.waxsRadialCheckBox.isChecked())
        s.setValue('WBubble/waxsRadialStart', self.waxsRadStartSpinBox.value())
        s.setValue('WBubble/waxsRadialStop', self.waxsRadStopSpinBox.value())
        s.setValue('WBubble/saxsRadialStart', self.saxsRadStartSpinBox.value())
        s.setValue('WBubble/saxsRadialStop', self.saxsRadStopSpinBox.value())
        s.setValue('WBubble/saxsRadial', self.saxsRadialCheckBox.isChecked())
        s.setValue('WBubble/page', self.tabWidget.currentIndex())

    def loadSettings(self, s=None):
        s = s or QtCore.QSettings()
        self.restoreGeometry(s.value('WBubble/Geometry', QtCore.QByteArray()))
        self.hostLineEdit.setText(str(s.value('WBubble/host', default.DEFAULT_HOST)))
        self.portSpinBox.setValue(int(s.value('WBubble/port', default.DEFAULT_PORT)))
        self.localCheckBox.setChecked(pyqt2bool(s.value('WBubble/localServer', False)))
        self.speedCheckBox.setChecked(pyqt2bool(s.value('WBubble/speed', False)))
        self.sspeedCheckBox.setChecked(False)
        self.on_speedCheckBox_toggled(self.speedCheckBox.isChecked())
        self.on_sspeedCheckBox_toggled(self.sspeedCheckBox.isChecked())
        self.sspeedCheckBox.setChecked(pyqt2bool(s.value('WBubble/sspeed', False)))
        self.waxsDirLineEdit.setText(str(s.value('WBubble/waxspath', '')))
        self.waxsPoniLineEdit.setText(str(s.value('WBubble/waxsPoniPath', '')))
        self.waxsBkgLineEdit.setText(str(s.value('WBubble/waxsBkgPath', '')))
        self.waxsBkgCoefSpinBox.setValue(float(s.value('WBubble/waxsBkgCoef', 0)))
        self.saxsDirLineEdit.setText(str(s.value('WBubble/saxspath', '')))
        self.saxsPoniLineEdit.setText(str(s.value('WBubble/saxsPoniPath', '')))
        self.saxsMaskLineEdit.setText(str(s.value('WBubble/saxsMaskPath', '')))
        self.waxsMaskLineEdit.setText(str(s.value('WBubble/waxsMaskPath', '')))
        self.saxsBkgLineEdit.setText(str(s.value('WBubble/saxsBkgPath', '')))
        self.saxsBkgCoefSpinBox.setValue(float(s.value('WBubble/saxsBkgCoef', 0)))
        self.saxsAziStartSpinBox.setValue(float(s.value('WBubble/saxsAziStart', 0)))
        self.saxsAziStopSpinBox.setValue(float(s.value('WBubble/saxsAziStop', 0)))
        self.multiplyLineEdit.setText(str(s.value('WBubble/multiply', '1')))
        beamline = s.value('WBubble/beamline', 'Dubble').replace('&', '')
        if beamline == 'SNBL':
            self.snblRadio.setChecked(True)
            self.on_snblRadio_toggled(True)
        elif beamline == 'Dubble':
            self.dubbleRadio.setChecked(True)
            self.on_dubbleRadio_toggled(True)
        norm = s.value('WBubble/waxsNormalization', 'Monitor')
        if norm == 'Background':
            self.radioNormBkg.setChecked(True)
        elif norm == 'Monitor':
            self.radioNormMon.setChecked(True)
        elif norm == 'None':
            self.radioNormNone.setChecked(True)
        det = s.value('WBubble/saxsDetector', 'Pilatus')
        self.saxsDetectorComboBox.setCurrentIndex(self.saxsDetectorComboBox.findText(det))
        self.on_saxsDetectorComboBox_currentIndexChanged(det)
        det = s.value('WBubble/waxsDetector', 'Pilatus')
        self.waxsDetectorComboBox.setCurrentIndex(self.waxsDetectorComboBox.findText(det))
        self.on_waxsDetectorComboBox_currentIndexChanged(det)
        outUnits = s.value('WBubble/outUnits', 'qRadio')
        if outUnits == 'tthRadio':
            self.tthRadio.setChecked(True)
        self.on_runSaxsButton_clicked(0)
        self.on_runWaxsButton_clicked(0)
        self.extCheckBox.setChecked(pyqt2bool(s.value('WBubble/extCheckbox', False)))
        self.subdirCheckBox.setChecked(pyqt2bool(s.value('WBubble/subdirCheckbox', False)))
        self.extEdit.setText(str(s.value('WBubble/ext')))
        self.subdirEdit.setText(str(s.value('WBubble/subdir')))
        self.saveFolder = str(s.value('WBubble/saveFolder'))
        multi = pyqt2bool(s.value('WBubble/multicolumn', False))
        self.multiCheckBox.setChecked(multi)
        self.on_multiCheckBox_toggled(multi)
        self.multiEdit.setText(str(s.value('WBubble/multicolumnName', default.MULTICOLUMN_NAME)))
        self.edfCheckBox.setChecked(pyqt2bool(s.value('WBubble/saveEdf', False)))
        self.waxsAziStartSpinBox.setValue(float(s.value('WBubble/waxsAzimuthStart', 0)))
        self.waxsAziStopSpinBox.setValue(float(s.value('WBubble/waxsAzimuthStop', 0)))
        self.waxsSlicesCheckBox.setChecked(pyqt2bool(s.value('WBubble/waxsAzimuthSlices', False)))
        self.saxsSlicesCheckBox.setChecked(pyqt2bool(s.value('WBubble/saxsAzimuthSlices', False)))
        self.saxsAzimuthCheckBox.setChecked(pyqt2bool(s.value('WBubble/saxsAzimuth', False)))
        self.saxsRadialCheckBox.setChecked(pyqt2bool(s.value('WBubble/saxsRadial', False)))
        self.waxsRadialCheckBox.setChecked(pyqt2bool(s.value('WBubble/waxsRadial', False)))
        self.waxsRadStartSpinBox.setValue(float(s.value('WBubble/waxsRadialStart', 0)))
        self.waxsRadStopSpinBox.setValue(float(s.value('WBubble/waxsRadialStop', 0)))
        self.saxsRadStartSpinBox.setValue(float(s.value('WBubble/saxsRadialStart', 0)))
        self.saxsRadStopSpinBox.setValue(float(s.value('WBubble/saxsRadialStop', 0)))
        self.tabWidget.setCurrentIndex(int(s.value('WBubble/page', 0)))

    @QtCore.pyqtSlot()
    def on_exitButton_clicked(self):
        self.close()

    def showServerState(self, status):
        if status['serverRunning']:
            self.serverLampLabel.setPixmap(QtGui.QPixmap(':/grnbtn'))
            self.serverStateLabel.setText(status['serverRunning'])
            self.tabWidget.setTabIcon(0, QtGui.QIcon(QtGui.QPixmap(':/grnbtn')))
            self.stopServerButton.show()
            self.runServerButton.hide()
            self.killServerButton.show()
        else:
            self.serverLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
            self.serverStateLabel.setText(status['serverRunning'])
            self.tabWidget.setTabIcon(0, QtGui.QIcon(QtGui.QPixmap(':/redbtn')))
            self.stopServerButton.hide()
            self.runServerButton.show()
            self.serverStateLabel.setText('Server is stopped')
            self.killServerButton.hide()

    def showWaxsState(self, status):
        running = status.get('running', False)
        if running:
            self.waxsLampLabel.setPixmap(QtGui.QPixmap(':/grnbtn'))
            self.tabWidget.setTabIcon(2, QtGui.QIcon(QtGui.QPixmap(':/grnbtn')))
            self.waxsStateLabel.setText('running on {}'.format(status.get('path', 'unknown')))
            self.runWaxsButton.hide()
            self.stopWaxsButton.show()
        else:
            self.waxsLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
            self.tabWidget.setTabIcon(2, QtGui.QIcon(QtGui.QPixmap(':/redbtn')))
            self.waxsStateLabel.setText('stopped')
            self.stopWaxsButton.hide()
            self.runWaxsButton.show()
        self.waxsLastfileLabel.setText(os.path.basename(status.get('imageFile', '')))
        self.waxsTotalLabel.setText('{} of {}'.format(status.get('total', 0), status.get('all', 0)))

    def showSaxsState(self, status):
        running = status.get('running', False)
        if running:
            self.saxsLampLabel.setPixmap(QtGui.QPixmap(':/grnbtn'))
            self.tabWidget.setTabIcon(1, QtGui.QIcon(QtGui.QPixmap(':/grnbtn')))
            self.saxsStateLabel.setText('running on {}'.format(status.get('path', 'unknown')))
            self.runSaxsButton.hide()
            self.stopSaxsButton.show()
        else:
            self.saxsLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
            self.tabWidget.setTabIcon(1, QtGui.QIcon(QtGui.QPixmap(':/redbtn')))
            self.saxsStateLabel.setText('stopped')
            self.stopSaxsButton.hide()
            self.runSaxsButton.show()
        self.saxsLastfileLabel.setText(os.path.basename(status.get('imageFile', '')))
        self.saxsTotalLabel.setText('{} of {}'.format(status.get('total', 0), status.get('all', 0)))

    def showServerErrors(self, errors):
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        QtWidgets.QMessageBox.critical(self, 'Server errors', errors)

    def showServerWarnings(self, warnings):
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        QtWidgets.QMessageBox.warning(self, 'Server warnings', warnings)

    @QtCore.pyqtSlot(bool)
    def on_localCheckBox_toggled(self, checked):
        if checked:
            self.hostLineEdit.setDisabled(True)
            self.portSpinBox.setDisabled(True)
            self.runServerButton.setText('Start server')
            self.stopServerButton.setText('Stop server')
        else:
            self.hostLineEdit.setEnabled(True)
            self.portSpinBox.setEnabled(True)
            self.runServerButton.setText('Connect')
            self.stopServerButton.setText('Disconnect')

    @QtCore.pyqtSlot()
    def on_stopServerButton_clicked(self):
        if self.localCheckBox.isChecked():
            pass
        else:
            self.stopServerButton.hide()
            self.runServerButton.show()
            self.killServerButton.hide()
            self.serverLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
            self.serverStateLabel.setText('Disconnected from the server')
            self.disconnectFromServerSignal.emit()

    @QtCore.pyqtSlot()
    def on_runServerButton_clicked(self):
        self.runServerButton.hide()
        self.runServerButton.show()
        self.startServerSignal.emit(self.hostLineEdit.text(), self.portSpinBox.value())

    @QtCore.pyqtSlot()
    def on_killServerButton_clicked(self):
        self.killServerSignal.emit()

    def getBeamlineRadio(self):
        return self.getRadio('Dubble', (self.dubbleRadio, self.snblRadio))

    def getNormalizationRadio(self):
        return self.getRadio('Monitor', (self.radioNormNone, self.radioNormBkg, self.radioNormMon))

    def getUnitsRadio(self):
        return self.getRadio('q', (self.qRadio, self.tthRadio), False)

    def getRadio(self, start, radios, text=True):
        value = start
        for radio in radios:
            if radio.isChecked():
                if text:
                    value = radio.text().replace('&', '')
                else:
                    value = radio.objectName()
                break
        return value

    def getCommonParams(self):
        return {'beamline': self.getBeamlineRadio(), 'units': self.getUnitsRadio()[0]}

    @QtCore.pyqtSlot()
    def on_runWaxsButton_clicked(self, run=1):
        path = self.waxsDirLineEdit.text()
        poniPath = self.waxsPoniLineEdit.text()
        ext = self.extEdit.text() if self.extCheckBox.isChecked() else ''
        subdir = self.subdirEdit.text() if self.subdirCheckBox.isChecked() else ''
        multi = ''
        if self.multiCheckBox.isChecked():
            name = self.multiEdit.text()
            multi = name if name else default.MULTICOLUMN_NAME
        if run and (not path or not poniPath):
            # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
            QtWidgets.QMessageBox.critical(self, 'WAXS Error', 'You have to set folder and poni file, at least.')
            return
        multiplier = self.multiplyLineEdit.text()
        radial = None
        if self.waxsRadialCheckBox.isChecked():
            radial = self.waxsRadStartSpinBox.value(), self.waxsRadStopSpinBox.value()

        norm = []
        for n in (self.editNormMin.text(), self.editNormMax.text()):
            try:
                norm.append(float(n))
            except ValueError:
                norm.append(0)

        params = {
            'path': path,
            'run': run,
            'poni': poniPath,
            'bkgCoef': self.waxsBkgCoefSpinBox.value(),
            'backgroundFiles': [s.strip() for s in self.waxsBkgLineEdit.text().split(';') if s],
            'maskFile': self.waxsMaskLineEdit.text(),
            'calibration': float(multiplier) if multiplier else 1,
            'ext': ext,
            'subdir': subdir,
            'multicolumnName': multi,
            'save': self.edfCheckBox.isChecked(),
            'detector': self.waxsDetectorComboBox.currentText(),
            'speed': self.speedCheckBox.isChecked(),
            'sspeed': self.sspeedCheckBox.isEnabled() and self.sspeedCheckBox.isChecked(),
            'azimuth': (self.waxsAziStartSpinBox.value(), self.waxsAziStopSpinBox.value()),
            'azimuthSlices': self.waxsSlicesCheckBox.isChecked(),
            'azimuthChecked': self.waxsAzimuthCheckBox.isChecked(),
            'radial': radial,
            'normalization': self.getNormalizationRadio(),
            'normrange': norm,
        }
        params.update(self.getCommonParams())
        params.update(self.wWaxsDark.params)
        self.runSignal.emit(params, 'waxs')

    @QtCore.pyqtSlot()
    def on_runSaxsButton_clicked(self, run=1):
        path = self.saxsDirLineEdit.text()
        poniPath = self.saxsPoniLineEdit.text()
        ext = str(self.extEdit.text()) if self.extCheckBox.isChecked() else ''
        subdir = str(self.subdirEdit.text()) if self.subdirCheckBox.isChecked() else ''
        multi = ''
        if self.multiCheckBox.isChecked():
            name = str(self.multiEdit.text())
            multi = name if name else default.MULTICOLUMN_NAME
        if run and (not path or not poniPath):
            # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
            QtWidgets.QMessageBox.critical(self, 'SAXS Error', 'You have to set folder and poni file, at least.')
            return
        radial = None
        if self.saxsRadialCheckBox.isChecked():
            radial = self.saxsRadStartSpinBox.value(), self.saxsRadStopSpinBox.value()
        params = {
            'path': path,
            'run': run,
            'poni': poniPath,
            'bkgCoef': self.saxsBkgCoefSpinBox.value(),
            'azimuth': (self.saxsAziStartSpinBox.value(), self.saxsAziStopSpinBox.value()),
            'maskFile': str(self.saxsMaskLineEdit.text()),
            'backgroundFiles': [s.strip() for s in str(self.saxsBkgLineEdit.text()).split(';') if s],
            'ext': ext,
            'subdir': subdir,
            'multicolumnName': multi,
            'save': self.edfCheckBox.isChecked(),
            'detector': self.saxsDetectorComboBox.currentText(),
            'speed': self.speedCheckBox.isChecked(),
            'sspeed': self.sspeedCheckBox.isEnabled() and self.sspeedCheckBox.isChecked(),
            'azimuthSlices': self.saxsSlicesCheckBox.isChecked(),
            'azimuthChecked': self.saxsAzimuthCheckBox.isChecked(),
            'radial': radial,
            'normalization': 'Monitor',
            'normrange': (None, None),
        }
        params.update(self.getCommonParams())
        params.update(self.wSaxsParams.params)
        params.update(self.wSaxsDark.params)
        self.runSignal.emit(params, 'saxs')

    @QtCore.pyqtSlot()
    def on_stopWaxsButton_clicked(self):
        self.runSignal.emit({'stop': 1}, 'waxs')

    @QtCore.pyqtSlot()
    def on_stopSaxsButton_clicked(self):
        self.runSignal.emit({'stop': 1}, 'saxs')

    @QtCore.pyqtSlot(bool)
    def on_waxsPlotButton_toggled(self, checked):
        self.waxsPlot.setVisible(checked)

    @QtCore.pyqtSlot(bool)
    def on_saxsPlotButton_toggled(self, checked):
        self.saxsPlot.setVisible(checked)

    @QtCore.pyqtSlot()
    def on_waxsFolderButton_clicked(self):
        self._folderButton_clicked(self.waxsDirLineEdit)

    @QtCore.pyqtSlot()
    def on_saxsFolderButton_clicked(self):
        self._folderButton_clicked(self.saxsDirLineEdit)

    def _folderButton_clicked(self, dirLineEdit):
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        d = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select folder', dirLineEdit.text())
        if d:
            dirLineEdit.setText(d)

    @QtCore.pyqtSlot()
    def on_waxsPoniButton_clicked(self):
        self._poniButton_clicked(self.waxsPoniLineEdit)

    @QtCore.pyqtSlot()
    def on_saxsPoniButton_clicked(self):
        self._poniButton_clicked(self.saxsPoniLineEdit)

    def _poniButton_clicked(self, poniLineEdit):
        currentPoni = poniLineEdit.text()
        if currentPoni:
            currentPoni = os.path.dirname(currentPoni)
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        poni = QtWidgets.QFileDialog.getOpenFileName(self, 'Select poni file', currentPoni, 'Poni (*.poni)')[0]
        if poni:
            poniLineEdit.setText(poni)

    @QtCore.pyqtSlot()
    def on_waxsBkgButton_clicked(self):
        self._bkgButton_clicked(self.waxsBkgLineEdit)

    @QtCore.pyqtSlot()
    def on_saxsBkgButton_clicked(self):
        self._bkgButton_clicked(self.saxsBkgLineEdit)

    def _bkgButton_clicked(self, bkgLineEdit):
        currentBkg = bkgLineEdit.text()
        if currentBkg:
            currentBkg = os.path.dirname(currentBkg.split(';')[0])
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        bkg = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select background files', currentBkg,
                                                     'Frames (*.edf *.cbf)')[0]
        if bkg:
            bkgLineEdit.setText(';'.join(bkg))

    @QtCore.pyqtSlot()
    def on_saxsMaskButton_clicked(self):
        self._maskButton_clicked(self.saxsMaskLineEdit)

    @QtCore.pyqtSlot()
    def on_waxsMaskButton_clicked(self):
        self._maskButton_clicked(self.waxsMaskLineEdit)

    def _maskButton_clicked(self, maskLineEdit):
        mask = maskLineEdit.text()
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        mask = QtWidgets.QFileDialog.getOpenFileName(self, 'Select mask file', mask,
                                                     'Masks (*.msk *.npz);;Fit2D mask (*.msk);;Bubble mask (*.npz)')[0]
        if mask:
            maskLineEdit.setText(mask)

    @QtCore.pyqtSlot()
    def on_advancedButton_clicked(self):
        self.wSaxsParams.show()

    def keyPressEvent(self, keyEvent):
        if keyEvent.key() != QtCore.Qt.Key_Escape:
            QtWidgets.QDialog.keyPressEvent(self, keyEvent)

    def on_snblRadio_toggled(self, checked):
        if checked:
            self.beamlineToggledSignal.emit('SNBL')
            self.tabWidget.setTabEnabled(1, False)

    def on_dubbleRadio_toggled(self, checked):
        if checked:
            self.beamlineToggledSignal.emit('Dubble')
            self.tabWidget.setTabEnabled(1, True)

    def on_radioNormBkg_toggled(self, checked):
        self.editNormMax.setEnabled(checked)
        self.editNormMin.setEnabled(checked)

    def on_extCheckBox_toggled(self, checked):
        self.extEdit.setEnabled(checked)

    @QtCore.pyqtSlot()
    def on_darkFilesButton_clicked(self):
        self.wSaxsDark.show()

    @QtCore.pyqtSlot()
    def on_waxsDarkFilesButton_clicked(self):
        self.wWaxsDark.show()

    def on_subdirCheckBox_toggled(self, checked):
        self.subdirEdit.setEnabled(checked)

    def on_multiCheckBox_toggled(self, checked):
        self.multiEdit.setEnabled(checked)

    @QtCore.pyqtSlot()
    def on_saveButton_clicked(self):
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        fn = QtWidgets.QFileDialog.getSaveFileName(self, 'Save window settings...', self.saveFolder,
                                                   'Bubble settings (*.bub)')[0]
        if fn:
            self.saveFolder = os.path.dirname(fn)
            self.saveSettings(QtCore.QSettings(fn, QtCore.QSettings.IniFormat))

    @QtCore.pyqtSlot(str)
    def on_saxsDetectorComboBox_currentIndexChanged(self, detector):
        self.darkFilesButton.setEnabled(detector == 'Frelon')
        self.applySaxsDarkSignal.emit()

    @QtCore.pyqtSlot(str)
    def on_waxsDetectorComboBox_currentIndexChanged(self, detector):
        self.waxsDarkFilesButton.setEnabled(detector == 'Frelon')
        self.applyWaxsDarkSignal.emit()

    # noinspection PyArgumentList
    @QtCore.pyqtSlot(name='on_saxsDirClearButton_clicked')
    @QtCore.pyqtSlot(name='on_saxsPoniClearButton_clicked')
    @QtCore.pyqtSlot(name='on_saxsMaskClearButton_clicked')
    @QtCore.pyqtSlot(name='on_saxsBkgClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsDirClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsPoniClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsMaskClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsBkgClearButton_clicked')
    def _clearButton_clicked(self):
        self.clearButton_clicked()

    @QtCore.pyqtSlot()
    def on_loadButton_clicked(self):
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        fn = QtWidgets.QFileDialog.getOpenFileName(self, 'Load window settings...', self.saveFolder,
                                                   'Bubble settings (*.bub)')[0]
        if fn:
            self.saveFolder = os.path.dirname(fn)
            self.loadSettings(QtCore.QSettings(fn, QtCore.QSettings.IniFormat))

    def clearButton_clicked(self, other=None):
        other = other or self
        # noinspection PyCallByClass
        button = QtCore.QObject.sender(other)
        bname = button.objectName()
        end = bname.find('ClearButton')
        other.__dict__['{0}LineEdit'.format(bname[:end])].setText('')

    @QtCore.pyqtSlot()
    def on_waxsMakeMaskButton_clicked(self):
        self.wWaxsMask.show()

    @QtCore.pyqtSlot()
    def on_saxsMakeMaskButton_clicked(self):
        self.wSaxsMask.show()

    def on_speedCheckBox_toggled(self, checked):
        self.sspeedCheckBox.setEnabled(checked)
        if not checked:
            self.sspeedCheckBox.setChecked(False)

    def on_sspeedCheckBox_toggled(self, checked):
        self.multiCheckBox.setEnabled(not checked)
        if not self.multiCheckBox.isEnabled():
            self.multiCheckBox.setChecked(False)

    @QtCore.pyqtSlot()
    def on_aboutButton_clicked(self):
        self.wabout.show()
