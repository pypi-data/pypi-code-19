import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QStatusBar, QWidget, QApplication, QVBoxLayout, QPushButton, QProgressBar
#from toolz.curried import partial


class Status(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.timer = QTimer()

        self.original_message = ""

        self.on_timeout()

    def showMessage(self, message,msecs=0):
        super().showMessage(message, msecs)
        if "124" in self.styleSheet():
            self.original_message = message

    def showError(self,message,msecs=3000):

        # print(msecs)
        if msecs == False:
            msecs = 3000
        self.setStyleSheet("background-color:rgb(230,53,65);color:white")
        self.timer.setInterval(msecs)
        self.timer.timeout.connect(self.on_timeout)
        #self.timer.singleShot(msecs,prt)
        self.timer.start()
        self.showMessage(message,msecs)

    def showSuccess(self,message,msecs=3000):

        # print(msecs)
        if msecs == False:
            msecs = 3000
        self.setStyleSheet("background-color:rgb(154,204,75);color:white")
        self.timer.setInterval(msecs)
        self.timer.timeout.connect(self.on_timeout)
        #self.timer.singleShot(msecs,prt)
        self.timer.start()
        self.showMessage(message,msecs)

    def showWarning(self,message,msecs=3000):
        # print(msecs)
        if msecs == False:
            msecs = 3000
        self.setStyleSheet("background-color:rgb(217,159,0);color:white")
        self.timer.setInterval(msecs)
        self.timer.timeout.connect(self.on_timeout)
        #self.timer.singleShot(msecs,prt)
        self.timer.start()
        self.showMessage(message,msecs)

    def on_timeout(self):
        self.setStyleSheet("background-color:rgb(124,124,124);color:white")
        self.timer.stop()

        self.showMessage(self.original_message)


if __name__ == '__main__':
    from functools import partial
    app = QApplication([])

    w = QWidget()

    s = Status()
    l = QVBoxLayout()
    p1 = QPushButton("showError")
    p2 = QPushButton("showWarning")
    p3 = QPushButton("showSuccess")

    prt1 = partial(s.showError,"error")
    prt2 = partial(s.showWarning,"warning")
    prt3 = partial(s.showSuccess,"success")

    prog = QProgressBar()

    p1.clicked.connect(prt1)
    p2.clicked.connect(prt2)
    p3.clicked.connect(prt3)

    s.showMessage('Hello')
    l.addWidget(p1)
    l.addWidget(p2)
    l.addWidget(p3)

    l.addWidget(prog)

    style = "QProgressBar {" \
            "border: 1px solid transparent;" \
            "border-radius: 8px;" \
            "text-align: center;" \
            "color:white;" \
            "font-family:'Akkurat-Mono';}" \
            "QProgressBar::chunk {" \
            "background-color: #9acc4b;" \
            "}"

    #prog.setStyleSheet("background-color:cyan;color:red")
    prog.setStyleSheet(style)
    prog.setMaximum(100)
    prog.setValue(50)
    l.addWidget(s)
    w.setLayout(l)
    #s.showMessage("Salut")
    #s.showError("Salut",1500)
    w.show()

    sys.exit(app.exec_())