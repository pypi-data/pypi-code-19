import sys
from pathlib import Path

import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFontDatabase
from PyQt5.QtWidgets import QWidget, QApplication


from mtb.pyinstaller_helpers import resource_path
from os.path import dirname


__all__ = ["mDark"]


class mDarkTest(QWidget):

    def __init__(self,parent=None):
        super(mDarkTest, self).__init__(parent)



class mDark(object):

    @staticmethod
    def palette():

        palette = QPalette()
        palette.setColor(QPalette.Window,QColor(53,53,53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        palette.setColor(QPalette.Base, QColor(42, 42, 42))
        palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        palette.setColor(QPalette.Dark, QColor(35, 35, 35))
        palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))


        return palette

    @staticmethod
    def style():

        path_to_fonts = []
        rel_font = resource_path("assets/fonts")

        if Path(rel_font).is_dir():
            pass
        else:
            rel_font = os.path.join(dirname(__file__),"assets/fonts")


        for f in Path(rel_font).iterdir():
            QFontDatabase.addApplicationFont( os.path.join(str(f)) )
            print("Adding {}".format(str(f)))



        style = ""
        path_to_css = resource_path("assets/ui/qtStyles.css")

        if Path(path_to_css).is_file():
            pass
        else:
            path_to_css = os.path.join(dirname(__file__),"assets/ui/qtStyles.css")

        with open(path_to_css) as e:

            for line in e:
                style += line


        return style


if __name__ == '__main__':
    app = QApplication([])
    #
    w = mDarkTest()
    #
    w.setPalette(mDark.palette())
    w.setStyleSheet(mDark.style())
    #
    w.show()
    #
    sys.exit(app.exec_())

#print(mDrak.style())