import os
import sys

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QVBoxLayout
from mtb.qtUtils import aToQ, QColor


__all__ = ["Alert","AlertPopup","AlertMouse"]


class Alert(QWidget):

    def __init__(self,
                 al="This is an alert widget",
                 bg=None,
                 fg=(255, 0, 0),
                 font="Akkurat",
                 fontSize=20,
                 parent=None):

        super(Alert, self).__init__(parent)


        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        #self.setWindowFlags(Qt.Popup)
        if self.parent():
            self.setGeometry(self.parent().geometry())
        else:
            self.setGeometry(QDesktopWidget().screenGeometry())

        #self.setWindowState(Qt.WindowMaximized)
        self.alert = al

        self.bg = bg



        self.fg = fg
        self.font = font
        self.fontSize = fontSize

    @property
    def fg(self):
        return self._fg

    @fg.setter
    def fg(self,fgcolor):
        if type(fgcolor) == tuple:
            self._fg = aToQ(fgcolor)
        elif type(fgcolor) == QColor:
            self._fg = fgcolor
        elif fgcolor == None:
            self._fg = aToQ((0, 0, 0, 0))
        else:
            raise TypeError

    @property
    def bg(self):
        return self._bg

    @bg.setter
    def bg(self, bgcolor):
        if type(bgcolor) == tuple:
            self._bg = aToQ(bgcolor)
        elif type(bgcolor) == QColor:
            self._bg = bgcolor
        elif bgcolor == None:
            self._bg = aToQ((0, 0, 0, 0))
        else:
            raise TypeError

    def paintEvent(self, event):
        qp = QPainter()

        qp.begin(self)
        self.drawBG(qp, event.rect())
        self.drawAlert(qp, event.rect())
        qp.end()

    def drawBG(self, qp, rect):
        qp.setBrush(self.bg)
        #qp.setOpacity(1)
        qp.setPen(QColor(0, 0, 0, 0))

        qp.drawRect(rect)

        qp.setOpacity(1)

    def drawAlert(self, qp, rect):

        qp.setPen(self.fg)
        qp.setFont(QFont(self.font, self.fontSize))

        text_rect = QRect(0, 0, self.width(), self.height())
        qp.drawText(text_rect, Qt.AlignCenter, self.alert)


class AlertPopup(Alert):

    def __init__(self, al="info"):
        super(AlertPopup, self).__init__()
        self.setAttribute(Qt.WA_QuitOnClose)

        if al == "info":
            self.alert = ""
            self.systemInfo()
        else:
            self.alert = al

    def mousePressEvent(self, event):
        self.close()

    def keyPressEvent(self, event):
        self.close()

    def systemInfo(self):
        self.alert = ""
        self.alert += "You are:" + "\n"
        self.alert += os.getlogin()


class AlertMouse(Alert):

    def __init__(self, al="I follow mouses :)"):
        super(AlertMouse, self).__init__()

        self.alert = al
        self.mx = 250
        self.my = 250

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)
        qp.setPen(self.fg)
        qp.setFont(QFont(self.font, self.fontSize))
        qp.drawText(self.mx, self.my, self.alert)
        qp.end()

    def mouseMoveEvent(self, event):
        super(AlertMouse, self).mouseMoveEvent(event)
        self.mx = event.globalX()
        self.my = event.globalY()
        self.alert = "The mouse is at {}x{}.".format(self.mx, self.my)
        self.repaint()


if __name__ == '__main__':
    app = QApplication([])

    w = QWidget()

    layout = QVBoxLayout()
    a = Alert(parent=w)
    layout.addWidget(a)
    w.setLayout(layout)
    w.resize(640,360)
    w.show()
    sys.exit(app.exec_())