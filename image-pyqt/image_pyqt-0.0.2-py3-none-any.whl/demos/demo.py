#!/usr/bin/python3
# 2017.07.26 15:32:16 CST
# create by ausk@github.com

import os, sys

########################################################################
## Method 1: import from the installed package!
rootdir = os.path.expanduser(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
sys.path.insert(0,rootdir)

from imagepyqt.widgets import imwidget
from imagepyqt.myQt import mkQApp, runQApp, QtWidgets
from imagepyqt import qimshow


########################################################################
"""
## Method2: import modules from current directory!
from ..widgets import imwidget
from .. import qimshow
from ..myQt import mkQApp, runQApp, QtWidgets
"""


########################################################################
imagename = os.path.abspath(os.path.join(os.path.dirname(__file__),"../data/test.png"))
#imagename = "/home/auss/Pictures/test.png"

def test1():
    import cv2
    img = cv2.imread(imagename)
    qApp=mkQApp()
    qimshow(img,"Test MyImageWidget[1]")
    runQApp()

def test2():
    import cv2
    img = cv2.imread(imagename)
    qApp = mkQApp()
    win = imwidget.MyImageWidget()
    win.setImage(img)
    win.setWindowTitle("Test MyImageWidget[2]")
    win.show()
    runQApp()

def run():
    test1()
    test2()

if __name__ == "__main__":
    run()
