#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.

#C In some methods LFit or L refer to the Lattice Constant not RLU

"""
# ---------------------------------------------------------------------------------------------------------------------#
from __future__ import unicode_literals

from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter
from peakutils import peak
from pylab import *
from scipy import exp
from scipy.optimize import curve_fit

from xPlotUtil.Source.AlgebraicExpressions import AlgebraicExpress


# ---------------------------------------------------------------------------------------------------------------------#

class GaussianFitting:
    """This were most of the fits occur, and the plotting of those outcomes.
    """

    def __init__ (self, parent=None):
        self.TwoPkGausFitData = []
        self.OnePkFitData = []
        self.LPosPrcChangeData = []
        self.LPos1PrcChangeData = []
        self.LPos2PrcChangeData = []
        self.readSpec = parent
        self.dockedOpt = self.readSpec.dockedOpt
        self.myMainWindow = self.dockedOpt.myMainWindow
        self.algebraExp = AlgebraicExpress(parent=self)
        self.continueGraphingEachFit = True #Boolean to stop on Each fit graphing

    # --------------------------------Gaussian Fit---------------------------------------------------------------------#
    def OnePeakFitting(self):
        """Calls on the gaussian fit function for one peak and saves fitted data in array.
        """
        try:
            nRow, nCol = self.dockedOpt.fileInfo()

            self.binFitData = zeros((nRow, 0))
            self.OnePkFitData = zeros((nCol, 6))  # Creates the empty 2D List
            for j in range(nCol):
                col_data = self.dockedOpt.TT[:, j]
                xx = arange(0, len(col_data))
                param = self.onePkFitting(xx, col_data)
                fit_result = param[0]
                fit_error = param[1]
                self.OnePkFitData[j, :] = (fit_result[0], fit_error[0], fit_result[1], fit_error[1], fit_result[2],
                                           fit_error[2])
            return False
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Please make sure the guesses are realistic when fitting.")
            return True

    def onePkFitting(self, xx, yy):
        """Gaussian Fit for one Peak.
        :param xx: x-value
        :param yy: y-values
        :return: fitted data and error
        """
        x1 = xx[0]
        x2 = xx[-1]
        y1 = yy[0]
        y2 = yy[-1]
        m = (y2-y1)/(x2-x1)
        b = y2-m*x2
        mean = sum(xx * yy) / sum(yy)  # note this correction
        sig = np.sqrt(sum(yy * (xx - mean) ** 2)) / sqrt(sum(yy))
        popt, pcov = curve_fit(self.gaus1, xx, yy, p0=[self.onePeakAmp, self.onePeakPos, self.onePeakWid, b, m])
        perr = np.sqrt(np.diag(pcov))

        # Filling array with the Gaussian fit data from each bin
        binFit = np.reshape(self.gaus1(xx, *popt), (len(self.gaus1(xx, *popt)), 1))
        self.binFitData = np.concatenate((self.binFitData, binFit), axis=1)

        if self.continueGraphingEachFit == True:
            self.graphEachFitRawData(xx, yy, popt, 1)
        return popt, perr

    def gaus1(self, x, a, x0, sigma, b, m):
        return a * exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + b + m * x

    def gausOnePeakInputDialog(self):
        """One Peak dialog where user inputs guesses for the gaussian fit.
        """
        self.dialogOnePeakGausFit = QDialog(self.myMainWindow)
        inputForm = QFormLayout()
        buttonLayout = QHBoxLayout()
        spaceLayout = QVBoxLayout()

        spaceLayout.addStretch(1)
        amp, pos = self.GuessOnePeak()
        self.onePeakAmpSpin = QDoubleSpinBox()
        self.onePeakAmpSpin.setMaximum(10000000)
        self.onePeakAmpSpin.setValue(amp)
        self.onePeakPosSpin = QDoubleSpinBox()
        self.onePeakPosSpin.setValue(pos)
        self.onePeakWidthSpin = QDoubleSpinBox()
        self.onePeakWidthSpin.setValue(5)

        ok = QPushButton("Ok")
        cancel = QPushButton("Cancel")

        cancel.clicked.connect(self.dialogOnePeakGausFit.close)
        ok.clicked.connect(self.returnOnePeakGausUserInput)
        buttonLayout.addWidget(cancel)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(ok)

        inputForm.addRow("Peak Amplitude: ", self.onePeakAmpSpin)
        inputForm.addRow("Peak Position: ", self.onePeakPosSpin)
        inputForm.addRow("Peak Width: ", self.onePeakWidthSpin)
        inputForm.addRow(spaceLayout)
        inputForm.addRow(buttonLayout)

        self.dialogOnePeakGausFit.setWindowTitle("Guesses")
        self.dialogOnePeakGausFit.setLayout(inputForm)
        self.dialogOnePeakGausFit.resize(200, 110)
        self.onePeakWidthSpin.setFocus()
        self.dialogOnePeakGausFit.show()

    def returnOnePeakGausUserInput(self):
        """Sets the values of the variables in the method onePkFitting, that are used as parameters.
        """
        self.onePeakAmp = float(self.onePeakAmpSpin.value())
        self.onePeakPos = float(self.onePeakPosSpin.value())
        self.onePeakWid = float(self.onePeakWidthSpin.value())

        self.dialogOnePeakGausFit.close()
        error = self.OnePeakFitting()

        # Marks that the data has been fitted for one peak
        if error == False:
            self.dockedOpt.onePeakStat = True
            self.dockedOpt.gausFitStat = True
            self.dockedOpt.GraphingGaussianOptionsTree()

    def GuessOnePeak(self):
        """This method uses the PeakUtils module to calculate the position of the peak, which helps get the
        amplitude.
        :return: amplitude and position of peak
        """
        try:
            y = self.dockedOpt.TT.mean(axis=1)
            ind = peak.indexes(y)
            pos = round(ind[0], 0)
            amp = round(y[ind[0]], 2)
            return amp, pos
        except:
                return 0, 0

    def TwoPeakFitting(self):
        """Calls on the gaussian fit function for two peaks and saves fitted data in array.
        """
        try:
            nRow, nCol = self.dockedOpt.fileInfo()
            self.binFitData = zeros((nRow, 0))
            self.TwoPkGausFitData = zeros((nCol, 12))  # Creates the empty 2D List
            for j in range(nCol):
                col_data = self.dockedOpt.TT[:, j]
                xx = arange(0, len(col_data))
                param = self.twoPkFitting(xx, col_data)
                fit_result = ["%f" % member for member in param[0]]
                fit_error = ["%f" % member for member in param[1]]
                self.TwoPkGausFitData[j, :] = (fit_result[0], fit_error[0], fit_result[1], fit_error[1], fit_result[2],
                                           fit_error[2], fit_result[3], fit_error[3], fit_result[4], fit_error[4],
                                           fit_result[5], fit_error[5])
            return False
        except:
            QMessageBox.warning(self.myMainWindow, "Warning", "Please make sure to input realistic guesses.")
            return True

    def twoPkFitting(self, xx, yy):
        """Gaussian Fit for one Peak.
              :param xx: x-value
              :param yy: y-values
              :return: fitted data and error
        """
        x1 = xx[0]
        x2 = xx[-1]
        y1 = yy[0]
        y2 = yy[-1]
        m = (y2 - y1) / (x2 - x1)
        b = y2 - m * x2
        mean = sum(xx * yy) / sum(yy)
        sig = np.sqrt(sum(yy * (xx - mean) ** 2)) / sqrt(sum(yy))
        m = 0
        popt, pcov = curve_fit(self.gaus2, xx, yy, p0=[self.twoPeak1Amp, self.twoPeak2Amp, self.twoPeak1Pos, self.twoPeak2Pos,
                                                       self.twoPeak1Wid, self.twoPeak2Wid, b, m])
        perr = np.sqrt(np.diag(pcov))

        # Filling array with the Gaussian fit data from each bin
        binFit = np.reshape(self.gaus2(xx, *popt), (len(self.gaus2(xx, *popt)), 1))
        self.binFitData = np.concatenate((self.binFitData, binFit), axis=1)

        if self.continueGraphingEachFit == True:
            self.graphEachFitRawData(xx, yy, popt, 2)

        return popt, perr

    def gaus2(self, x, a1, a2, x01, x02, sigma1, sigma2, background, m):
        return a1 * exp(-(x - x01) ** 2 / (2 * sigma1 ** 2))\
               + a2 *exp(-(x - x02) ** 2 / (2 * sigma2 ** 2)) + background + m * x

    def gausTwoPeakInputDialog(self):
        """Two Peak dialog where user inputs guesses for the gaussian fit.
        """
        self.dialogGausFit = QDialog(self.myMainWindow)
        inputForm = QFormLayout()
        buttonLayout = QHBoxLayout()
        spaceLayout = QVBoxLayout()

        spaceLayout.addStretch(1)
        amp1, pos1, amp2, pos2 = self.GuessTwoPeak()
        self.twoPeak1AmpSpin = QDoubleSpinBox()
        self.twoPeak1AmpSpin.setMaximum(10000000)
        self.twoPeak1AmpSpin.setValue(amp1)
        self.twoPeak1PosSpin = QDoubleSpinBox()
        self.twoPeak1PosSpin.setValue(pos1)
        self.twoPeak1WidthSpin = QDoubleSpinBox()
        self.twoPeak1WidthSpin.setValue(5)

        self.twoPeak2AmpSpin = QDoubleSpinBox()
        self.twoPeak2AmpSpin.setMaximum(10000000)
        self.twoPeak2AmpSpin.setValue(amp2)
        self.twoPeak2PosSpin = QDoubleSpinBox()
        self.twoPeak2PosSpin.setValue(pos2)
        self.twoPeak2WidthSpin = QDoubleSpinBox()
        self.twoPeak2WidthSpin.setValue(5)

        ok = QPushButton("Ok")
        cancel = QPushButton("Cancel")

        cancel.clicked.connect(self.dialogGausFit.close)
        ok.clicked.connect(self.returnTwoPeakGausUserInput)
        buttonLayout.addWidget(cancel)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(ok)

        inputForm.addRow("Peak#1 Amplitude: ", self.twoPeak1AmpSpin)
        inputForm.addRow("Peak#1 Position: ", self.twoPeak1PosSpin)
        inputForm.addRow("Peak#1 Width: ", self.twoPeak1WidthSpin)
        inputForm.addRow("Peak#2 Amplitude: ", self.twoPeak2AmpSpin)
        inputForm.addRow("Peak#2 Position: ", self.twoPeak2PosSpin)
        inputForm.addRow("Peak#2 Width: ", self.twoPeak2WidthSpin)
        inputForm.addRow(spaceLayout)
        inputForm.addRow(buttonLayout)

        self.dialogGausFit.setWindowTitle("Input Guess Data for Fit")
        self.dialogGausFit.setLayout(inputForm)
        self.dialogGausFit.resize(250, 200)
        self.twoPeak2WidthSpin.setFocus()
        self.dialogGausFit.show()

    def returnTwoPeakGausUserInput(self):
        """Sets the values of the variables in the method twoPkFitting, that are used as parameters.
        """
        self.twoPeak1Amp = float(self.twoPeak1AmpSpin.value())
        self.twoPeak1Pos = float(self.twoPeak1PosSpin.value())
        self.twoPeak1Wid = float(self.twoPeak1WidthSpin.value())

        self.twoPeak2Amp = float(self.twoPeak2AmpSpin.value())
        self.twoPeak2Pos = float(self.twoPeak2PosSpin.value())
        self.twoPeak2Wid = float(self.twoPeak2WidthSpin.value())

        self.dialogGausFit.close()

        error = self.TwoPeakFitting()

        if error == False:
            # Marks that the data has been fitted for one peak
            self.dockedOpt.twoPeakStat = True
            self.dockedOpt.gausFitStat = True
            self.dockedOpt.GraphingGaussianOptionsTree()

    def GuessTwoPeak(self):
        """This method uses the PeakUtils module to calculate the position of the peaks, which help get the
        amplitude.
        :return: amplitude and position for peak 1 and 2.
        """
        try:
            y = self.dockedOpt.TT.mean(axis=1)
            ind = peak.indexes(y, min_dist=4)
            pos1 = round(ind[0], 0)
            amp1 = round(y[ind[0]], 3)
            pos2 = round(ind[1], 0)
            amp2 = round(y[ind[1]], 3)
            return amp1, pos1, amp2, pos2
        except:
            return 0, 0, 0, 0

    def graphEachFitRawData(self, xx, yy, popt, whichPeak):
        """This method graphs the raw data and the fitted data for each column.
        :param xx: bins
        :param yy: raw data column
        :param popt: from the gaussian fit
        :param whichPeak: number of peaks
        """
        self.mainGraph = QDialog(self.myMainWindow)
        self.mainGraph.resize(600, 600)
        dpi = 100
        fig = Figure((3.0, 3.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(self.mainGraph)
        axes = fig.add_subplot(111)

        axes.plot(xx, yy, 'b+:', label='data')
        if(whichPeak == 1):
            axes.plot(xx, self.gaus1(xx, *popt), 'ro:', label='fit')
        elif(whichPeak == 2):
            axes.plot(xx, self.gaus2(xx, *popt), 'ro:', label='fit')
        axes.legend()
        axes.set_title('Gaussian Fit')
        axes.set_xlabel('Bins')
        axes.set_ylabel('Intensity')
        canvas.draw()

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.skipEachFitGraphButton()
        self.nextFitGraphButton()
        hbox.addWidget(self.skipEachFitGraphBtn)
        hbox.addStretch(1)
        hbox.addWidget(self.nextFitGraphBtn)
        graphNavigationBar = NavigationToolbar(canvas, self.mainGraph)
        vbox.addLayout(hbox)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        self.mainGraph.setLayout(vbox)
        self.mainGraph.exec_()

    def skipEachFitGraphButton(self):
        """Button that allows the user to skip each fit graph.
        """
        self.skipEachFitGraphBtn = QPushButton('Skip')
        self.skipEachFitGraphBtn.setStatusTip("Skip the graphing of each fit")
        self.skipEachFitGraphBtn.clicked.connect(self.skipEachFit)

    def nextFitGraphButton(self):
        """Button that shows the next fit graph.
        """
        self.nextFitGraphBtn = QPushButton('Next')
        self.nextFitGraphBtn.clicked.connect(self.nextFitGraph)
        self.nextFitGraphBtn.setStatusTip("Graphs the next fit and the original data")

    def nextFitGraph(self):
        """Closes the current fit graph to show the next.
        """
        self.mainGraph.close()

    def skipEachFit(self):
        """Closes the current fit graph and sets continueGraphingEachFit to false
         so that other graphs are not showed.
         """
        self.continueGraphingEachFit = False
        self.mainGraph.close()

    def GraphUtilGaussianFitGraphs(self, name, x, y, error, xLabel, yLabel, whichGraph):
        """Generic plotting method that plots depending on which graph is being plotted.
        :param canvas: canvas for widget
        :param fig: figure for graph
        :param name: name of tab
        :param x: x-values
        :param y: y-values
        :param error: error values for gaussian fit graphs
        :param xLabel: x-axis label
        :param yLabel: y-axis label
        :param whichGraph: char that represents either gaussian or lattice fit
        """
        mainGraph = QWidget()
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        canvas.setParent(mainGraph)
        axes = fig.add_subplot(111)

        axes.plot(x, y)

        if whichGraph == 'G':
            axes.errorbar(x, y, yerr=error, fmt='o')
        elif whichGraph == 'L':
            axes.plot(x, y, 'go')
            axes.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))

        axes.set_title(name)
        axes.set_xlabel(xLabel)
        axes.set_ylabel(yLabel)
        canvas.draw()

        tab = QWidget()
        tab.setStatusTip(name)
        vbox = QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)

        self.myMainWindow.savingCanvasTabs(tab, name, canvas, fig)

    def graphOnePeakAmplitude(self):
        """This method graphs the Amplitude for one peak.
        """
        x = self.getVoltage()
        y = self.OnePkFitData[:, 0]
        error = self.OnePkFitData[:, 1]
        xLabel = 'Voltage'
        yLabel = 'Intensity'
        name = 'Amplitude (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphOnePeakPosition(self):
        """This method graphs the peak position for one peak.
        """
        x = self.getVoltage()
        y = self.OnePkFitData[:, 2]
        error = self.OnePkFitData[:, 3]
        xLabel = 'Voltage'
        yLabel = 'Position'
        name = 'Position (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphOnePeakWidth(self):
        """This method graphs the Peak width for one peak.
        """
        x = self.getVoltage()
        y = self.OnePkFitData[:, 4]
        error = self.OnePkFitData[:, 5]
        xLabel = 'Voltage'
        yLabel = 'Width'
        name = 'Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphOnePeakAmplitudeXWidth(self):
        """This method graphs the amplitude x width for one peak.
        """
        x = self.getVoltage()
        yA = self.OnePkFitData[:, 0]
        yW = self.OnePkFitData[:, 4]
        a_err = self.OnePkFitData[:, 1]
        w_err = self.OnePkFitData[:, 5]
        y = yA * yW
        error = ((y * a_err) + (y * w_err)) / y

        xLabel = 'Voltage'
        yLabel = 'A x W'
        name = 'Amplitude X Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakAmplitude1(self):
        """This method graphs the peak one amplitude for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 0]
        error = self.TwoPkGausFitData[:, 1]
        xLabel = 'Voltage'
        yLabel = 'Intensity'
        name = 'Peak #1 Amplitude (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakPosition1(self):
        """This method graphs the peak one position for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 4]
        error = self.TwoPkGausFitData[:, 5]
        xLabel = 'Voltage'
        yLabel = 'Position'
        name = 'Peak #1 Position (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakWidth1(self):
        """This method graphs the peak one width for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 8]
        error = self.TwoPkGausFitData[:, 9]
        xLabel = 'Voltage'
        yLabel = 'Width'
        name = 'Peak #1 Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakAmplitudeXWidth1(self):
        """This method graphs the peak one amplitude x width for two peak.
        """
        x = self.getVoltage()
        yA = self.TwoPkGausFitData[:, 0]
        yW = self.TwoPkGausFitData[:, 8]
        a_err = self.TwoPkGausFitData[:, 1]
        w_err = self.TwoPkGausFitData[:, 9]
        y = yA * yW
        error = ((y * a_err) + (y * w_err))/y

        xLabel = 'Voltage'
        yLabel = 'A x W'
        name = 'Peak #1 Amplitude X Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakAmplitude2(self):
        """This method graphs the peak two Amplitude for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 2]
        error = self.TwoPkGausFitData[:, 3]
        xLabel = 'Voltage'
        yLabel = 'Intensity'
        name = 'Peak #2 Amplitude (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(
            name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakPosition2(self):
        """This method graphs the peak two position for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 6]
        error = self.TwoPkGausFitData[:, 7]
        xLabel = 'Voltage'
        yLabel = 'Position'
        name = 'Peak #2 Position (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakWidth2(self):
        """This method graphs the peak two width for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 10]
        error = self.TwoPkGausFitData[:, 11]
        xLabel = 'Voltage'
        yLabel = 'Width'
        name = 'Peak #2 Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakAmplitudeXWidth2(self):
        """This method graphs the peak two amplitude x width for the two peak.
        """
        x = self.getVoltage()
        yA = self.TwoPkGausFitData[:, 2]
        yW = self.TwoPkGausFitData[:, 10]
        a_err = self.TwoPkGausFitData[:, 3]
        w_err = self.TwoPkGausFitData[:, 11]
        y = yA * yW
        error = ((y * a_err) + (y * w_err)) / y

        xLabel = 'Voltage'
        yLabel = 'A x W'
        name = 'Peak #2 Amplitude X Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def getVoltage(self):
        """This method gets the voltage of the bins.
        :return: the voltage
        """
        try:
            x = [] # X array initialized

            # Gets the amplitude
            inF = open(self.dockedOpt.fileName, 'r')
            lines = inF.readlines()
            header = ''
            for (iL, line) in enumerate(lines):
                if line.startswith('#'):
                    header = line
            inF.close()
            words = header.split()
            amplWord = words[6]
            ampl = amplWord.split('.')
            amp = float(ampl[0])

            # get the bins
            nRow, bins = self.dockedOpt.fileInfo()

            # Uses the data to find the x axis
            amplStart = amp/2
            points = bins/2
            xDif = amp/points
            xStart = xDif/2
            startX = (-1*amplStart) + xStart
            x.append(startX)
            for j in range(points-1):
                startX = startX + xDif
                x.append(startX)

            x.append(startX)
            for j in range(points-1):
                startX = startX - xDif
                x.append(startX)
            return x
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Unable to detect voltage. Please make sure the PVvalue "
                                                            "contains the voltage in the comments.")
    # -----------------------------------------Lattice Fit-------------------------------------------------------------#
    def PositionLFit(self, pos, rows):
        """This method calculates the lattice based on the passed paramaters.
        :param pos: position of the peak
        :param rows: number of total points
        """
        l = (1/(((pos/rows)*(self.readSpec.lMax-self.readSpec.lMin)+self.readSpec.lMin)/2))*self.readSpec.lElement
        return l

    def doLFit(self):
        """This function stores the lattice in arrays depending on the peak.
        """
        try:
            nRow, nCol = self.dockedOpt.fileInfo()

            if  self.dockedOpt.onePeakStat == True :
                self.LPosData = []  # L Constant for One Peak
                for i in range(nCol):
                    self.LPosData.append(self.PositionLFit(self.OnePkFitData[i, 2], nRow))

            elif self.dockedOpt.twoPeakStat == True:
                self.LPos1Data = []  # L Constant for Two Peak [#1]
                self.LPos2Data = []  # L Constant for Two Peak [#2]
                # Position 1
                for i in range(nCol):
                  self.LPos1Data.append(self.PositionLFit(self.TwoPkGausFitData[i, 4], nCol))
                # Position 2
                for i in range(nCol):
                  self.LPos2Data.append(self.PositionLFit(self.TwoPkGausFitData[i, 6], nCol))
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Please make sure the gaussian fit was done correctly.")

    def graphOnePeakLFitPos(self):
        """This method graphs the Lattice fit position for one peak.
        """
        x = self.getVoltage()
        y = self.LPosData
        xLabel = 'Voltage'
        yLabel = 'L Constant (\u00c5)'
        name = 'Lattice - Position (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def graphTwoPeakLFitPos1(self):
        """This method graphs the peak one Lattice fit position for two peak.
        """
        x = self.getVoltage()
        y = self.LPos1Data
        xLabel = 'Voltage'
        yLabel = 'L Constant'
        name = 'Lattice - Position #1 (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def graphTwoPeakLFitPos2(self):
        """This method graphs the peak two Lattice fit position for two peak.
        """
        x = self.getVoltage()
        y = self.LPos2Data
        xLabel = 'Voltage'
        yLabel = 'L Constant'
        name = 'Lattice - Position #2 (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def doLFitPercentChange(self):
        """This function finds the percentage change of the lattice, depending on the peak.
        """
        try:
            self.LPosPrcChangeData = []

            if self.dockedOpt.onePeakStat == True:
                for i in range(0, len(self.LPosData)):
                    pctChangeData = ((self.LPosData[i] - self.LPosData[0]) / self.LPosData[0]) * 100
                    self.LPosPrcChangeData.append(pctChangeData)

            elif self.dockedOpt.twoPeakStat == True:
                self.LPos1PrcChangeData = []
                self.LPos2PrcChangeData = []
                for i in range(0, len(self.LPos1Data)):
                    pctChangeData = ((self.LPos1Data[i] - self.LPos1Data[0]) / self.LPos1Data[0]) * 100
                    self.LPos1PrcChangeData.append(pctChangeData)

                for i in range(0, len(self.LPos2Data)):
                    pctChangeData = ((self.LPos2Data[i] - self.LPos2Data[0]) / self.LPos2Data[0]) * 100
                    self.LPos2PrcChangeData.append(pctChangeData)
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Something went wrong while doing the percentage change"
                                                            "lattice fit. Make sure the lattice fit was "
                                                            "done correctly.")

    def percentageChangeLConstantOnePeak(self):
        """This method graphs the lattice %-change for one peak.
        """
        x = self.getVoltage()
        y = self.LPosPrcChangeData
        xLabel = 'Voltage'
        yLabel = '%-Change'
        name = 'Lattice %-Change (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def percentageChangeLConstantPeakOne(self):
        """This method graphs the peak one lattice %-change for two peak.
         """
        x = self.getVoltage()
        y = self.LPos1PrcChangeData
        xLabel = 'Voltage'
        yLabel = '%-Change'
        name = 'Lattice %-Change #1 (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def percentageChangeLConstantPeakTwo(self):
        """This method graphs the peak two lattice %-change for two peak.
        """
        x = self.getVoltage()
        y = self.LPos2PrcChangeData
        xLabel = 'Voltage'
        yLabel = '%-Change'
        name = 'Lattice %-Change #2 (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def EachFitDataReport(self):
        try:
            if self.dockedOpt.gausFitStat == True:
                selectedFilters = ".txt"
                reportFile, reportFileFilter = QFileDialog.getSaveFileName(self.myMainWindow, "Save Report", None, selectedFilters)

                if reportFile != "":
                    reportFile += reportFileFilter
                    _, nCol = self.dockedOpt.fileInfo()
                    header = "#Bin "

                    i = 1
                    while i <= nCol:
                        header += str(i)+" "
                        i += 1

                    scanNum = self.readSpec.scan
                    comment = "#C PVvalue #" + scanNum + "\n"
                    if self.dockedOpt.onePeakStat == True:
                        np.savetxt(reportFile, self.binFitData, fmt=str('%f'), header=header, comments=comment)
                    elif self.dockedOpt.twoPeakStat == True:
                        np.savetxt(reportFile, self.binFitData, fmt=str('%-14.6f'), delimiter=" ", header=header, comments=comment)
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Make sure the gaussian fit was done properly, before "
                                                            "exporting the report again.")





