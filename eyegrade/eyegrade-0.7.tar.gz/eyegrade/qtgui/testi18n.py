from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MyWindow(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        self.hbox = QHBoxLayout(self)
        self.myButtons = QDialogButtonBox(self)
        self.hbox.addWidget(self.myButtons)
        button = self.myButtons.addButton(QDialogButtonBox.Open)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    translator = QTranslator()
    print translator.load(QLocale.system(), 'qt', '_',
                          QLibraryInfo.location(QLibraryInfo.TranslationsPath))
#    print translator.load("qt_ru", QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    ui = MyWindow()
    ui.show()
    sys.exit(app.exec_())
    
