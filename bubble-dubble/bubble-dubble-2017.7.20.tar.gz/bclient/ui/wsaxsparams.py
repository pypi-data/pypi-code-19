# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WSaxsParams(object):
    def setupUi(self, WSaxsParams):
        WSaxsParams.setObjectName("WSaxsParams")
        WSaxsParams.setWindowModality(QtCore.Qt.WindowModal)
        WSaxsParams.resize(390, 170)
        WSaxsParams.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        WSaxsParams.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(WSaxsParams)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(WSaxsParams)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.thicknessLineEdit = QtWidgets.QLineEdit(WSaxsParams)
        self.thicknessLineEdit.setText("")
        self.thicknessLineEdit.setObjectName("thicknessLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.thicknessLineEdit)
        self.label_2 = QtWidgets.QLabel(WSaxsParams)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.concentrationLineEdit = QtWidgets.QLineEdit(WSaxsParams)
        self.concentrationLineEdit.setText("")
        self.concentrationLineEdit.setObjectName("concentrationLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.concentrationLineEdit)
        self.label_3 = QtWidgets.QLabel(WSaxsParams)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.calibrationLineEdit = QtWidgets.QLineEdit(WSaxsParams)
        self.calibrationLineEdit.setText("")
        self.calibrationLineEdit.setObjectName("calibrationLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.calibrationLineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.okButton = QtWidgets.QPushButton(WSaxsParams)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.cancelButton = QtWidgets.QPushButton(WSaxsParams)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WSaxsParams)
        QtCore.QMetaObject.connectSlotsByName(WSaxsParams)

    def retranslateUi(self, WSaxsParams):
        _translate = QtCore.QCoreApplication.translate
        WSaxsParams.setWindowTitle(_translate("WSaxsParams", "Advanced parameters for SAXS"))
        self.label.setText(_translate("WSaxsParams", "Sample thickness (cm):"))
        self.label_2.setText(_translate("WSaxsParams", "Sample concentration (g/ml):"))
        self.label_3.setText(_translate("WSaxsParams", "<html><head/><body><p>Calibration factor (cm<span style=\" vertical-align:super;\">-1</span>):</p></body></html>"))
        self.okButton.setText(_translate("WSaxsParams", "Apply"))
        self.cancelButton.setText(_translate("WSaxsParams", "Cancel"))


