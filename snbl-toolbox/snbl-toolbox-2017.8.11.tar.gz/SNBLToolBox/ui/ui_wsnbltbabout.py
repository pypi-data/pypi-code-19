# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WSnblAbout(object):
    def setupUi(self, WSnblAbout):
        WSnblAbout.setObjectName("WSnblAbout")
        WSnblAbout.resize(863, 485)
        self.verticalLayout = QtWidgets.QVBoxLayout(WSnblAbout)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label = QtWidgets.QLabel(WSnblAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(191, 71))
        self.label.setMaximumSize(QtCore.QSize(191, 71))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/snbl"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.aboutLabel = QtWidgets.QLabel(WSnblAbout)
        self.aboutLabel.setObjectName("aboutLabel")
        self.horizontalLayout_3.addWidget(self.aboutLabel)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.aboutQtButton = QtWidgets.QPushButton(WSnblAbout)
        self.aboutQtButton.setObjectName("aboutQtButton")
        self.horizontalLayout.addWidget(self.aboutQtButton)
        self.closeButton = QtWidgets.QPushButton(WSnblAbout)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WSnblAbout)
        QtCore.QMetaObject.connectSlotsByName(WSnblAbout)

    def retranslateUi(self, WSnblAbout):
        _translate = QtCore.QCoreApplication.translate
        WSnblAbout.setWindowTitle(_translate("WSnblAbout", "About SNBL Tool Box"))
        self.aboutLabel.setText(_translate("WSnblAbout", "<html><head/><body><p>SNBL Tool Box v1.0 (Swiss knife for Pilatus 2M data)</p><p>(c) Vadim Dyadkin</p><p>This program is licensed under GPL v3</p><p>Mercurial repository: <a href=\"http://hg.3lp.cx/snbltb\"><span style=\" text-decoration: underline; color:#0057ae;\">http://hg.3lp.cx/snbltb</span></a></p><p>Mercurial hash: @</p><p>When you use this software, please quote the following reference:</p><p><a href=\"http://dx.doi.org/10.1107/S1600577516002411\"><span style=\" text-decoration: underline; color:#0057ae;\">http://dx.doi.org/10.1107/S1600577516002411</a></p></body></html>"))
        self.aboutQtButton.setText(_translate("WSnblAbout", "About Qt"))
        self.closeButton.setText(_translate("WSnblAbout", "Close"))

from . import resources_rc
