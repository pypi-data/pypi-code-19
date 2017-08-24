''' 
 @package   pNbody
 @file      libqt.py
 @brief     PyQt4 interface
 @copyright GPLv3
 @author    Yves Revaz <yves.revaz@epfl.ch>
 @section   COPYRIGHT  Copyright (C) 2017 EPFL (Ecole Polytechnique Federale de Lausanne)  LASTRO - Laboratory of Astrophysics of EPFL

 This file is part of pNbody. 
'''


from PyQt4 import QtCore, QtGui
from numpy import *
import pNbody
from libutil import *

from PIL import ImageQt


def rgb(r, g, b):
    # use qRgb to pack the colors, and then turn the resulting long
    # into a negative integer with the same bitpattern.
    return (QtGui.qRgb(r, g, b) & 0xffffff) - 0x1000000


class QNumarrayImage(QtGui.QImage):
    '''
    QNumarrayImage class
    '''

    def __init__(self, data, palette_name):

	format      = QtGui.QImage.Format_Indexed8
	
        # include the palette 																   
        palette = Palette(palette_name)	

	
	#data = data*0+64
	data = data.astype(uint8)
	
	# give the right form	
	shape = data.shape
	data  = transpose(data)
	data  = ravel(data)
	data.shape=shape
	
	self.__data = data.tostring()

        # init object
        QtGui.QImage.__init__(self, self.__data, data.shape[0], data.shape[1], format)


	# color table
	colortable = []
        for i in range(256):
          colortable.append(rgb(palette.r[i],palette.g[i],palette.b[i]))
        self.setColorTable(colortable)
	
	

def qtplot(mat,palette='light'):
  '''
  plot a matrix using qt
  '''

  app = QtGui.QApplication(sys.argv)

  imageLabel = QtGui.QLabel()
  imageLabel.setScaledContents(True)
  
  matint,mn,mx,cd = set_ranges(mat,scale='lin',mn=None,mx=None,cd=None)
  
  # without qt
  imageQt = QNumarrayImage(matint,palette)
  
  # using PIL
  #imagePIL = get_image(matint,name=None,palette_name=palette)
  #imageQt  = ImageQt.ImageQt(imagePIL)
  	  
  imageLabel.setPixmap(QtGui.QPixmap.fromImage(imageQt))  
  
  imageLabel.show()
  sys.exit(app.exec_())


def display(imagePIL):
    '''
    display a PIL image
    '''

    imageQt = ImageQt.ImageQt(imagePIL)

    global app
    app = QtGui.QApplication.instance()

    if (app is None):
        app = QtGui.QApplication(sys.argv)

    imageLabel = QtGui.QLabel()
    imageLabel.setScaledContents(True)
    imageLabel.setPixmap(QtGui.QPixmap.fromImage(imageQt))
    imageLabel.setWindowTitle('Image')
    imageLabel.show()
    # sys.exit(app.exec_())
    app.exec_()
