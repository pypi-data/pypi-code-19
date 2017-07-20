#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
from pyqtgraph import dockarea


class WPlot(QtWidgets.QMainWindow):
    def __init__(self, name, button, parent=None):
        # noinspection PyArgumentList
        super().__init__(parent=parent)
        self.data = None
        self.array = None
        self.setupUI()
        self.name = name
        self._parent = parent
        self.button = button
        self.setWindowTitle('{} plot'.format(name))
        self.loadSettings()

    def setupUI(self):
        self.area = dockarea.DockArea(self)
        self.setCentralWidget(self.area)
        d1 = dockarea.Dock('2D')
        d2 = dockarea.Dock('1D')
        d3 = dockarea.Dock('Coordinates', size=(1, 1))
        self.area.addDock(d1, 'top')
        self.area.addDock(d2, 'bottom')
        self.area.addDock(d3, 'right', d2)
        self.plot2DView = pg.ImageView()
        self.plot1DView = pg.PlotWidget()
        self.coordsLabel = QtWidgets.QLabel()
        d1.addWidget(self.plot2DView)
        d2.addWidget(self.plot1DView)
        d3.addWidget(self.coordsLabel)
        plotItem = self.plot1DView.getPlotItem()
        imageItem = self.plot2DView.getImageItem()
        imageView = self.plot2DView.getView()

        def mouseMoved1D(evt):
            pos = evt[0]
            if plotItem.sceneBoundingRect().contains(pos):
                mousePoint = plotItem.vb.mapSceneToView(pos)
                self.coordsLabel.setText('x = {:.6f}\ny = {:.6f}'.format(mousePoint.x(), mousePoint.y()))

        def mouseMoved2D(evt):
            pos = evt[0]
            if imageItem.sceneBoundingRect().contains(pos):
                mousePoint = imageView.mapSceneToView(pos)
                x, y = mousePoint.x(), mousePoint.y()
                i = self.array[int(x), int(y)] if self.array is not None else 0
                self.coordsLabel.setText('x = {:.0f}\ny = {:.0f}\nI = {:.6f}'.format(x, y, i))

        self.proxy2D = pg.SignalProxy(plotItem.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved1D)
        self.proxy1D = pg.SignalProxy(imageItem.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved2D)

    def closeEvent(self, event):
        self.saveSettings()
        self.button.setChecked(False)
        event.accept()

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WPlot{}/Geometry'.format(self.name), self.saveGeometry())
        s.setValue('WPlot{}/dockState'.format(self.name), json.dumps(self.area.saveState()))

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WPlot{}/Geometry'.format(self.name), QtCore.QByteArray()))
        dockState = s.value('WPlot{}/dockState'.format(self.name), None)
        if dockState:
            self.area.restoreState(json.loads(dockState))

    def plot(self, response):
        data1d = response.get('data1d', None)
        if data1d:
            x, y, e = data1d
            try:
                y[y <= 0] = y[y > 0].min()
            except ValueError:  # it seems that the array is zero-like, skip it
                pass
            self.data = y
            self.plot1DView.plot(x, y, pen='g', clear=True)
            self.plot1DView.setTitle('{}; Tr = {:.5f}'.format(response.get('chiFile', ''),
                                                              response.get('transmission', 0)))
        image = response.get('image', None)
        if image is not None:
            self.array = image
            self.plot2DView.setImage(self.array)
            self.plot2DView.setLevels(0, self.array.mean() + 8 * self.array.std())
