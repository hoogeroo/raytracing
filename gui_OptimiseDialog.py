# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_OptimiseDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_OptimiseDialog(object):
    def setupUi(self, OptimiseDialog):
        OptimiseDialog.setObjectName("OptimiseDialog")
        OptimiseDialog.resize(262, 302)
        self.gridLayout = QtWidgets.QGridLayout(OptimiseDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(OptimiseDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.regionBox = QtWidgets.QLineEdit(OptimiseDialog)
        self.regionBox.setObjectName("regionBox")
        self.gridLayout.addWidget(self.regionBox, 3, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(OptimiseDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        self.scrollArea = QtWidgets.QScrollArea(OptimiseDialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 242, 163))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 241, 191))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 2, 0, 1, 2)
        self.label = QtWidgets.QLabel(OptimiseDialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.collimateButton = QtWidgets.QRadioButton(OptimiseDialog)
        self.collimateButton.setChecked(False)
        self.collimateButton.setObjectName("collimateButton")
        self.gridLayout.addWidget(self.collimateButton, 4, 1, 1, 1)
        self.focusButton = QtWidgets.QRadioButton(OptimiseDialog)
        self.focusButton.setObjectName("focusButton")
        self.gridLayout.addWidget(self.focusButton, 4, 0, 1, 1)

        self.retranslateUi(OptimiseDialog)
        self.buttonBox.accepted.connect(OptimiseDialog.accept)
        self.buttonBox.rejected.connect(OptimiseDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(OptimiseDialog)

    def retranslateUi(self, OptimiseDialog):
        _translate = QtCore.QCoreApplication.translate
        OptimiseDialog.setWindowTitle(_translate("OptimiseDialog", "Optimise Settings"))
        self.label_2.setText(_translate("OptimiseDialog", "Focus Area"))
        self.label.setText(_translate("OptimiseDialog", "Free Positions"))
        self.collimateButton.setText(_translate("OptimiseDialog", "Collimate"))
        self.focusButton.setText(_translate("OptimiseDialog", "Focus"))

