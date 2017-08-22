from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QPushButton


class Button(QPushButton):
    """
    Simple button with custom signals

    Signals:
        leftClick
        rightClick
        shiftClick

    Args:
        label(str): The Button text label.
    """
    # creation du signal emetteur (emet rien pour le moment)
    leftClick = pyqtSignal()
    rightClick = pyqtSignal()

    shiftClick = pyqtSignal()
    def __init__(self, label):
        QPushButton.__init__(self, label)

        self.mainStyle = "font-family:Akkurat-Mono;color:white"
        self.setMinimumWidth(5)

        self.setFlat(True)
        self.amount = 0

        self.cOn = "cyan"
        self.cOff = "black"


        self.setStyleSheet(self.cOff)

    @property
    def cOn(self):
        return self._cOn
    @cOn.setter
    def cOn(self,color):
        self._cOn = "background-color:" + color + ";border:none;border-radius:5px;"+self.mainStyle

    @property
    def cOff(self):
        return self._cOff
    @cOff.setter
    def cOff(self,color):
        self._cOff = "background-color:" + color + ";border:none;border-radius:5px;"+self.mainStyle


    def mousePressEvent(self, event):
        # on integre la fonction QPushButton.mousePressEvent(self, event) a notre fonction PushRightButton.mousePressEvent(self, event)
        #QPushButton.mousePressEvent(self, event)
        if event.button() == Qt.LeftButton:
            if event.modifiers() != Qt.ShiftModifier:
                self.leftClick.emit()
        # condition du click droit
        if event.button() == Qt.RightButton:
            # emittion du signal rightClick
            self.rightClick.emit()
            # print ('right click')
        if event.modifiers() == Qt.ShiftModifier:
            self.shiftClick.emit()