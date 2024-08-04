# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_StartWindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_StartWindow(object):
    def setupUi(self, StartWindow):
        StartWindow.setObjectName("StartWindow")
        StartWindow.resize(126, 146)
        self.verticalLayout = QtWidgets.QVBoxLayout(StartWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.newButton = QtWidgets.QPushButton(StartWindow)
        self.newButton.setObjectName("newButton")
        self.verticalLayout.addWidget(self.newButton)
        self.loadButton = QtWidgets.QPushButton(StartWindow)
        self.loadButton.setObjectName("loadButton")
        self.verticalLayout.addWidget(self.loadButton)
        self.quitButton = QtWidgets.QPushButton(StartWindow)
        self.quitButton.setObjectName("quitButton")
        self.verticalLayout.addWidget(self.quitButton)

        self.retranslateUi(StartWindow)
        QtCore.QMetaObject.connectSlotsByName(StartWindow)

    def retranslateUi(self, StartWindow):
        _translate = QtCore.QCoreApplication.translate
        StartWindow.setWindowTitle(_translate("StartWindow", "Raytrace"))
        self.newButton.setText(_translate("StartWindow", "New"))
        self.loadButton.setText(_translate("StartWindow", "Load"))
        self.quitButton.setText(_translate("StartWindow", "Quit"))

