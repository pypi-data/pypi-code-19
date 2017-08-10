"""
***Source code of Normalizing STXM Project***

Using matplotlib inside QT

- Funtctions:
        - draw vertical lines (patches) on an plot
        - aplies a normalization function on the selected lines
        - using the numpy.mean() function as a first nonrmalization resource
        - 
        - 
        

"""

import os

from imageNorm import imageNorm # imports the module to normalize the image

from PyQt5 import QtCore, QtGui, uic, QtWidgets

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.widgets import  RectangleSelector
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

import sys

        
qtDesignerFile = "../data/stxmnorm.ui" # Enter file created by QTDesigner here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtDesignerFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MyApp, self).__init__()

        self.imageNorm = imageNorm() # instanciates the class to use its modules
        print "axes: ", self.imageNorm.axes        

        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.img_orig = None
        self.img = None
        self.imgplot = None
        self.caxes = None
        self.axes = None
        self.mouseispressed = None
        self.openfileformat = None
        self.pathssvfile = None

        self.canvas = None
        self.axes = None       
        self.figure = None                        
        self.fig_dict = {} # sets the list of figures of the GUI to empty
        self.fname = ''
        self.y0 = int(0)
        self.y1 = int(0)

##        self.fig = plt.figure()
##        self.axes = self.fig.add_subplot(111)

        ##        self.canvas = 0
##        self.image_list.itemClicked.connect(self.selectFigure)
        
        # Menu bar actions
        fileOpen = self.file_open
        fileOpen.triggered.connect(self.showDialog)        

        fileSave = self.file_save
        fileSave.triggered.connect(self.saveProject)

        fileExport = self.file_export
        fileExport.triggered.connect(self.exportImage)

        editRemoveFigure = self.edit_removefigure
        editRemoveFigure.triggered.connect(self.removeFigure)

        editResetImage = self.edit_resetimage
        editResetImage.triggered.connect(self.resetImage)

##        # Buttons from QT
        """Normalize Image"""
        self.normalize_image.clicked.connect(self.normImage)
        
        """Clear Selections"""
        self.clear_selection.clicked.connect(self.clearSelection)        
##
##        """Shift Buttons"""
##        self.shift_right.clicked.connect(self.shiftLineRight)
##        self.shift_left.clicked.connect(self.shiftLineLeft)
##
##        """Select Line Button"""
##        self.select_line.clicked.connect(self.selectLine)
##                


    

    def showDialog(self):
        if self.fname != '':
            self.removeFigure()
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.environ['HOME'] )        
        self.fname = fname[0]
        
        self.figure = self.imageNorm.loadImage(self.fname) # always add 'self.' to call a member function (functions within a class)

        self.addFigure(self.fname)

     
    def addFigure(self, fname):
        self.canvas = FigureCanvas(self.figure) # send the figure as an argument to plot it        
        self.img_original_vl.addWidget(self.canvas) # add a figure to the vertical layout of the widget

        """ Creates the connections between the canvas, events and the funtions called"""
        self.canvas.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.canvas.figure.canvas.mpl_connect('button_release_event', self.onRelease)
        self.canvas.figure.canvas.mpl_connect('motion_notify_event', self.onMotion)

        self.selector = RectangleSelector(self.imageNorm.axes, self.imageNorm.onSelect, drawtype='box',
                             spancoords='data', button=1, minspanx=2, minspany=2)
        
        self.addNavigationToolbar()
        
        self.canvas.draw()
        self.canvas.update()
        
        index = fname.rindex("/")
        list_name = fname[index+1:len(fname)]
        self.image_list.addItem(list_name)


    def addNavigationToolbar(self):
        """
        self.toolbar = NavigationToolbar(self.canvas,\
                self, coordinates=True)
        self.addToolBar(self.toolbar)
        """
        # Personalization of Buttons in the NavigationToolbar
        NavigationToolbar.toolitems = ((u'Home', u'Reset original view', u'home', u'home'), (u'Back', u'Back to  previous view', u'back', u'back'),
                                       (u'Forward', u'Forward to next view', u'forward', u'forward'), (None, None, None, None),
                                       (u'Pan', u'Pan axes with left mouse, zoom with right', u'move', u'pan'), (u'Zoom', u'Zoom to rectangle', u'zoom_to_rect', u'zoom'),
                                       (None, None, None, None))
        
        
        # add fixed toolbar       

        self.toolbar = NavigationToolbar(self.canvas,\
                self.image_original, coordinates=True)        
        self.img_original_vl.addWidget(self.toolbar)
        

    def onPress(self, event):
##        print "mouse Pressed"
        self.imageNorm.onPress(event)
##        self.canvas.figure.canvas.draw()

        
    def onRelease(self, event):
##        print "mouse released"
        self.y0, self.y1 = self.imageNorm.onRelease(event)
##        print "y0: ", self.y0, "y1: ", self.y1
        self.selection_y0.setValue(self.y0)
        self.selection_y1.setValue(self.y1)        
##        self.canvas.figure.canvas.draw()


    def onMotion(self, event):
##        print "on motion"
        self.imageNorm.onMotion(event)
##        self.canvas.figure.canvas.draw()
    

    def saveProject(self):
        savename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '/home/carlos/Documents/Elettra/Normalizing_stxm_project')[0]
        self.imageNorm.saveProject(self.fname, savename)     
        self.canvas.figure.canvas.draw()
        

    def exportImage(self):
        savename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '/home/carlos/Documents/Elettra/Normalizing_stxm_project')[0]
        self.imageNorm.exportImage(savename)
        self.canvas.figure.canvas.draw()


    def resetImage(self):
        self.imageNorm.resetImage(self.fname)
        self.canvas.figure.canvas.draw()
        
                
    def removeFigure(self):
        self.imageNorm.removeFigure()
        self.img_original_vl.removeWidget(self.canvas)
        self.canvas.close()
        self.img_original_vl.removeWidget(self.toolbar)
        self.toolbar.close()
        self.fig_dict.clear()
        self.image_list.clear()
        

    def normImage(self):
        self.imageNorm.normImage()
        self.canvas.figure.canvas.draw()
        

    def clearSelection(self):
        self.imageNorm.clearSelection(self.clear_all_selections.isChecked())
        self.canvas.figure.canvas.draw()
        
def gui():
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
    
              
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

