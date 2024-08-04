# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_SourceDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SourceDialog(object):
    def setupUi(self, SourceDialog):
        SourceDialog.setObjectName("SourceDialog")
        SourceDialog.resize(315, 343)
        self.gridLayout = QtWidgets.QGridLayout(SourceDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.loadButton = QtWidgets.QPushButton(SourceDialog)
        self.loadButton.setObjectName("loadButton")
        self.gridLayout.addWidget(self.loadButton, 0, 2, 1, 1)
        self.saveloadBox = QtWidgets.QLineEdit(SourceDialog)
        self.saveloadBox.setObjectName("saveloadBox")
        self.gridLayout.addWidget(self.saveloadBox, 1, 0, 1, 3)
        self.label = QtWidgets.QLabel(SourceDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.nameBox = QtWidgets.QLineEdit(SourceDialog)
        self.nameBox.setObjectName("nameBox")
        self.gridLayout.addWidget(self.nameBox, 2, 1, 1, 2)
        self.label_2 = QtWidgets.QLabel(SourceDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.posyBox = QtWidgets.QLineEdit(SourceDialog)
        self.posyBox.setObjectName("posyBox")
        self.gridLayout.addWidget(self.posyBox, 3, 1, 1, 2)
        self.label_3 = QtWidgets.QLabel(SourceDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.poszBox = QtWidgets.QLineEdit(SourceDialog)
        self.poszBox.setObjectName("poszBox")
        self.gridLayout.addWidget(self.poszBox, 4, 1, 1, 2)
        self.label_4 = QtWidgets.QLabel(SourceDialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)
        self.nRaysBox = QtWidgets.QLineEdit(SourceDialog)
        self.nRaysBox.setObjectName("nRaysBox")
        self.gridLayout.addWidget(self.nRaysBox, 5, 1, 1, 2)
        self.label_5 = QtWidgets.QLabel(SourceDialog)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 6, 0, 1, 2)
        self.numAperBox = QtWidgets.QLineEdit(SourceDialog)
        self.numAperBox.setObjectName("numAperBox")
        self.gridLayout.addWidget(self.numAperBox, 6, 2, 1, 1)
        self.wavelengthBox = QtWidgets.QLineEdit(SourceDialog)
        self.wavelengthBox.setObjectName("wavelengthBox")
        self.gridLayout.addWidget(self.wavelengthBox, 7, 2, 1, 1)
        self.sourceButtonBox = QtWidgets.QDialogButtonBox(SourceDialog)
        self.sourceButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.sourceButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.sourceButtonBox.setObjectName("sourceButtonBox")
        self.gridLayout.addWidget(self.sourceButtonBox, 8, 0, 1, 3)
        self.saveButton = QtWidgets.QPushButton(SourceDialog)
        self.saveButton.setObjectName("saveButton")
        self.gridLayout.addWidget(self.saveButton, 0, 0, 1, 2)
        self.label_6 = QtWidgets.QLabel(SourceDialog)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 7, 0, 1, 1)

        self.retranslateUi(SourceDialog)
        self.sourceButtonBox.accepted.connect(SourceDialog.accept)
        self.sourceButtonBox.rejected.connect(SourceDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SourceDialog)

    def retranslateUi(self, SourceDialog):
        _translate = QtCore.QCoreApplication.translate
        SourceDialog.setWindowTitle(_translate("SourceDialog", "Source"))
        self.loadButton.setText(_translate("SourceDialog", "Load"))
        self.label.setText(_translate("SourceDialog", "Name"))
        self.label_2.setText(_translate("SourceDialog", "Position (y)"))
        self.label_3.setText(_translate("SourceDialog", "Position (z)"))
        self.label_4.setText(_translate("SourceDialog", "Number of Rays"))
        self.label_5.setText(_translate("SourceDialog", "Numerical Aperture"))
        self.saveButton.setText(_translate("SourceDialog", "File"))
        self.label_6.setText(_translate("SourceDialog", "Wavelength (nm)"))

