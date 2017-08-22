import sys

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QFrame


class ColorBand(QWidget):
    def __init__(self,howmany=3,colorarray=[]):
        super(ColorBand, self).__init__()


        if colorarray:
            self.colors = colorarray
            self.count = len(colorarray)

        else:
            self.colors = []
            self.count = howmany

        #self.resize(800,600)


        self.buildUI()


    def sizeHint(self):
        return QSize(600,200)

    def buildUI(self):

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        layout.setSpacing(0)


        self.frames = []
        for x in range(0,self.count):
            frame = QFrame()
            #frame.setFrameShape(QFrame.StyledPanel)
            self.frames.append(frame)
            layout.addWidget(frame)

        #layout
        self.setColors()


    def clearColors(self):

        if self.colors:
            self.colors = None

        for id in range(0,self.count):
            self.frames[id].setStyleSheet("")

    def setColors(self,colorarray=None):

        if not self.colors and colorarray :
            self.colors = colorarray

        if self.count == len(self.colors):
            for id, c in enumerate(self.colors):
                style = "background-color:rgb({},{},{})".format(*c)
                self.frames[id].setStyleSheet(style)


    @staticmethod
    def showColors(color_array):

        if not QApplication.instance():

            app = QApplication([])

        if type(color_array) == list:

            a = ColorBand(colorarray=color_array)

            a.show()

            sys.exit(app.exec_())




if __name__ == '__main__':
    app = QApplication(sys.argv)



    w = ColorBand()
    w.show()
    sys.exit(app.exec_())