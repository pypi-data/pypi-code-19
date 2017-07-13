#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets


def pyqt2bool(entry):
    return not (entry == 'false' or not entry)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('Dubble')
    app.setOrganizationDomain('esrf.eu')
    app.setApplicationName('bubble')
    from .wbubblec import WBubble
    wbubble = WBubble()
    wbubble.show()
    sys.exit(app.exec_())
