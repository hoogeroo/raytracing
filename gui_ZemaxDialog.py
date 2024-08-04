# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_ZemaxDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ZemaxDialog(object):
    def setupUi(self, ZemaxDialog):
        ZemaxDialog.setObjectName("ZemaxDialog")
        ZemaxDialog.resize(451, 185)
        self.gridLayout = QtWidgets.QGridLayout(ZemaxDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.zemaxFileBox = QtWidgets.QLineEdit(ZemaxDialog)
        self.zemaxFileBox.setObjectName("zemaxFileBox")
        self.gridLayout.addWidget(self.zemaxFileBox, 2, 1, 1, 2)
        self.fileButton = QtWidgets.QPushButton(ZemaxDialog)
        self.fileButton.setObjectName("fileButton")
        self.gridLayout.addWidget(self.fileButton, 0, 0, 1, 1)
        self.zemaxButtonBox = QtWidgets.QDialogButtonBox(ZemaxDialog)
        self.zemaxButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.zemaxButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.zemaxButtonBox.setObjectName("zemaxButtonBox")
        self.gridLayout.addWidget(self.zemaxButtonBox, 5, 2, 1, 1)
        self.zemaxFileButton = QtWidgets.QPushButton(ZemaxDialog)
        self.zemaxFileButton.setObjectName("zemaxFileButton")
        self.gridLayout.addWidget(self.zemaxFileButton, 2, 0, 1, 1)
        self.fileBox = QtWidgets.QLineEdit(ZemaxDialog)
        self.fileBox.setObjectName("fileBox")
        self.gridLayout.addWidget(self.fileBox, 0, 2, 1, 1)
        self.label = QtWidgets.QLabel(ZemaxDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        self.loadButton = QtWidgets.QPushButton(ZemaxDialog)
        self.loadButton.setObjectName("loadButton")
        self.gridLayout.addWidget(self.loadButton, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(ZemaxDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.nameBox = QtWidgets.QLineEdit(ZemaxDialog)
        self.nameBox.setObjectName("nameBox")
        self.gridLayout.addWidget(self.nameBox, 1, 1, 1, 2)
        self.positionBox = QtWidgets.QLineEdit(ZemaxDialog)
        self.positionBox.setObjectName("positionBox")
        self.gridLayout.addWidget(self.positionBox, 4, 1, 1, 1)
        self.flipButton = QtWidgets.QPushButton(ZemaxDialog)
        self.flipButton.setObjectName("flipButton")
        self.gridLayout.addWidget(self.flipButton, 4, 2, 1, 1)

        self.retranslateUi(ZemaxDialog)
        self.zemaxButtonBox.accepted.connect(ZemaxDialog.accept)
        self.zemaxButtonBox.rejected.connect(ZemaxDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ZemaxDialog)

    def retranslateUi(self, ZemaxDialog):
        _translate = QtCore.QCoreApplication.translate
        ZemaxDialog.setWindowTitle(_translate("ZemaxDialog", "Dialog"))
        self.fileButton.setText(_translate("ZemaxDialog", "File"))
        self.zemaxFileButton.setText(_translate("ZemaxDialog", "Zemax File"))
        self.label.setText(_translate("ZemaxDialog", "Position"))
        self.loadButton.setText(_translate("ZemaxDialog", "Load"))
        self.label_2.setText(_translate("ZemaxDialog", "Name"))
        self.flipButton.setText(_translate("ZemaxDialog", "Flip"))

