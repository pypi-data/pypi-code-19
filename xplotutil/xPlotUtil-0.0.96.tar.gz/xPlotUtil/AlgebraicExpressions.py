#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""
# ---------------------------------------------------------------------------------------------------------------------#
from __future__ import unicode_literals
import sys
import numpy as np
import os
from pylab import *

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from scipy.optimize import curve_fit
from scipy import exp
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import FormatStrFormatter
# ---------------------------------------------------------------------------------------------------------------------#

class AlgebraicExpress:
    """This class is where the algebraic expressions are formed to be plotted.
    """

    def __init__(self, parent=None):
        self.gausFit = parent
        self.dockedOpt = self.gausFit.dockedOpt
        self.readSpec = self.gausFit.readSpec
        self.myMainWindow = self.gausFit.myMainWindow


    def singularValueDecomposition(self):
        """This method calculates the svd of the raw data.
        """
        self.U = []
        self.S = []
        self.V = []

        self.U, self.S, self.V = svd(self.dockedOpt.TT)

    def PlotAlgebraicExpGraphs(self, title, name1, x, y1, xLabel, yLabel1, y2, name2, yLabel2, y3, name3, yLabel3):
        """Generic plotting method that creates a canvas with 3 subplots.
        :param title: Title of tab
        :param name1: name of graph one
        :param x: x-axis of graphs
        :param y1: y-axis of graph one
        :param xLabel: x-label for graphs
        :param yLabel1: y-label for graph two
        :param y2: y-axis of graph two
        :param name2: name of graph 2
        :param yLabel2: y-label for graph two
        :param y3: y-axis of graph three
        :param name3: name of graph three
        :param yLabel3: y-label for graph three
        """
        mainGraph = QWidget()
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        canvas.setParent(mainGraph)
        axes = fig.add_subplot(221)
        ax = fig.add_subplot(222)
        axe = fig.add_subplot(223)

        axes.set_title(name1)
        axes.set_xlabel(xLabel)
        axes.set_ylabel(yLabel1)
        axes.plot(x, y1)

        ax.set_title(name2)
        ax.set_xlabel(xLabel)
        ax.set_ylabel(yLabel2)
        ax.plot(x, y2)

        axe.set_title(name3)
        axe.set_xlabel(xLabel)
        axe.set_ylabel(yLabel3)
        axe.plot(x, y3)

        fig.tight_layout(pad=.4, w_pad=.5, h_pad=-1.4)
        canvas.draw()

        tab = QWidget()
        tab.setStatusTip(title)
        vbox = QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)

        self.myMainWindow.savingCanvasTabs(tab, title, canvas, fig)

    def plotTh2ThExp(self):
        """This method plots the theta2theta graphs.
        """
        title = '\u03B82\u03B8 (Scan#: ' + self.readSpec.scan + ')'

        name1 = "\u03B82\u03B8"
        x = self.readSpec.L
        y1 = -self.U[:, 0]
        xLabel = "RLU"
        yLabel1 = "TH2TH"

        name2 = "\u03B82\u03B8'"
        y2 = self.U[:, 1]
        yLabel2 = "Counts"

        name3 = "\u03B82\u03B8''"
        y3 = self.U[:, 3]
        yLabel3 = "Counts"
        self.PlotAlgebraicExpGraphs(title, name1, x, y1, xLabel, yLabel1, y2, name2, yLabel2, y3, name3, yLabel3)

    def plotWeightingExp(self):
        """This method plots the weighting graphs.
        """
        title = 'Weighting (Scan#: ' + self.readSpec.scan + ')'

        name1 = "Weighting 1"
        x = self.gausFit.getVoltage()
        y1 = -self.V[0]
        xLabel = "Voltage"
        yLabel1 = "Weighting 1"

        name2 = "Weighting 2"
        y2 = self.V[1]
        yLabel2 = "Weighting 2"

        name3 = "Weighting 3"
        y3 = self.V[2]
        yLabel3 = "Weighting 3"
        self.PlotAlgebraicExpGraphs(title, name1, x, y1, xLabel, yLabel1, y2, name2, yLabel2, y3, name3, yLabel3)

    def PlotAlgebraicExpGraph(self, title, name, x, y, xLabel, yLabel):
        """Generic plotting method with one subplot.
        :param title: Title of tab
        :param name: name of graph and tool tip
        :param x: x-axis
        :param y: y-axis
        :param xLabel: x label
        :param yLabel: y label
        """
        mainGraph = QWidget()
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        canvas.setParent(mainGraph)
        axes = fig.add_subplot(111)

        axes.set_title(name)
        axes.set_xlabel(xLabel)
        axes.set_ylabel(yLabel)
        axes.plot(x, y)

        fig.tight_layout()
        canvas.draw()

        tab = QWidget()
        tab.setStatusTip(title)
        vbox = QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)

        self.myMainWindow.savingCanvasTabs(tab, title, canvas, fig)

    def plotSingleValueIndex(self):
        """Plots the single value index graph.
        """
        title = 'Singular Value Index (Scan#: ' + self.readSpec.scan + ')'
        name = "Singular Value Index"
        x = self.gausFit.getVoltage()
        y = log(self.S)
        xLabel = "Voltage"
        yLabel = "Singular Value"
        self.PlotAlgebraicExpGraph(title, name, x, y, xLabel, yLabel)


