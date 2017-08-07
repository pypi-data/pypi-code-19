# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_widgetSensors(object):
    def setupUi(self, widgetSensors):
        widgetSensors.setObjectName("widgetSensors")
        widgetSensors.resize(445, 76)
        widgetSensors.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.gridLayout = QtWidgets.QGridLayout(widgetSensors)
        self.gridLayout.setObjectName("gridLayout")
        self.labelA = QtWidgets.QLabel(widgetSensors)
        self.labelA.setObjectName("labelA")
        self.gridLayout.addWidget(self.labelA, 1, 0, 1, 1)
        self.labelC = QtWidgets.QLabel(widgetSensors)
        self.labelC.setObjectName("labelC")
        self.gridLayout.addWidget(self.labelC, 1, 4, 1, 1)
        self.checkBoxA = QtWidgets.QCheckBox(widgetSensors)
        self.checkBoxA.setObjectName("checkBoxA")
        self.gridLayout.addWidget(self.checkBoxA, 0, 0, 1, 1)
        self.checkBoxC = QtWidgets.QCheckBox(widgetSensors)
        self.checkBoxC.setObjectName("checkBoxC")
        self.gridLayout.addWidget(self.checkBoxC, 0, 4, 1, 1)
        self.line = QtWidgets.QFrame(widgetSensors)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 0, 1, 2, 1)
        self.labelB = QtWidgets.QLabel(widgetSensors)
        self.labelB.setObjectName("labelB")
        self.gridLayout.addWidget(self.labelB, 1, 2, 1, 1)
        self.checkBoxB = QtWidgets.QCheckBox(widgetSensors)
        self.checkBoxB.setObjectName("checkBoxB")
        self.gridLayout.addWidget(self.checkBoxB, 0, 2, 1, 1)
        self.checkBoxD = QtWidgets.QCheckBox(widgetSensors)
        self.checkBoxD.setObjectName("checkBoxD")
        self.gridLayout.addWidget(self.checkBoxD, 0, 6, 1, 1)
        self.labelD = QtWidgets.QLabel(widgetSensors)
        self.labelD.setObjectName("labelD")
        self.gridLayout.addWidget(self.labelD, 1, 6, 1, 1)
        self.line_3 = QtWidgets.QFrame(widgetSensors)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 0, 5, 2, 1)
        self.line_2 = QtWidgets.QFrame(widgetSensors)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 0, 3, 2, 1)

        self.retranslateUi(widgetSensors)
        QtCore.QMetaObject.connectSlotsByName(widgetSensors)

    def retranslateUi(self, widgetSensors):
        _translate = QtCore.QCoreApplication.translate
        widgetSensors.setWindowTitle(_translate("widgetSensors", "Form"))
        self.labelA.setText(_translate("widgetSensors", "000.00 K"))
        self.labelC.setText(_translate("widgetSensors", "000.00 K"))
        self.checkBoxA.setText(_translate("widgetSensors", "A"))
        self.checkBoxC.setText(_translate("widgetSensors", "C"))
        self.labelB.setText(_translate("widgetSensors", "000.00 K"))
        self.checkBoxB.setText(_translate("widgetSensors", "B"))
        self.checkBoxD.setText(_translate("widgetSensors", "D"))
        self.labelD.setText(_translate("widgetSensors", "000.00 K"))


