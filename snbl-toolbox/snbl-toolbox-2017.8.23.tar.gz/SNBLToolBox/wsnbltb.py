#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets
from .ui.ui_snbltb import Ui_WSnblToolBox
from .ui.ui_wsnbltbabout import Ui_WSnblAbout
from .wcrysis import WCrysis
from .convert import ConvertWizard
from .wheader import WHeader
from .wsleuth import WSleuth
from .roerik.wgunnar import WGunnar
from .wdarth import WDarth
# noinspection PyUnresolvedReferences
from .ui import resources_rc

try:
    from . import frozen
except ImportError:
    frozen = False


def get_hg_hash():
    if not get_hg_hash.hash:
        if hasattr(sys, 'frozen') or frozen:
            # noinspection PyUnresolvedReferences
            get_hg_hash.hash = frozen.hg_hash
        else:
            path = os.path.dirname(os.path.dirname(__file__))
            try:
                pipe = subprocess.Popen(['hg', 'id', '-i', '-R', path], stdout=subprocess.PIPE)
                get_hg_hash.hash = pipe.stdout.read().decode()
            except OSError:
                get_hg_hash.hash = 'unknown'
        get_hg_hash.hash = get_hg_hash.hash.strip()
    return get_hg_hash.hash
get_hg_hash.hash = ''


class WAboutSnblTB(QtWidgets.QDialog, Ui_WSnblAbout):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self._parent = parent
        self.setupUi(self)
        lt = self.aboutLabel.text()
        lt = lt.replace('@', get_hg_hash())
        self.aboutLabel.setText(lt)
        self.setWindowIcon(QtGui.QIcon(':/swiss'))
        # noinspection PyCallByClass,PyTypeChecker
        QtCore.QTimer.singleShot(0.1, lambda: self.resize(0, 0))

    @QtCore.pyqtSlot()
    def on_closeButton_clicked(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_aboutQtButton_clicked(self):
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        QtWidgets.QMessageBox.aboutQt(self)


class WSnblTB(QtWidgets.QDialog, Ui_WSnblToolBox):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self._parent = parent
        self.setupUi(self)
        self.loadSettings()
        self.wcrysis = WCrysis(self)
        self.wconvert = ConvertWizard(self)
        self.wabout = WAboutSnblTB(self)
        self.wheader = WHeader(self)
        self.wsleuth = WSleuth(self)
        self.wroerik = WGunnar(self)
        self.wdarth = WDarth(self)
        # noinspection PyArgumentList
        if QtWidgets.QApplication.screens()[0].logicalDotsPerInch() > 120:  # Hack for HiDPI displays
            size = QtCore.QSize(146, 146)
            self.roerikButton.setIconSize(size)
            self.crysisButton.setIconSize(size)
            self.convertButton.setIconSize(size)
            self.infoButton.setIconSize(size)
            self.headExButton.setIconSize(size)
            self.darthButton.setIconSize(size)
            self.sleuthButton.setIconSize(size)
            self.sigmasButton.setIconSize(size)
        # noinspection PyCallByClass,PyTypeChecker
        QtCore.QTimer.singleShot(0.1, lambda: self.resize(0, 0))

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            pass
        else:
            QtWidgets.QDialog.keyPressEvent(self, event)

    def closeEvent(self, event):
        self.saveSettings()
        self.wcrysis.close()
        self.wconvert.close()
        self.wabout.close()
        self.wheader.close()
        self.wsleuth.close()
        self.wroerik.close()
        self.wdarth.close()

    def saveSettings(self):
        settings = QtCore.QSettings()
        settings.setValue('WSNBLToolBox/Geometry', self.saveGeometry())

    def loadSettings(self):
        settings = QtCore.QSettings()
        self.restoreGeometry(settings.value('WSNBLToolBox/Geometry', QtCore.QByteArray()))

    @QtCore.pyqtSlot()
    def on_crysisButton_clicked(self):
        self.wcrysis.show()

    @QtCore.pyqtSlot()
    def on_convertButton_clicked(self):
        if self.wconvert.stopped:
            self.wconvert = ConvertWizard(self)
        self.wconvert.show()

    @QtCore.pyqtSlot()
    def on_sigmasButton_clicked(self):
        # noinspection PyArgumentList,PyCallByClass,PyTypeChecker
        QtWidgets.QMessageBox.question(self, 'Fit2D?!', 'Fit2D?! In 2016?! Seriously?! No way!',
                                       QtWidgets.QMessageBox.No)

    @QtCore.pyqtSlot()
    def on_infoButton_clicked(self):
        self.wabout.show()

    @QtCore.pyqtSlot()
    def on_headExButton_clicked(self):
        self.wheader.show()

    @QtCore.pyqtSlot()
    def on_sleuthButton_clicked(self):
        self.wsleuth.show()

    @QtCore.pyqtSlot()
    def on_darthButton_clicked(self):
        self.wdarth.show()

    @QtCore.pyqtSlot()
    def on_roerikButton_clicked(self):
        self.wroerik.show()
