from functools import partial

from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QCursor, QColor, QFont, QPainter
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout
from mtb.qtUtils import randQColor
from mtb.qtWidgets import Button, Label

__all__ = ["Bar_wrap", "Bar"]


class Bar(QWidget):
    valueChanged = pyqtSignal(int)
    divisionChanged = pyqtSignal(int)

    def __init__(self, parent=None, color=QColor(255, 0, 0)):
        super(QWidget, self).__init__(parent)

        self.division = 20
        self.padding = 2
        self.percent = 0
        self.old_percent = 0
        self.border = False
        self.border_size = 3
        self.randomColor()

    def setValue(self, value):
        self.percent = value
        self.valueChanged.emit(value)
        self.repaint()

    def setDivision(self, div, add=False):

        if add:
            self.division += div
        else:
            self.division = div

        self.divisionChanged.emit(self.division)
        self.repaint()

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.HighQualityAntialiasing, True)

        if self.border or self.percent == 0:
            self.drawBorder(event.rect(), qp)

        self.drawBars(event.rect(), qp)
        qp.end()

    def randomColor(self):
        self.color = randQColor(20)
        self.repaint()

    def zeroValue(self):
        self.percent = 0
        self.repaint()

    def changeColor(self):
        self.repaint()

    def drawBars(self, rect, qp):

        try:
            barHeight = self.height() / self.division
            div = self.division / 100 * self.percent

            qp.setPen(QColor(0, 0, 0, 0))
            qp.setBrush(self.color)

            if div > 0:
                for i in range(1, 1 + round(div)):
                    ypos = rect.height() - barHeight * i

                    baseRect = QRect(0, ypos, rect.width(), barHeight - self.padding)
                    qp.drawRect(baseRect)

        except:
            print("Cannot Draw")
            pass

        qp.setPen(QColor(255, 255, 255))
        qp.setFont(QFont('Akkurat', 12))
        qp.translate(0, self.border_size * 2)
        qp.drawText(rect, Qt.AlignHCenter, str(self.percent))

    def drawBorder(self, rect, qp):
        border = self.border_size
        qp.setPen(QColor(0, 0, 0, 0))
        qp.setBrush(self.color)
        qp.drawRect(0, 0, rect.width(), border)
        qp.drawRect(0, 0, self.border_size, rect.height())
        qp.drawRect(rect.width() - self.border_size, 0, self.border_size,
                    rect.height())
        qp.drawRect(0,
                    rect.height() - self.border_size,
                    rect.width(), self.border_size)

    def mousePressEvent(self, event):
        self.border = True
        self.repaint()

    def mouseReleaseEvent(self, event):
        self.border = False
        self.repaint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:

            relCursor = self.mapFromGlobal(QCursor.pos())
            self.percent = round(relCursor.y() / self.height() * 100)
            self.percent = 100 - self.percent

            if self.percent > 100:
                self.percent = 100
            if self.percent < 0:
                self.percent = 0

            if self.percent >= 0 and self.percent <= 100:
                self.valueChanged.emit(self.percent)
                self.repaint()


class Bar_wrap(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        layout = QVBoxLayout()

        self.zero = Button("Zero")
        self.rand = Button("Random")
        self.tool = Bar()

        self.tool.setMinimumWidth(50)

        layout.addWidget(self.tool)
        layout.addWidget(self.zero)
        layout.addWidget(self.rand)

        self.zero.leftClick.connect(self.tool.zeroValue)
        self.rand.leftClick.connect(self.tool.randomColor)

        layout2 = QHBoxLayout()
        layout2.setContentsMargins(0, 0, 0, 0)
        self.d5 = Button("-")
        self.d20 = Label("20")
        self.d50 = Button("+")

        self.d5.leftClick.connect(partial(self.tool.setDivision, -1, add=True))

        self.d50.leftClick.connect(partial(self.tool.setDivision, 1, add=True))

        self.tool.divisionChanged.connect(self.setLabel)
        layout2.addWidget(self.d5)
        layout2.addWidget(self.d20)
        layout2.addWidget(self.d50)

        layout.addLayout(layout2)
        self.setStyleSheet("background-color:rgb(40,40,40)")
        self.setLayout(layout)
        self.resize(200, 600)

    def setLabel(self, label):
        self.d20.setText(str(label))
