#!/usr/bin/python3
# 2017.07.04 23:47:34 CST

import sys,os
assert(sys.version_info[0]==3)

__version__ = "0.0.1"
print("imagepyqt version:{}".format(__version__))

CONFIG_OPTIONS = {
    'useOpenGL': False,
    'foreground': 'd',  ## foreground color
    'background': 'k',  ## background color
    'antialias': False,
}

def getConfigOption(opt):
    assert(opt in CONFIG_OPTIONS.keys())
    return CONFIG_OPTIONS[opt]

def setConfigOption(opt,value):
    global CONFIG_OPTIONS
    #assert(opt in CONFIG_OPTIONS)
    assert(opt in CONFIG_OPTIONS.keys())
    CONFIG_OPTIONS[opt] = value

def setConfigOptions(**opts):
    for k,v in opts.items():
        setConfigOption(k, v)

def do_gc():
    import gc
    gc.collect()

## debug.py
def warnOnException(func):
    """Decorator that catches/ignores exceptions and prints a stack trace."""
    def inner(*args, **kwds):
        try:
            func(*args, **kwds)
        except Exception as ex:
            print('Ignored exception in function {}(): \n{}'.format(func.__name__,ex))
    return inner


def cmpToKey(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

## python2_3
def sortList(l, cmpFunc):
    if sys.version_info[0] == 2:
        l.sort(cmpFunc)
    else:
        l.sort(key=cmpToKey(cmpFunc))

if sys.version_info[0] == 3:
    xrange = range
    def cmp(a,b):
        if a>b:
            return 1
        elif b > a:
            return -1
        else:
            return 0
else:
    import __builtin__
    xrange = __builtin__.xrange
    cmp = __builtin__.cmp


# Add compatibility for dict @ 2017.06.22 by <ausk@github.com>
# http://legacy.python.org/dev/peps/pep-0469/#migrating-to-the-common-subset-of-python-2-and-3

try:
    dict.iteritems
except AttributeError:
    # Python 3
    def itervalues(d):
        return iter(d.values())
    def iteritems(d):
        return iter(d.items())
else:
    # Python 2
    def itervalues(d):
        return d.itervalues()
    def iteritems(d):
        return d.iteritems()


# file changed
def fileSelectHandler(parent=None):
    """
    dialog = QtWidgets.QFileDialog(parent)
    dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile) # require existing file is selected
    dialog.setNameFilter("Image files (*.jpg *.png)")
    dialog.setDirectory("~")
    #filename, filetype = dialog.getOpenFileName()
    filename = dialog.getOpenFileName()[0]
    """
    fdname = QtWidgets.QFileDialog.getOpenFileName(parent, "Open file", os.path.expanduser('~') + '/Pictures', "Image Files (*.png *.jpg *.bmp)")
    return fdname[0] if fdname else None

def fileSaveHandler(parent=None):
    fdname = QtWidgets.QFileDialog.getSaveFileName(parent, "Save file", os.path.expanduser('~') + '/Desktop')
    return fdname[0] if fdname else None

def folderSelectHandler(parent=None):
    foldername = QtWidgets.QFileDialog.getExistingDirectory(parent, "Open folder", os.path.expanduser('~'), options=QtWidgets.QFileDialog.ShowDirsOnly)
    print(foldername)


_images = []
def myimshow(img, title="Test ImageView"):
    mkQApp()
    win = MyImageWidget()
    win.setWindowTitle(title)
    win.setImage(img)
    _images.append(win)
    win.show()
    return win

qimshow = myimshow
imshow = myimshow

## 从模块导入所有的东西
from .myQt import *
from .widgets import *
from .demos import *
