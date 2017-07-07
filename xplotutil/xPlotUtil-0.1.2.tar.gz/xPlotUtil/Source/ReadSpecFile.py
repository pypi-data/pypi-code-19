#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.

#C In some methods LFit or L refer to the Lattice Constant not RLU
"""

# ---------------------------------------------------------------------------------------------------------------------#
from __future__ import unicode_literals

import os

from PyQt5.QtWidgets import *
from pylab import *

from xPlotUtil.Source.GaussianFit import GaussianFitting


# ---------------------------------------------------------------------------------------------------------------------#


class ReadSpec:
    """Loads spec file and gets appropriate information from it for a certain PVvalue/scan
    """

    def __init__ (self, parent=None):
        self.dockedOpt = parent
        self.myMainWindow = self.dockedOpt.myMainWindow
        self.gausFit = GaussianFitting(self)
        self.algebraExp = self.gausFit.algebraExp
        self.specFileOpened = False
        self.specFileName = None

        # Initializing lattice information
        self.lElement = 0
        self.lMax = 0
        self.lMin = 0

    def openSpecFile(self):
        """This method calls on the file dialog to open the spec file if no previous spec file has been open. Otherwise
        it asks the user if he wants to open a new spec file.
        """
        if self.specFileOpened == False:
            self.openSpecDialog()
        elif self.specFileOpened == True:
            response = self.dockedOpt.msgApp("Open New Spec File", "Would you like to open a new spec file?")
            if response == "Y":
                self.openSpecDialog()

    def getPVNumKey(self, text):
        h = text.split('.')
        return int(h[1])

    def openSpecDialog(self):
        """This method creates a file dialog to open the spec file. Once the file has been open it resets
        various attributes to their original value to initialize/reestablish functionality.
        """
        try:
            selectedFilter = "Spec files (*.spec)"
            self.specFileName, self.specFileFilter = QFileDialog.getOpenFileName(self.myMainWindow, "Open Spec File",
                                                                                 None, selectedFilter)
            # Makes sure a file has been opened
            if os.path.isfile(self.specFileName):
                # Gets the PVvalue files in the directory
                self.specDirectory = os.path.dirname(self.specFileName)
                self.PvFiles = [f for f in os.listdir(self.specDirectory) if f.find("PVvalue") == 0]
                self.PvFiles.sort(key=self.getPVNumKey)

                self.dockedOpt.mainOptions.close()
                self.dockedOpt.DockMainOptions()
                self.dockedOpt.gausFitStat = False
                self.dockedOpt.LFitStat = False
                self.dockedOpt.normalizingStat = False
                self.algebraicExpStat = False
                self.dockedOpt.specFileInfo()
                self.specFileOpened = True
                self.dockedOpt.fileOpened = False
                self.continueGraphingEachFit = True
                self.myMainWindow.LatticeFitAction.setEnabled(False)
                self.myMainWindow.showProgress("Spec file opened")
        except:
             print("Please make sure the directory follows the proper format, including the spec and PVvalue files.")

    def loadScans(self, scans):
        """Loads the scan into the specDataList
        :param scans: list of scans provided using spec2nexus.spec
        """
        self.scans = scans
        scanKeys = self.scans.keys()
        scanKeys.sort(key=int)  # Sorts the scans in order lowest-greater
        for scan in scanKeys:
            for file in self.PvFiles:
                f = file.split('.')
                if f[1] == scan:
                    PValue = 'PVvalue #' + str(scans[scan].scanNum)
                    self.dockedOpt.specDataList.addItem(PValue)

    def currentScan(self):
        """This method calls on the open file dialog to open the PVvalue file. It gets the required data
        from the  spec file for the PVvalue/scan.
        """
        scan = self.PvFiles[self.dockedOpt.specDataList.currentRow()].split(".")
        self.scan = scan[1]
        self.currentRow = self.dockedOpt.specDataList.currentRow()

        if self.specDirectory.find("/") == 0:
            fileName = self.specDirectory + "/" + self.PvFiles[self.currentRow]
        elif self.specDirectory.find("\\") == 0:
            fileName = self.specDirectory + "\\" + self.PvFiles[self.currentRow]

        self.dockedOpt.openFile(fileName)

        # Making sure the file of the PVvalue has been opened
        if self.dockedOpt.fileOpened == True:
            try:
                if os.path.isfile(self.dockedOpt.fileName):
                    self.normalizers = [] # Array that will contain possible normalizers
                    self.L = []  # Array of the RLU

                    self.L = self.scans[self.scan].data["L"]
                    self.lMin = self.L[0]
                    self.lMax = self.L[-1]

                    k = self.scans[self.scan].G["G1"].split(" ")
                    self.lElement = float(k[2])

                    # Gets possible normalizer values
                    for key in self.scans[self.scan].data.keys():
                        if key.find("Ion_Ch_") == 0:
                            self.normalizers.append(key)
                    self.normalizers.sort()
            except:
                print("Please make sure the PVValue has the correct information in the spec file.")

    ''' # Current using the L from the spec file
    def getRLU(self):
        """This function gets the Lattice for the particular file, using the lattice max, lattice min and the
        number of points on each column for the raw data. """
        nRow, nCol = self.dockedOpt.fileInfo()  # nRows = points || nCol = bins
        if nRow != 0:
            adjustment = (self.lMax - self.lMin)/nRow
            self.L = [] #  Initializing Lattice array
            self.L.append(self.lMin)
            RLU = self.lMin
            count = 1
            while count < nRow:
                RLU += round(adjustment, 4)
                self.L.append(round(RLU, 5))
                count += 1
    '''

    def NormalizerDialog(self):
        """This method creates a dialog with dynamically created radio buttons from the spec file, which allow the
        user to pick which chamber was used to normalize.
        """
        if self.dockedOpt.normalizingStat == False and self.dockedOpt.FileError() == False :
            self.normalizeDialog = QDialog(self.myMainWindow)
            dialogBox = QVBoxLayout()
            buttonLayout = QHBoxLayout()
            vBox = QVBoxLayout()

            groupBox = QGroupBox("Select normalizer")
            self.buttonGroup = QButtonGroup(groupBox)

            for norm in self.normalizers:
                normalizerRB = QRadioButton(norm)
                self.buttonGroup.addButton(normalizerRB, int(norm[-1]))
                vBox.addWidget(normalizerRB)

            groupBox.setLayout(vBox)

            ok = QPushButton("Ok")
            cancel = QPushButton("Cancel")

            cancel.clicked.connect(self.normalizeDialog.close)
            ok.clicked.connect(self.getNormalizer)

            buttonLayout.addWidget(cancel)
            buttonLayout.addStretch(1)
            buttonLayout.addWidget(ok)

            dialogBox.addWidget(groupBox)
            dialogBox.addLayout(buttonLayout)

            self.normalizeDialog.setWindowTitle("Normalize raw data")
            self.normalizeDialog.setLayout(dialogBox)
            self.normalizeDialog.resize(250, 250)
            self.normalizeDialog.exec_()

    def getNormalizer(self):
        """This function divides the raw data stored in array TT by the normalizer to normalize it.
        """
        try:
            if self.buttonGroup.checkedId() != -1:
                self.normalizeDialog.close()
                for norm in self.normalizers:
                    if norm.endswith(str(self.buttonGroup.checkedId())):
                        self.normalizer = self.scans[self.scan].data[norm]
                        self.normalizer = np.reshape(self.normalizer, (len(self.normalizer), 1))
                        self.dockedOpt.TT = np.divide(self.dockedOpt.TT, self.normalizer)
                        self.dockedOpt.normalizingStat = True
        except:
            QMessageBox.warning(self.myMainWindow, "Dimension Error", "Please make sure the selected normalizer "
                                                                      "has the same row dimension as the raw data.")

    def possibleRawDataLineGraphXAxis(self):
        """This function finds the possible x-axis for the raw data line graph. Also adds Bins to
        the list.
        :return: list of possible x-axis
        """
        linePlotXAxis = []
        for key in self.scans[self.scan].L:
            if key == 'L':
                linePlotXAxis.append(key)
                linePlotXAxis.append(str('Bins'))
                break
            else:
                linePlotXAxis.append(key)
        return linePlotXAxis

    def RawDataLineGraphXAxisDialog(self):
        """This method creates a dialog with dynamically created radio buttons from the spec file, which allow the
        user to pick which x-axis to use for the raw data line graph.
        """
        self.xAxisRawDataDialog = QDialog(self.myMainWindow)
        self.xAxisRawDataDialog.setModal(True)
        dialogBox = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        vBox = QVBoxLayout()

        groupBox = QGroupBox("Select x-axis")
        self.possibleRawDataXBtnGroup = QButtonGroup(groupBox)
        xAxis = self.possibleRawDataLineGraphXAxis()
        for x in xAxis:
            xRB = QRadioButton(x)
            self.possibleRawDataXBtnGroup.addButton(xRB)
            vBox.addWidget(xRB)
        groupBox.setLayout(vBox)

        ok = QPushButton("Ok")
        cancel = QPushButton("Cancel")

        cancel.clicked.connect(self.xAxisRawDataDialog.close)
        ok.clicked.connect(self.xAxisRawDataDialog.accept)

        buttonLayout.addWidget(cancel)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(ok)

        dialogBox.addWidget(groupBox)
        dialogBox.addLayout(buttonLayout)

        self.xAxisRawDataDialog.setWindowTitle("Raw data line graph x-axis")
        self.xAxisRawDataDialog.setLayout(dialogBox)
        self.xAxisRawDataDialog.resize(200, 100)
        self.xAxisRawDataDialog.exec_()

    def getRawDataLinePlotElements(self):
        """This function selects the x-axis depending on what the user selected, as well as other
        criteria for the raw data line graph. Returns a list of zeros if no radio button was selected.
        :return: list of elements to plot the raw data line graph
        """
        self.RawDataLineGraphXAxisDialog()

        if self.xAxisRawDataDialog.result() == self.xAxisRawDataDialog.Accepted and self.possibleRawDataXBtnGroup.checkedButton() != None:
            xAxis = self.possibleRawDataLineGraphXAxis()
            radioBtn = self.possibleRawDataXBtnGroup.buttons()

            # Gets the x-axis for the line graph
            i = 0
            for btn in radioBtn:
                if btn == self.possibleRawDataXBtnGroup.checkedButton():
                    if xAxis[i] == 'L':
                        x = self.scans[self.scan].data[xAxis[i]]
                        gTitle = 'Raw Data in RLU (Scan#: ' + self.scan + ')'
                        xLabel = 'RLU (Reciprocal Lattice Unit)'
                        statTip = 'Raw Data in RLU (Reciprocal Lattice Unit)'
                        tabName = 'Raw Data (RLU)'
                    elif xAxis[i] == 'Bins':
                        nRow, nCol = self.dockedOpt.fileInfo()
                        x = range(nRow)
                        gTitle = 'Raw Data in Bins (Scan#: ' + self.scan + ')'
                        xLabel = 'Points'
                        statTip = 'Raw Data in Bins'
                        tabName = 'Raw Data (Bins)'
                    else:
                        x = self.scans[self.scan].data[xAxis[i]]
                        gTitle = 'Raw Data in ' + xAxis[i] + ' (Scan#: ' + self.scan + ')'
                        xLabel = xAxis[i]
                        statTip = 'Raw Data in ' + xAxis[i]
                        tabName = 'Raw Data (' + xAxis[i] + ')'
                else:
                    i += 1
            self.xAxisRawDataDialog.close()
            return x, gTitle, xLabel, statTip, tabName
        else:
            self.xAxisRawDataDialog.close()
            return 0, 0, 0, 0, 0





