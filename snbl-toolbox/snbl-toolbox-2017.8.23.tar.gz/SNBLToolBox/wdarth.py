#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import glob
from PyQt5 import QtCore, QtGui, QtWidgets
from cryio import parparser, cbfimage
from crymon import reconstruct
from .ui.ui_wdarth import Ui_WDarth
from . import pyqt2bool


class WorkerSignals(QtCore.QObject):
    errorSignal = QtCore.pyqtSignal(str)
    progressSignal = QtCore.pyqtSignal(str)
    stopSignal = QtCore.pyqtSignal()
    finishedSignal = QtCore.pyqtSignal(object)
    nFilesSignal = QtCore.pyqtSignal(int)


class Worker(QtCore.QRunnable):
    def __init__(self, params):
        QtCore.QRunnable.__init__(self)
        self.stop = False
        folder = params['folder']
        self.folder = folder[:-1] if folder[-1] == '/' or folder[-1] == '\\' else folder
        self.params = params
        self.signals = WorkerSignals()
        self.signals.stopSignal.connect(self.stopIt)

    def stopIt(self):
        self.stop = True

    def parfile(self):
        self.par = parparser.ParParser(self.params['par'])

    def makeSlice(self):
        s = reconstruct.Slice()
        s.downsample = self.params['downsample']
        s.lorentz = self.params['lorentz']
        s.scale = self.params['scale']
        if 'layer' in self.params:
            l = self.params['layer']
            s.p0.h, s.p0.k, s.p0.l = [float(i) for i in l['hkl1'].split()]
            s.p1.h, s.p1.k, s.p1.l = [float(i) for i in l['hkl2'].split()]
            s.pc.h, s.pc.k, s.pc.l = [float(i) for i in l['center'].split()]
            s.qmax = float(l['qmax'])
            s.thickness = float(l['thickness'])
            self.reconst = reconstruct.Layer(self.par.parstruct, s)
        else:
            s.p0.h, s.p0.k, s.p0.l = 1, 0, 0
            s.p1.h, s.p1.k, s.p1.l = 0, 1, 0
            s.pc.h, s.pc.k, s.pc.l = 0, 0, 0
            s.dQ = self.params['dQ']
            s.x = self.params['x']
            s.y = self.params['y']
            s.z = self.params['z']
            self.reconst = reconstruct.Volume(self.par.parstruct, s)

    def makemap(self):
        for i, cbf in enumerate(self.cbflist, 1):
            if self.stop:
                break
            image = cbfimage.CbfImage(cbf)
            self.reconst.add(image.array, image.header['Start_angle'], image.header['Angle_increment'])
            self.signals.progressSignal.emit('Reading files')
        self.signals.progressSignal.emit('Calculating CCP4')
        if not self.stop:
            self.reconst.save(self.mapname)
        self.signals.progressSignal.emit('Finished')

    def genMapName(self):
        layer_dirs = os.path.join(self.folder, 'layers')
        try:
            os.mkdir(layer_dirs)
        except OSError:
            if not os.path.isdir(layer_dirs):
                self.stopIt()
                return
        if 'layer' in self.params:
            l = self.params['layer']
            fn = '{}__{}__{}__{}.cbf'.format(self.basename, l['hkl1'], l['hkl2'], l['center']).replace(' ', '_')
            self.mapname = os.path.join(layer_dirs, fn)
        else:
            fn = '{}.ccp4'.format(self.basename)
            self.mapname = os.path.join(layer_dirs, fn)

    def run(self):
        self.basename = os.path.basename(self.folder)
        self.genMapName()
        self.cbflist = glob.glob(os.path.join(self.folder, '*.cbf'))
        self.signals.nFilesSignal.emit(len(self.cbflist))
        self.cbflist.sort()
        self.parfile()
        self.makeSlice()
        self.makemap()
        self.stopIt()
        self.signals.finishedSignal.emit(self)


class WorkerPool(QtCore.QObject):
    progressSignal = QtCore.pyqtSignal(str, int)
    finishedSignal = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.pool = QtCore.QThreadPool.globalInstance()
        self.workers, self.errors = [], []

    def run(self, params):
        folder = params['folder']
        self.files = self.done = 0
        self.workers, self.errors = [], []
        for dirpath, dirnames, filenames in os.walk(folder):
            pars = glob.glob(os.path.join(dirpath, '*_cracker.par'))
            if not pars:
                continue
            layers = params.pop('layers')
            if params['volume']:
                p = params.copy()
                p['par'] = pars[0]
                p['folder'] = dirpath
                self.startWorker(p)
            for layer in layers:
                p = params.copy()
                p['par'] = pars[0]
                p['folder'] = dirpath
                p['layer'] = layer
                self.startWorker(p)

    def startWorker(self, p):
        worker = Worker(p)
        worker.signals.errorSignal.connect(self.workerError)
        worker.signals.progressSignal.connect(self.workerProgress)
        worker.signals.finishedSignal.connect(self.workerFinished)
        worker.signals.nFilesSignal.connect(self.addNFiles)
        self.workers.append(worker)
        self.pool.start(worker)

    def addNFiles(self, n):
        self.files += n

    def stopIt(self):
        for worker in self.workers:
            worker.signals.stopSignal.emit()

    def workerProgress(self, info):
        self.done += 1
        done = 100.0 * self.done / self.files
        self.progressSignal.emit(info, done)

    def workerError(self, folder):
        self.errors.append(folder)

    def workerFinished(self, worker):
        self.workers.remove(worker)
        if not self.workers:
            self.progressSignal.emit('Finished', 100)
            self.finishedSignal.emit(self.errors)


class WDarth(QtWidgets.QDialog, Ui_WDarth):
    stopWorkerSignal = QtCore.pyqtSignal()
    runWorkerSignal = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self._parent = parent
        self.setUI()
        self.setPool()
        self.connectSignals()
        self.workerThread.start()

    def connectSignals(self):
        self.stopWorkerSignal.connect(self.pool.stopIt)
        self.runWorkerSignal.connect(self.pool.run)

    def setPool(self):
        self.workerThread = QtCore.QThread()
        self.pool = WorkerPool()
        self.pool.moveToThread(self.workerThread)
        self.pool.progressSignal.connect(self.showProgress)
        self.pool.finishedSignal.connect(self.workerFinished)

    def setUI(self):
        self.setupUi(self)
        intValidator = QtGui.QIntValidator()
        intValidator.setBottom(1)
        floatValidator = QtGui.QDoubleValidator()
        floatValidator.setBottom(1e-3)
        self.xLineEdit.setValidator(intValidator)
        self.yLineEdit.setValidator(intValidator)
        self.zLineEdit.setValidator(intValidator)
        self.editDownsample.setValidator(intValidator)
        self.editScale.setValidator(intValidator)
        self.dQLineEdit.setValidator(floatValidator)
        self.stopButton.setVisible(False)
        self.loadSettings()

    def showError(self, errors):
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        QtWidgets.QMessageBox.critical(self,
                                       'Darth Vader error',
                                       'Datasets in folders\n{}\nare corrupted: it seems you have aborted the '
                                       'experiments because the headers are empty.\n It cannot be '
                                       'processed.'.format('\n'.join(errors)))

    def showProgress(self, info, value):
        self.runProgressBar.setFormat('{0}: %p%'.format(info))
        self.runProgressBar.setValue(value)

    def closeEvent(self, event):
        self.saveSettings()
        self.stopWorkerSignal.emit()
        self.hide()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            pass
        else:
            QtWidgets.QDialog.keyPressEvent(self, event)

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WDarth/Geometry', self.saveGeometry())
        s.setValue('WDarth/lastFolder', self.lastFolder)
        s.setValue('WDarth/folder', self.folderLineEdit.text())
        s.setValue('WDarth/x', self.xLineEdit.text())
        s.setValue('WDarth/y', self.yLineEdit.text())
        s.setValue('WDarth/z', self.zLineEdit.text())
        s.setValue('WDarth/dQ', self.dQLineEdit.text())
        s.setValue('WDarth/lorentz', self.lorentzCheckBox.isChecked())
        s.setValue('WDarth/treeLayersState', self.treeLayers.header().saveState())
        s.setValue('WDarth/downsample', self.editDownsample.text())
        s.setValue('WDarth/scale', self.editScale.text())
        s.setValue('WDarth/volume', self.volumeCheckBox.isChecked())

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WDarth/Geometry', QtCore.QByteArray()))
        self.lastFolder = s.value('WDarth/lastFolder', u'')
        self.folderLineEdit.setText(s.value('WDarth/folder', u''))
        self.xLineEdit.setText(s.value('WDarth/x', '256'))
        self.yLineEdit.setText(s.value('WDarth/y', '256'))
        self.zLineEdit.setText(s.value('WDarth/z', '256'))
        self.dQLineEdit.setText(s.value('WDarth/dQ', '0.6'))
        self.lorentzCheckBox.setChecked(pyqt2bool(s.value('WDarth/lorentz', False)))
        self.treeLayers.header().restoreState(s.value('WDarth/treeLayersState', QtCore.QByteArray()))
        self.editDownsample.setText(s.value('WDarth/downsample', '1'))
        self.editScale.setText(s.value('WDarth/scale', '1'))
        self.volumeCheckBox.setChecked(pyqt2bool(s.value('WDarth/volume', True)))

    @QtCore.pyqtSlot()
    def on_runButton_clicked(self):
        folder = self.folderLineEdit.text()
        if not folder or not os.path.exists(folder):
            return
        self.runButton.setVisible(False)
        self.stopButton.setVisible(True)
        params = {
            'folder': folder,
            'x': int(self.xLineEdit.text()),
            'y': int(self.yLineEdit.text()),
            'z': int(self.zLineEdit.text()),
            'dQ': float(self.dQLineEdit.text()),
            'lorentz': int(self.lorentzCheckBox.isChecked()),
            'scale': int(self.editScale.text()),
            'volume': self.volumeCheckBox.isChecked(),
            'layers': self.treeLayers.getLayers(),
            'downsample': int(self.editDownsample.text()),
        }
        self.runWorkerSignal.emit(params)

    def workerFinished(self, errors):
        self.runButton.setVisible(True)
        self.stopButton.setVisible(False)
        if errors:
            self.showError(errors)

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        self.stopWorkerSignal.emit()

    @QtCore.pyqtSlot()
    def on_folderButton_clicked(self):
        # noinspection PyCallByClass,PyTypeChecker
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory', self.lastFolder)
        if not folder:
            return
        self.folderLineEdit.setText(folder)
        self.lastFolder = folder
