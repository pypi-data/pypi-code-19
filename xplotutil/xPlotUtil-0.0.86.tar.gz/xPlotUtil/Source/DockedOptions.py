#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.

#C In some methods LFit or L refer to the Lattice Constant not RLU.
"""

# ---------------------------------------------------------------------------------------------------------------------#
from __future__ import unicode_literals

import gc
import os

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pylab import *
from spec2nexus.spec import SpecDataFile

from xPlotUtil.Source.ReadSpecFile import ReadSpec


# ---------------------------------------------------------------------------------------------------------------------#


class DockedOption(QDockWidget):
    """Sets up the docked widget main options. """

    def __init__ (self, parent=None):
        super(DockedOption, self).__init__(parent)
        self.fileName = None  # PVvalue file

        # Initializing other classes
        self.myMainWindow = parent
        self.readSpec = ReadSpec(self)
        self.gausFit = self.readSpec.gausFit
        self.algebraExp = self.gausFit.algebraExp

        # Keeps track of when the function has been apply
        self.onePeakStat = False
        self.twoPeakStat = False
        self.fileOpened = False

        self.gausFitStat = False
        self.LFitStat = False
        self.normalizingStat = False
        self.algebraicExpStat = False


        self.TT = [] # 2D array where raw data is stored

    # ----------------------------------Main Option Functions----------------------------------------------------------#
    def DockMainOptions(self):
        """Function that creates the dockWidget for the Main options.
        """

        self.mainOptions = QDockWidget("Main Options", self)
        self.mainOptions.setFloating(False)
        self.mainOptions.setMaximumWidth(320)
        self.mainOptions.setMinimumWidth(320)
        self.mainOptions.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)

        layout = QFormLayout()
        FileHLayout = QHBoxLayout()
        PVLayout = QHBoxLayout()
        BtnLayout = QHBoxLayout()
        self.dataDockedWidget = QWidget()

        self.FileNameRdOnlyBox()
        self.BrowseButton()
        self.GraphDataButton()
        self.SpecDataValueList()
        self.DataGraphingRawOptionsTree()

        FileHLayout.addWidget(self.fileNameLabel)
        FileHLayout.addWidget(self.rdOnlyFileName)
        FileHLayout.addStretch(1)
        FileHLayout.addWidget(self.BrowseBtn)

        PVLayout.addWidget(self.pvLabel)
        PVLayout.addWidget(self.rdOnlyScanSelected)
        PVLayout.addStretch(1)

        BtnLayout.addStretch(1)
        BtnLayout.addWidget(self.GraphDataBtn)

        layout.addRow(FileHLayout)
        layout.addRow(PVLayout)
        layout.setVerticalSpacing(20)
        layout.addRow(self.specDataList)
        layout.addRow(self.graphingOptionsTree)
        layout.addRow(BtnLayout)
        self.dataDockedWidget.setLayout(layout)
        self.mainOptions.setWidget(self.dataDockedWidget)

        # Adding the docked widget to the main window
        self.myMainWindow.addDockWidget(Qt.RightDockWidgetArea, self.mainOptions)

    def restoreMainOptions(self):
        """This method displays the main options again, if it's not visible.
        """
        if self.mainOptions.isVisible() == False:
            self.mainOptions.show()

    def FileNameRdOnlyBox(self):
        """This method contains two QLineEdit boxes, set to read only that display the spec file
        and PVvalue files opened.
        """
        # Spec file is display
        self.rdOnlyFileName = QLineEdit()
        self.rdOnlyFileName.setReadOnly(True)
        self.rdOnlyFileName.setTextMargins(0, 0, 10, 0)
        self.rdOnlyFileName.setFixedWidth(125)

        # PVvalue file is displayed
        self.rdOnlyScanSelected = QLineEdit()
        self.rdOnlyScanSelected.setReadOnly(True)
        self.rdOnlyScanSelected.setTextMargins(0, 0, 10, 0)
        self.rdOnlyScanSelected.setFixedWidth(250)

        # Spec Label
        self.fileNameLabel = QLabel()
        self.fileNameLabel.setText("Spec File: ")

        # PvValue label
        self.pvLabel = QLabel()
        self.pvLabel.setText("Scan: ")

    def BrowseButton(self):
        """Function that creates a browse button, connects to the openFile() method.
        """
        self.BrowseBtn = QPushButton('Browse', self)
        self.BrowseBtn.clicked.connect(self.readSpec.openSpecFile)
        self.BrowseBtn.setStatusTip("Browse and open an existing file")

    def GraphDataButton(self):
        """Function that creates a graph button, connects to the GraphData() method.
        """
        self.GraphDataBtn = QPushButton('Graph', self)
        self.GraphDataBtn.setStatusTip("Graphs the checked boxes")
        self.GraphDataBtn.clicked.connect(self.plottingFits)

    def SpecDataValueList(self):
        """This list displays the values/scans of the spec file.
        """
        self.specDataList = QListWidget()
        self.specDataList.itemDoubleClicked.connect(self.openPVFile)

    # ----------------------------------Opening PVvalue file and such--------------------------------------------------#
    def openPVFile(self):
        """This method calls on the openDialog if no file has previously been open or asks
         the user if it wants to open a new file.
         """
        if self.fileOpened == False:
            self.readSpec.currentScan()
        elif self.fileOpened == True:
            response = self.msgApp("New PVvalue File", "Would you like to open the new selected PVvalue file?")
            if response == "Y":
                self.readSpec.currentScan()

    def openFile(self, fileName):
        """This method allows the user to open a new PVvalue file. It also resets some attributes to
        their original value to enable the fits and other functionality.
        """
        self.fileName = fileName

        # Makes sure a file has been opened before changing attributes to orginal value
        if os.path.isfile(self.fileName) == True:
            self.mainOptions.close()
            self.DockMainOptions()
            self.specFileInfo()
            self.myMainWindow.LatticeFitAction.setEnabled(False)
            self.specDataList.setCurrentRow(self.readSpec.currentRow)
            self.onePeakStat = False
            self.twoPeakStat = False
            self.normalizingStat = False
            self.gausFitStat = False
            self.LFitStat = False
            self.algebraicExpStat = False
            self.rdOnlyScanSelected.setStatusTip(self.fileName)
            self.rdOnlyScanSelected.setText(self.fileName)
            self.fileOpened = True
            self.gausFit.continueGraphingEachFit = True
            self.loadFile()

    def loadFile(self):
        """This method is used to load the PVvalue file into an array. Displays error message, if file could
        not be loaded into 2d array.
        """
        try:
            data = np.loadtxt(open(self.fileName))
            nRow = data.shape[0]  # Gets the number of rows
            nCol = data.shape[1]  # Gets the number of columns
            x = 0
            for f in range(nCol):
                if (np.mean(data[:, f]) == 0):
                    break
                else:
                    x += 1
            nCol = x

            self.TT = np.zeros((nRow, nCol))

            for i in range(nCol):
                self.TT[:, i] = data[:, i]
        except:
            QMessageBox.warning(self.myMainWindow, "Warning", "Please make sure the PVvalue file follows the "
                                                              "appropriate format. There should be an equal amount of "
                                                              "rows and columns.")
            self.mainOptions.close()
            self.DockMainOptions()
            self.specFileInfo()
            self.fileOpened = False

    def fileInfo(self):
        """ This method returns the points (rows) and bins (columns) from the raw data file sheet.
        :return: Number of points and bins
        """
        nRow = self.TT.shape[0]  # Gets the number of rows
        nCol = self.TT.shape[1]

        return nRow, nCol

    def specFileInfo(self):
        """This method sets the name, status tip for the spec file, and loads the scan to the list
        from the spec file.
        """
        self.rdOnlyFileName.setText(self.readSpec.specFileName)
        self.rdOnlyFileName.setStatusTip(self.readSpec.specFileName)
        specFile = SpecDataFile(self.readSpec.specFileName)
        self.readSpec.loadScans(specFile.scans)

    # ------------------------------------What Peak?-------------------------------------------------------------------#
    def WhichPeakGaussianFit(self):
        """This function asks the user for the amount of peaks. Then calls on the appropriate dialog, depending on
        the peak number.
        """
        if self.FileError() == False and self.gausFitStat == False:
            chosePeak = self.PeakDialog()
            if (chosePeak == 'One'):
                self.gausFit.gausOnePeakInputDialog()
            elif (chosePeak == 'Two'):
                self.gausFit.gausTwoPeakInputDialog()

    def PeakDialog(self):
        """Method that creates a dialog, so that the user can peak the number of peaks.
        :return: Number of peaks
        """
        peakList = ['One', 'Two']
        text, ok = QInputDialog.getItem(self, 'Peak Fit', 'Choose Peak: ', peakList)

        if ok:
            return text

    # ----------------------------------Misc. Functions----------------------------------------------------------------#
    def msgApp(self, title, msg):
        """Generic message box
        :param title: Title displayed in message box
        :param msg: message display and box
        """
        userInfo = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No)

        if userInfo == QMessageBox.Yes:
            return "Y"
        if userInfo == QMessageBox.No:
            return "N"
        self.close()

    def resetxPlot(self):
        """This function basically resets xPlot Util. It closes and removes the grap[hs created and
        changes various attributes to their original value to enable fits and other functionality.
        """
        self.mainOptions.close()
        self.DockMainOptions()
        self.gausFit.continueGraphingEachFit = True

        self.myMainWindow.LatticeFitAction.setEnabled(False)

        self.readSpec.specFileOpened = False
        self.readSpec.specFileName = None

        self.fileName = None
        self.onePeakStat = False
        self.twoPeakStat = False
        self.fileOpened = False
        self.gausFitStat = False
        self.LFitStat = False
        self.normalizingStat = False
        self.algebraicExpStat = False

        # Closes and removes the graphs created
        index = len(self.myMainWindow.canvasArray)
        i = 0
        j = 0
        while i < index:
            self.myMainWindow.canvasArray.pop(j)
            self.myMainWindow.figArray.pop(j)
            gc.collect()
            self.myMainWindow.tabWidget.removeTab(j)
            i += 1

    def FileError(self):
        """This method checks that a PVvalue file has been opened or selected.
        :return: truth value of PVvalue file error
        """
        if self.fileName is "" or self.fileName is None:
            return True
        else:
            if os.path.isfile(self.fileName) == False:
                return True
            else:
                if self.rdOnlyScanSelected.text() == "":
                    QMessageBox.warning(self, "Error - No Scan Selected", "Please select a scan.")
                else:
                    return False

    # --------------------------------Tree Graphing Options------------------------------------------------------------#
    def DataGraphingRawOptionsTree(self):
        """This method initializes the tree branch for the raw data graphing options.
        """
        # Initialization of the main tree
        self.graphingOptionsTree = QTreeWidget()
        self.graphingOptionsTree.setHeaderLabel("Graphing Options")

        """Initialization of the top level Fits"""
        # Raw Data Top Branch
        self.rawDataTopBranch = QTreeWidgetItem()
        self.rawDataTopBranch.setText(0, "Raw Data")
        self.rawDataTopBranch.setFlags(self.rawDataTopBranch.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

        """Raw Data Children"""
        # Color Graph
        self.colorGraphBranch = QTreeWidgetItem(self.rawDataTopBranch)
        self.colorGraphBranch.setText(0, "Color Graph")
        self.colorGraphBranch.setFlags(self.colorGraphBranch.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        self.colorGraphBranch.setCheckState(0, Qt.Unchecked)

        # Line Graph
        self.lineGraphBranch = QTreeWidgetItem(self.rawDataTopBranch)
        self.lineGraphBranch.setText(0, "Line Graph")
        self.lineGraphBranch.setFlags(self.lineGraphBranch.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        self.lineGraphBranch.setCheckState(0, Qt.Unchecked)

        self.graphingOptionsTree.addTopLevelItem(self.rawDataTopBranch)

    def DataGraphingAlgebraicExpOptionsTree(self):
        """This method initializes the tree branch for the algebraic expression graphing options.
        """
        if self.algebraicExpStat == False and self.fileOpened == True:
            # Algebraic Expressions Top Branch
            self.algebraicExpTopBranch = QTreeWidgetItem()
            self.algebraicExpTopBranch.setText(0, "Algebraic Expressions")
            self.algebraicExpTopBranch.setFlags(self.algebraicExpTopBranch.flags() | Qt.ItemIsTristate |
                                                Qt.ItemIsUserCheckable)

            # Single Value Index
            self.singleValueIndexBranch = QTreeWidgetItem(self.algebraicExpTopBranch)
            self.singleValueIndexBranch.setText(0, "Single Value Index")
            self.singleValueIndexBranch.setFlags(self.singleValueIndexBranch.flags() | Qt.ItemIsTristate |
                                                 Qt.ItemIsUserCheckable)
            self.singleValueIndexBranch.setCheckState(0, Qt.Unchecked)

            # Th2Th Graph
            self.th2ThBranch = QTreeWidgetItem(self.algebraicExpTopBranch)
            self.th2ThBranch.setText(0, "\u03B82\u03B8")
            self.th2ThBranch.setFlags(self.th2ThBranch.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            self.th2ThBranch.setCheckState(0, Qt.Unchecked)

            # Weighting Graph
            self.weightingBranch = QTreeWidgetItem(self.algebraicExpTopBranch)
            self.weightingBranch.setText(0, "Weighting")
            self.weightingBranch.setFlags(self.weightingBranch.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            self.weightingBranch.setCheckState(0, Qt.Unchecked)

            self.algebraicExpStat = True
            self.algebraExp.singularValueDecomposition()
            self.graphingOptionsTree.addTopLevelItem(self.algebraicExpTopBranch)

    def GraphingGaussianOptionsTree(self):
        """This method initializes the tree branch for the gaussian fit graphing options.
        """
        # Gaussian Fit Top Branch
        self.gaussianFitTopBranch = QTreeWidgetItem()
        self.gaussianFitTopBranch.setText(0, "Gaussian Fit")
        self.gaussianFitTopBranch.setFlags(self.gaussianFitTopBranch.flags() | Qt.ItemIsTristate |
                                           Qt.ItemIsUserCheckable)

        if self.twoPeakStat == True:
            """Gaussian Fit Children"""
            # Peak One
            self.peakOneBranch = QTreeWidgetItem(self.gaussianFitTopBranch)
            self.peakOneBranch.setText(0, "Peak #1")
            self.peakOneBranch.setFlags(self.peakOneBranch.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            # Peak Two
            self.peakTwoBranch = QTreeWidgetItem(self.gaussianFitTopBranch)
            self.peakTwoBranch.setText(0, "Peak #2")
            self.peakTwoBranch.setFlags(self.peakTwoBranch.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            """Peak One Tree Branch Children"""
            # Amplitude Peak One
            self.amplitudePeakOne = QTreeWidgetItem(self.peakOneBranch)
            self.amplitudePeakOne.setFlags(self.amplitudePeakOne.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.amplitudePeakOne.setText(0, "Amplitude")
            self.amplitudePeakOne.setCheckState(0, Qt.Unchecked)

            # Position Peak One
            self.positionPeakOne = QTreeWidgetItem(self.peakOneBranch)
            self.positionPeakOne.setFlags(self.positionPeakOne.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.positionPeakOne.setText(0, "Position")
            self.positionPeakOne.setCheckState(0, Qt.Unchecked)

            # Width Peak One
            self.widthPeakOne = QTreeWidgetItem(self.peakOneBranch)
            self.widthPeakOne.setFlags(self.widthPeakOne.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.widthPeakOne.setText(0, "Width")
            self.widthPeakOne.setCheckState(0, Qt.Unchecked)

            # Amplitude x Width Peak One
            self.ampXWidPeakOne = QTreeWidgetItem(self.peakOneBranch)
            self.ampXWidPeakOne.setFlags(self.positionPeakOne.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.ampXWidPeakOne.setText(0, "Amplitude x Width")
            self.ampXWidPeakOne.setCheckState(0, Qt.Unchecked)

            """Peak Two Tree Branch Children"""
            # Amplitude Peak Two
            self.amplitudePeakTwo = QTreeWidgetItem(self.peakTwoBranch)
            self.amplitudePeakTwo.setFlags(self.amplitudePeakTwo.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.amplitudePeakTwo.setText(0, "Amplitude")
            self.amplitudePeakTwo.setCheckState(0, Qt.Unchecked)

            # Position Peak Two
            self.positionPeakTwo = QTreeWidgetItem(self.peakTwoBranch)
            self.positionPeakTwo.setFlags(self.positionPeakTwo.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.positionPeakTwo.setText(0, "Position")
            self.positionPeakTwo.setCheckState(0, Qt.Unchecked)

            # Width Peak Two
            self.widthPeakTwo = QTreeWidgetItem(self.peakTwoBranch)
            self.widthPeakTwo.setFlags(self.widthPeakTwo.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.widthPeakTwo.setText(0, "Width")
            self.widthPeakTwo.setCheckState(0, Qt.Unchecked)

            # Amplitude x Width Peak Two
            self.ampXWidPeakTwo = QTreeWidgetItem(self.peakTwoBranch)
            self.ampXWidPeakTwo.setFlags(self.ampXWidPeakTwo.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.ampXWidPeakTwo.setText(0, "Amplitude x Width")
            self.ampXWidPeakTwo.setCheckState(0, Qt.Unchecked)

        elif self.onePeakStat == True:
            """Children of Gaussian Branch"""
            # Amplitude
            self.onePeakAmplitude = QTreeWidgetItem(self.gaussianFitTopBranch)
            self.onePeakAmplitude.setFlags(self.onePeakAmplitude.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.onePeakAmplitude.setText(0, "Amplitude")
            self.onePeakAmplitude.setCheckState(0, Qt.Unchecked)

            # Position
            self.onePeakPosition = QTreeWidgetItem(self.gaussianFitTopBranch)
            self.onePeakPosition.setFlags(self.onePeakPosition.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.onePeakPosition.setText(0, "Position")
            self.onePeakPosition.setCheckState(0, Qt.Unchecked)

            # Width Peak One
            self.onePeakWidth = QTreeWidgetItem(self.gaussianFitTopBranch)
            self.onePeakWidth.setFlags(self.onePeakWidth.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.onePeakWidth.setText(0, "Width")
            self.onePeakWidth.setCheckState(0, Qt.Unchecked)

            # Amplitude x Width Peak One
            self.onePeakAmpxWid = QTreeWidgetItem(self.gaussianFitTopBranch)
            self.onePeakAmpxWid.setFlags(self.onePeakAmpxWid.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            self.onePeakAmpxWid.setText(0, "Amplitude x Width")
            self.onePeakAmpxWid.setCheckState(0, Qt.Unchecked)

        #Adding the top branch to the graphing options tree
        self.graphingOptionsTree.addTopLevelItem(self.gaussianFitTopBranch)

        self.myMainWindow.LatticeFitAction.setEnabled(True)


    def GraphingLatticeOptionsTree(self):
        """This method initializes the tree branch for the lattice fit graphing options"""
        if self.LFitStat == False and self.gausFitStat == True:
            # L Fit Top Branch
            self.LFitTopBranch = QTreeWidgetItem()
            self.LFitTopBranch.setText(0, "Lattice Fit")
            self.LFitTopBranch.setFlags(self.LFitTopBranch.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            """L FitData Children, depending on the peak"""
            if self.onePeakStat == True:
                # RLU Graph
                self.onePeakRLU = QTreeWidgetItem(self.LFitTopBranch)
                self.onePeakRLU.setText(0, "Lattice")
                self.onePeakRLU.setFlags(self.onePeakRLU.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                self.onePeakRLU.setCheckState(0, Qt.Unchecked)

                # %Change Graph
                self.onePeakRLUPrcChange = QTreeWidgetItem(self.LFitTopBranch)
                self.onePeakRLUPrcChange.setText(0, "Lattice %-Change")
                self.onePeakRLUPrcChange.setFlags(self.onePeakRLUPrcChange.flags() | Qt.ItemIsTristate |
                                                  Qt.ItemIsUserCheckable)
                self.onePeakRLUPrcChange.setCheckState(0, Qt.Unchecked)

            elif self.twoPeakStat == True:
                # Peak One
                peakOneBranch = QTreeWidgetItem(self.LFitTopBranch)
                peakOneBranch.setText(0, "Peak #1")
                peakOneBranch.setFlags(peakOneBranch.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

                # Peak Two
                peakTwoBranch = QTreeWidgetItem(self.LFitTopBranch)
                peakTwoBranch.setText(0, "Peak #2")
                peakTwoBranch.setFlags(peakTwoBranch.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

                # RLU Graph Peak one
                self.RLUPeakOne = QTreeWidgetItem(peakOneBranch)
                self.RLUPeakOne.setText(0, "Lattice")
                self.RLUPeakOne.setFlags(self.RLUPeakOne.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                self.RLUPeakOne.setCheckState(0, Qt.Unchecked)

                # %Change Graph Peak One
                self.RLUPrcChangePeakOne = QTreeWidgetItem(peakOneBranch)
                self.RLUPrcChangePeakOne.setText(0, "Lattice %-Change")
                self.RLUPrcChangePeakOne.setFlags(self.RLUPrcChangePeakOne.flags() | Qt.ItemIsTristate |
                                                  Qt.ItemIsUserCheckable)
                self.RLUPrcChangePeakOne.setCheckState(0, Qt.Unchecked)

                # RLU Graph Peak two
                self.RLUPeakTwo = QTreeWidgetItem(peakTwoBranch)
                self.RLUPeakTwo.setText(0, "Lattice")
                self.RLUPeakTwo.setFlags(self.RLUPeakTwo.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                self.RLUPeakTwo.setCheckState(0, Qt.Unchecked)

                # %Change Graph Peak two
                self.RLUPrcChangePeakTwo = QTreeWidgetItem(peakTwoBranch)
                self.RLUPrcChangePeakTwo.setText(0, "Lattice")
                self.RLUPrcChangePeakTwo.setFlags(self.RLUPrcChangePeakTwo.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                self.RLUPrcChangePeakTwo.setCheckState(0, Qt.Unchecked)

            # Adding the top branch to the graphing options tree
            self.graphingOptionsTree.addTopLevelItem(self.LFitTopBranch)
            self.gausFit.doLFit()
            self.gausFit.doLFitPercentChange()
            self.LFitStat = True

    # ------------------------------------------Plotting Methods-------------------------------------------------------#
    def plottingFits(self):
        """This function calls on the appropriate method to plot the graphs, taking into account the fit and
        number of peaks.
        """
        try:
            if self.FileError() == False:
                # Raw Data
                if self.colorGraphBranch.checkState(0) == 2:
                    self.myMainWindow.PlotColorGraphRawData()
                    self.colorGraphBranch.setCheckState(0, 0)
                if self.lineGraphBranch.checkState(0) == 2:
                    self.myMainWindow.PlotLineGraphRawData()
                    self.lineGraphBranch.setCheckState(0, 0)

                if self.algebraicExpStat == True:
                    if self.singleValueIndexBranch.checkState(0) == 2:
                        self.algebraExp.plotSingleValueIndex()
                        self.singleValueIndexBranch.setCheckState(0, 0)
                    if self.th2ThBranch.checkState(0) == 2:
                        self.algebraExp.plotTh2ThExp()
                        self.th2ThBranch.setCheckState(0, 0)
                    if self.weightingBranch.checkState(0) == 2:
                        self.algebraExp.plotWeightingExp()
                        self.weightingBranch.setCheckState(0, 0)
                # Gaussian Fit
                if self.onePeakStat == True:
                    self.graphingOnePeak()
                elif self.twoPeakStat == True:
                    self.graphingTwoPeak()
        except:
            QMessageBox.warning(self.myMainWindow, "Warning", "Please make sure the PVvalue file belongs to the spec"
                                                              " file and/or follows the appropriate format. "
                                                              "Reopen the PVvalue file.")

    def graphingOnePeak(self):
        """This method calls on the appropriate method to plot one peak graphs.
        """
        try:
            if self.onePeakAmplitude.checkState(0) == 2:
                self.gausFit.graphOnePeakAmplitude()
                self.onePeakAmplitude.setCheckState(0, 0)
            if self.onePeakPosition.checkState(0) == 2:
                self.gausFit.graphOnePeakPosition()
                self.onePeakPosition.setCheckState(0, 0)
            if self.onePeakWidth.checkState(0) == 2:
                self.gausFit.graphOnePeakWidth()
                self.onePeakWidth.setCheckState(0, 0)
            if self.onePeakAmpxWid.checkState(0) == 2:
                self.gausFit.graphOnePeakAmplitudeXWidth()
                self.onePeakAmpxWid.setCheckState(0, 0)

            # Lattice Fit
            if self.LFitStat == True:
                if self.onePeakRLU.checkState(0) == 2:
                    self.gausFit.graphOnePeakLFitPos()
                    self.onePeakRLU.setCheckState(0, 0)
                if self.onePeakRLUPrcChange.checkState(0) == 2:
                    self.gausFit.percentageChangeLConstantOnePeak()
                    self.onePeakRLUPrcChange.setCheckState(0, 0)
        except:
            QMessageBox.warning(self.myMainWindow, "Warning", "Please make sure to the fitting was correct and/or the "
                                                              "files follow the correct format. "
                                                              "Reopen the PVvalue file")

    def graphingTwoPeak(self):
        """This method calls on the appropriate method to plot two peak graphs.
        """
        try:
            # Peak One
            if self.amplitudePeakOne.checkState(0) == 2:
                self.gausFit.graphTwoPeakAmplitude1()
                self.amplitudePeakOne.setCheckState(0, 0)
            if self.positionPeakOne.checkState(0) == 2:
                self.gausFit.graphTwoPeakPosition1()
                self.positionPeakOne.setCheckState(0, 0)
            if self.widthPeakOne.checkState(0) == 2:
                self.gausFit.graphTwoPeakWidth1()
                self.widthPeakOne.setCheckState(0, 0)
            if self.ampXWidPeakOne.checkState(0) == 2:
                self.gausFit.graphTwoPeakAmplitudeXWidth1()
                self.ampXWidPeakOne.setCheckState(0, 0)

            # Peak Two
            if self.amplitudePeakTwo.checkState(0) == 2:
                self.gausFit.graphTwoPeakAmplitude2()
                self.amplitudePeakTwo.setCheckState(0, 0)
            if self.positionPeakTwo.checkState(0) == 2:
                self.gausFit.graphTwoPeakPosition2()
                self.positionPeakTwo.setCheckState(0, 0)
            if self.widthPeakTwo.checkState(0) == 2:
                self.gausFit.graphTwoPeakWidth2()
                self.widthPeakTwo.setCheckState(0, 0)
            if self.ampXWidPeakTwo.checkState(0) == 2:
                self.gausFit.graphTwoPeakAmplitudeXWidth2()
                self.ampXWidPeakTwo.setCheckState(0, 0)

            # Lattice Fit
            if self.LFitStat == True:
                if self.RLUPeakOne.checkState(0) == 2:
                    self.gausFit.graphTwoPeakLFitPos1()
                    self.RLUPeakOne.setCheckState(0, 0)
                if self.RLUPrcChangePeakOne.checkState(0) == 2:
                    self.gausFit.percentageChangeLConstantPeakOne()
                    self.RLUPrcChangePeakOne.setCheckState(0, 0)
                if self.RLUPeakTwo.checkState(0) == 2:
                    self.gausFit.graphTwoPeakLFitPos2()
                    self.RLUPeakTwo.setCheckState(0, 0)
                if self.RLUPrcChangePeakTwo.checkState(0) == 2:
                    self.gausFit.percentageChangeLConstantPeakTwo()
                    self.RLUPrcChangePeakTwo.setCheckState(0, 0)
        except:
            QMessageBox.warning(self.myMainWindow, "Warning", "Please make sure to the fitting was correct and/or the"
                                                              "files follow the correct format. "
                                                              "Reopen the PVvalue")





