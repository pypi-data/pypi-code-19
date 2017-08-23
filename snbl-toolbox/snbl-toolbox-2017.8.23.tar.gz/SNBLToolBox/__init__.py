#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets


def pyqt2bool(entry):
    return not (entry == 'false' or not entry)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    from SNBLToolBox.wsnbltb import WSnblTB
    wsnbl = WSnblTB()
    wsnbl.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
