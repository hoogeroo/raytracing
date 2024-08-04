from PyQt5 import QtCore, QtWidgets
from gui_MasterWindow import Ui_MasterWindow
from gui_AchromatDialog import Ui_AchromatDialog
from gui_SourceDialog import Ui_SourceDialog
from gui_LensDialog import Ui_LensDialog
from gui_StartWindow import Ui_StartWindow
from gui_ZemaxDialog import Ui_ZemaxDialog
from gui_OptimiseDialog import Ui_OptimiseDialog
from importlib import reload
import numpy as np
from scipy.optimize import minimize
import pyqtgraph as pg
import zemax as zm
import libraytrace as lrt
import shared
import os

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class StartWindow(QtWidgets.QWidget, Ui_StartWindow):
    def __init__(self,parent=None):
        QtWidgetes.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.newButton.clicked.connect(self.handleNewButton)
        self.loadButton.clicked.connect(self.handleLoadButton)
        self.quitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.cwd=os.getcwd()

    def getName(self):
        return str(self.fileStringList.takeFirst())

    def handleNewButton(self):
        self.saveDialog = QtWidgets.QFileDialog(self)
        if self.saveDialog.exec_()==QtWidgets.QFileDialog.Accepted:
            self.fileStringList = self.saveDialog.selectedFiles()
            self.masterWindow = MasterWindow(self)
            self.masterWindow.projectName = str(self.fileStringList.takeFirst())
            self.masterWindow.cwd=self.cwd
            self.masterWindow.show()
            self.hide()


    def handleLoadButton(self):
        self.masterWindow = MasterWindow(self)
        self.masterWindow.cwd=self.cwd
        self.masterWindow.projectName = str(QtWidgets.QFileDialog.getOpenFileName())
        openFile=open(self.masterWindow.projectName, 'r')

        lines=openFile.readlines()
        for line in lines:
            if line[0:12]=='source      ':
                self.masterWindow.loadSource(line[13:-1])
            elif line[0:12]=='lens        ':
                self.masterWindow.loadLens(line[13:-1])
            elif line[0:12]=='achromat    ':
                self.masterWindow.loadAchromat(line[13:-1])
            elif line[0:12]=='zemax lens  ':
                print(line[13:-1])
                self.masterWindow.loadZemax(line[13:-1])
            elif line[0:12]=='end point   ':
                self.masterWindow.endDistanceBox.setText(line[13:-1])
            elif line[0:12]=='region      ':
                self.masterWindow.region=int(line[13:-1])
            elif line[0:12]=='focus       ':
                if line[13:-1]=='True':
                    self.masterWindow.focus=True
                elif line[13:-1]=='False':
                    self.masterWindow.focus=False

        self.masterWindow.plotComponents()
        self.hide()
        self.masterWindow.show()


class MasterWindow(QtWidgets.QMainWindow, Ui_MasterWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        #menubar=QtGui.QMenuBar()
        #self.gridLayout.addWidget(menubar,0,0)
        #actionFile=menubar.addMenu("File")
        #self.closeaction=actionFile.addAction("Close")
        self.actionExit.triggered.connect(self.handleExitButton)
        self.achromatButton.clicked.connect(self.handleAchromatButton)
        self.exitButton.clicked.connect(self.handleExitButton)#QtCore.QCoreApplication.instance().quit)
        self.writeButton.clicked.connect(self.handleWriteButton)
        self.sourceButton.clicked.connect(self.handleSourceButton)
        self.lensButton.clicked.connect(self.handleLensButton)
        self.runButton.clicked.connect(self.handleRunButton)
        self.editSourceButton.clicked.connect(self.handleEditSource)
        self.deleteSourceButton.clicked.connect(self.handleDeleteSource)
        self.editLensButton.clicked.connect(self.handleEditLens)
        self.deleteLensButton.clicked.connect(self.handleDeleteLens)
        self.editAchromatButton.clicked.connect(self.handleEditAchromat)
        self.deleteAchromatButton.clicked.connect(self.handleDeleteAchromat)
        self.zemaxButton.clicked.connect(self.handleZemaxButton)
        self.editZemaxButton.clicked.connect(self.handleEditZemax)
        self.deleteZemaxButton.clicked.connect(self.handleDeleteZemax)
        self.saveButton.clicked.connect(self.handleSaveButton)
        self.optimiseButton.clicked.connect(self.handleOptimiseButton)
        self.settingsButton.clicked.connect(self.handleSettingsButton)
        self.focus=True

        #arrays for attributes of sources
        self.sourceNames=np.array([],dtype=object)
        self.sourcePosys=np.array([],dtype=object)
        self.sourcePoszs=np.array([],dtype=object)
        self.sourceNRays=np.array([],dtype=object)
        self.sourceNumApers=np.array([],dtype=object)
        self.sourcePaths=np.array([],dtype=object)
        self.sourceWavelengths=np.array([],dtype=object)

        #arrays for attributes of lenses
        self.lensNames=np.array([],dtype=object)
        self.lensPositions=np.array([],dtype=object)
        self.lensRadii=np.array([],dtype=object)
        self.lensRefrinds=np.array([],dtype=object)
        self.lensRadius1s=np.array([],dtype=object)
        self.lensScale1s=np.array([],dtype=object)
        self.lensOffset1s=np.array([],dtype=object)
        self.lensk1s=np.array([],dtype=object)
        self.lensa41s=np.array([],dtype=object)
        self.lensa61s=np.array([],dtype=object)
        self.lensa81s=np.array([],dtype=object)
        self.lensa101s=np.array([],dtype=object)
        self.lensa121s=np.array([],dtype=object)
        self.lensRadius2s=np.array([],dtype=object)
        self.lensScale2s=np.array([],dtype=object)
        self.lensOffset2s=np.array([],dtype=object)
        self.lensk2s=np.array([],dtype=object)
        self.lensa42s=np.array([],dtype=object)
        self.lensa62s=np.array([],dtype=object)
        self.lensa82s=np.array([],dtype=object)
        self.lensa102s=np.array([],dtype=object)
        self.lensa122s=np.array([],dtype=object)
        self.lensThickness1s=np.array([],dtype=object)
        self.lensThickness2s=np.array([],dtype=object)
        self.lensSurface1Types=np.array([],dtype=object)
        self.lensSurface2Types=np.array([],dtype=object)
        self.lensPaths=np.array([],dtype=object)
        self.lensFrees=np.array([],dtype=object)

        #arrays for the attributes of achromats
        self.achromatNames=np.array([],dtype=object)
        self.achromatPositions=np.array([],dtype=object)
        self.achromatRadii=np.array([],dtype=object)
        self.achromatRefrind1s=np.array([],dtype=object)
        self.achromatRefrind2s=np.array([],dtype=object)
        self.achromatRadius1s=np.array([],dtype=object)
        self.achromatScale1s=np.array([],dtype=object)
        self.achromatOffset1s=np.array([],dtype=object)
        self.achromatk1s=np.array([],dtype=object)
        self.achromata41s=np.array([],dtype=object)
        self.achromata61s=np.array([],dtype=object)
        self.achromata81s=np.array([],dtype=object)
        self.achromata101s=np.array([],dtype=object)
        self.achromata121s=np.array([],dtype=object)
        self.achromatRadius2s=np.array([],dtype=object)
        self.achromatScale2s=np.array([],dtype=object)
        self.achromatOffset2s=np.array([],dtype=object)
        self.achromatk2s=np.array([],dtype=object)
        self.achromata42s=np.array([],dtype=object)
        self.achromata62s=np.array([],dtype=object)
        self.achromata82s=np.array([],dtype=object)
        self.achromata102s=np.array([],dtype=object)
        self.achromata122s=np.array([],dtype=object)
        self.achromatRadius3s=np.array([],dtype=object)
        self.achromatScale3s=np.array([],dtype=object)
        self.achromatOffset3s=np.array([],dtype=object)
        self.achromatk3s=np.array([],dtype=object)
        self.achromata43s=np.array([],dtype=object)
        self.achromata63s=np.array([],dtype=object)
        self.achromata83s=np.array([],dtype=object)
        self.achromata103s=np.array([],dtype=object)
        self.achromata123s=np.array([],dtype=object)
        self.achromatThickness1s=np.array([],dtype=object)
        self.achromatThickness2s=np.array([],dtype=object)
        self.achromatThickness3s=np.array([],dtype=object)
        self.achromatSurface1Types=np.array([],dtype=object)
        self.achromatSurface2Types=np.array([],dtype=object)
        self.achromatSurface3Types=np.array([],dtype=object)
        self.achromatPaths=np.array([],dtype=object)
        self.achromatFrees=np.array([],dtype=object)

        #array for zemax objects
        self.zemaxs=np.array([],dtype=object)
        self.zemaxNames=np.array([],dtype=object)
        self.zemaxFileNames=np.array([],dtype=object)
        self.zemaxPositions=np.array([],dtype=object)
        self.zemaxPaths=np.array([],dtype=object)
        self.zemaxWays=np.array([],dtype=object)
        self.zemaxFrees=np.array([],dtype=object)

        self.outFileArray=np.array([],dtype=object)
        self.preamble=np.array([],dtype=object)
        self.raySequence=np.array([],dtype=object)
        self.region=0
        self.projectName='Raytracing'
        self.menubar.setNativeMenuBar(False)
        self.actionOpen.triggered.connect(self.handleLoadButton)
        self.actionSave_As.triggered.connect(self.handleFileSaveAs)
        self.actionSave.triggered.connect(self.handleSaveButton)
        self.setWindowTitle(self.projectName)
        #self.setMenuBar(self.menubar
    def handleLoadButton(self):
        #self.masterWindow = MasterWindow(self)
        #self.masterWindow.cwd=self.cwd
        self.projectName = str(QtWidgets.QFileDialog.getOpenFileName()[0])
        print(self.projectName)
        openFile=open(self.projectName, 'r')
        lines=openFile.readlines()
        for line in lines:
            if line[0:12]=='source      ':
                self.loadSource(line[13:-1])
            elif line[0:12]=='lens        ':
                self.loadLens(line[13:-1])
            elif line[0:12]=='achromat    ':
                self.loadAchromat(line[13:-1])
            elif line[0:12]=='zemax lens  ':
                print(line[13:-1])
                self.loadZemax(line[13:-1])
            elif line[0:12]=='end point   ':
                self.endDistanceBox.setText(line[13:-1])
            elif line[0:12]=='region      ':
                self.region=int(line[13:-1])
            elif line[0:12]=='focus       ':
                if line[13:-1]=='True':
                    self.focus=True
                elif line[13:-1]=='False':
                    self.focus=False
        self.plotComponents()
        openFile.close()
        #self.masterWindow.show()


    def handleSourceButton(self):
        self.sourceWindow = SourceDialog(self)
        if self.sourceWindow.exec_()==QtWidgets.QDialog.Accepted:
            name, posy, posz, nRays, numAper, wavelength, path = self.sourceWindow.getValues()
            self.sourceNames=np.append(self.sourceNames, str(name))
            self.sourcePosys=np.append(self.sourcePosys, str(posy))
            self.sourcePoszs=np.append(self.sourcePoszs, str(posz))
            self.sourceNRays=np.append(self.sourceNRays, str(nRays))
            self.sourceNumApers=np.append(self.sourceNumApers, str(numAper))
            self.sourcePaths=np.append(self.sourcePaths, str(path))
            self.sourceWavelengths=np.append(self.sourceWavelengths, str(wavelength))

            self.sourceCombo.addItem(str(name))

            self.plotFigure.clear()
            self.plotComponents()

    def handleEditSource(self):
        index=self.sourceCombo.currentIndex()
        self.sourceWindow = SourceDialog(self)
        self.sourceWindow.nameBox.setText(self.sourceNames[index])
        self.sourceWindow.posyBox.setText(self.sourcePosys[index])
        self.sourceWindow.poszBox.setText(self.sourcePoszs[index])
        self.sourceWindow.nRaysBox.setText(self.sourceNRays[index])
        self.sourceWindow.numAperBox.setText(self.sourceNumApers[index])
        self.sourceWindow.saveloadBox.setText(self.sourcePaths[index])
        self.sourceWindow.wavelengthBox.setText(self.sourceWavelengths[index])
        if self.sourceWindow.exec_()==QtWidgets.QDialog.Accepted:
            name, posy, posz, nRays, numAper, wavelength, path = self.sourceWindow.getValues()
            self.sourceNames[index]=str(name)
            self.sourcePosys[index]=str(posy)
            self.sourcePoszs[index]=str(posz)
            self.sourceNRays[index]=str(nRays)
            self.sourceNumApers[index]=str(numAper)
            self.sourceWavelengths[index]=str(wavelength)
            self.sourcePaths[index]=str(path)
            self.sourceCombo.setItemText(index, name)

            self.plotFigure.clear()
            self.plotComponents()

    def handleDeleteSource(self):
        index=self.sourceCombo.currentIndex()
        self.sourceNames=np.concatenate((self.sourceNames[0:index],self.sourceNames[index+1:]))
        self.sourcePosys=np.concatenate((self.sourcePosys[0:index],self.sourcePosys[index+1:]))
        self.sourcePoszs=np.concatenate((self.sourcePoszs[0:index],self.sourcePoszs[index+1:]))
        self.sourceNRays=np.concatenate((self.sourceNRays[0:index],self.sourceNRays[index+1:]))
        self.sourceNumApers=np.concatenate((self.sourceNumApers[0:index],self.sourceNumApers[index+1:]))
        self.sourcePaths=np.concatenate((self.sourcePaths[0:index],self.sourcePaths[index+1:]))
        self.sourceWavelengths=np.concatenate((self.sourceWavelengths[0:index],self.sourceWavelengths[index+1:]))

        self.sourceCombo.clear()

        for name in self.sourceNames:
            self.sourceCombo.addItem(str(name))

        self.plotFigure.clear()
        self.plotComponents()

    def handleLensButton(self):
        self.lensWindow = LensDialog(self)
        if self.lensWindow.exec_()==QtWidgets.QDialog.Accepted:
            name, position, radius, refrind, radius1, scale1, offset1,\
                lensk1, lensa41, lensa61, lensa81, lensa101, lensa121,\
                radius2, scale2, offset2,\
                lensk2, lensa42, lensa62, lensa82, lensa102, lensa122,\
                thickness1, thickness2, surface1type, surface2type, path, free = self.lensWindow.getValues()
            self.lensNames=np.append(self.lensNames,str(name))
            self.lensPositions=np.append(self.lensPositions,str(position))
            self.lensRadii=np.append(self.lensRadii,str(radius))
            self.lensRefrinds=np.append(self.lensRefrinds,str(refrind))
            self.lensRadius1s=np.append(self.lensRadius1s,str(radius1))
            self.lensScale1s=np.append(self.lensScale1s,str(scale1))
            self.lensOffset1s=np.append(self.lensOffset1s,str(offset1))
            self.lensk1s=np.append(self.lensk1s,str(lensk1))
            self.lensa41s=np.append(self.lensa41s,str(lensa41))
            self.lensa61s=np.append(self.lensa61s,str(lensa61))
            self.lensa81s=np.append(self.lensa81s,str(lensa81))
            self.lensa101s=np.append(self.lensa101s,str(lensa101))
            self.lensa121s=np.append(self.lensa121s,str(lensa121))
            self.lensRadius2s=np.append(self.lensRadius2s,str(radius2))
            self.lensScale2s=np.append(self.lensScale2s,str(scale2))
            self.lensOffset2s=np.append(self.lensOffset2s,str(offset2))
            self.lensk2s=np.append(self.lensk2s,str(lensk2))
            self.lensa42s=np.append(self.lensa42s,str(lensa42))
            self.lensa62s=np.append(self.lensa62s,str(lensa62))
            self.lensa82s=np.append(self.lensa82s,str(lensa82))
            self.lensa102s=np.append(self.lensa102s,str(lensa102))
            self.lensa122s=np.append(self.lensa122s,str(lensa122))
            self.lensThickness1s=np.append(self.lensThickness1s,str(thickness1))
            self.lensThickness2s=np.append(self.lensThickness2s,str(thickness2))
            self.lensSurface1Types=np.append(self.lensSurface1Types,str(surface1type))
            self.lensSurface2Types=np.append(self.lensSurface2Types,str(surface2type))
            self.lensPaths=np.append(self.lensPaths,str(path))
            self.lensFrees=np.append(self.lensFrees,free)

            self.lensCombo.addItem(str(name))

            self.plotFigure.clear()
            self.plotComponents()

    def handleEditLens(self):
        index=self.lensCombo.currentIndex()
        self.lensWindow = LensDialog(self)
        self.lensWindow.nameBox.setText(self.lensNames[index])
        self.lensWindow.positionBox.setText(str(self.lensPositions[index]))
        self.lensWindow.radiusBox.setText(self.lensRadii[index])
        self.lensWindow.refrindBox.setText(self.lensRefrinds[index])
        self.lensWindow.radius1Box.setText(self.lensRadius1s[index])
        self.lensWindow.scale1Box.setText(self.lensScale1s[index])
        self.lensWindow.offset1Box.setText(self.lensOffset1s[index])
        self.lensWindow.kBox1.setText(self.lensk1s[index])
        self.lensWindow.a4Box1.setText(self.lensa41s[index])
        self.lensWindow.a6Box1.setText(self.lensa61s[index])
        self.lensWindow.a8Box1.setText(self.lensa81s[index])
        self.lensWindow.a10Box1.setText(self.lensa101s[index])
        self.lensWindow.a12Box1.setText(self.lensa121s[index])
        self.lensWindow.radius2Box.setText(self.lensRadius2s[index])
        self.lensWindow.scale2Box.setText(self.lensScale2s[index])
        self.lensWindow.offset2Box.setText(self.lensOffset2s[index])
        self.lensWindow.kBox2.setText(self.lensk2s[index])
        self.lensWindow.a4Box2.setText(self.lensa42s[index])
        self.lensWindow.a6Box2.setText(self.lensa62s[index])
        self.lensWindow.a8Box2.setText(self.lensa82s[index])
        self.lensWindow.a10Box2.setText(self.lensa102s[index])
        self.lensWindow.a12Box2.setText(self.lensa122s[index])
        self.lensWindow.thickness1Box.setText(self.lensThickness1s[index])
        self.lensWindow.thickness2Box.setText(self.lensThickness2s[index])
        self.lensWindow.surface1Combo.setCurrentIndex(int(self.lensSurface1Types[index]))
        self.lensWindow.showFrame1(int(self.lensSurface1Types[index]))
        self.lensWindow.surface2Combo.setCurrentIndex(int(self.lensSurface2Types[index]))
        self.lensWindow.showFrame2(int(self.lensSurface2Types[index]))
        self.lensWindow.saveloadBox.setText(self.lensPaths[index])
        if self.lensWindow.exec_()==QtWidgets.QDialog.Accepted:
           name, position, radius, refrind, radius1, scale1, offset1,\
               lensk1, lensa41, lensa61, lensa81, lensa101, lensa121,\
                radius2, scale2, offset2,\
                lensk2, lensa42, lensa62, lensa82, lensa102, lensa122,\
                thickness1, thickness2, surface1type, surface2type, path, free = self.lensWindow.getValues()
           self.lensNames[index]=str(name)
           self.lensPositions[index]=str(position)
           self.lensRadii[index]=str(radius)
           self.lensRefrinds[index]=str(refrind)
           self.lensRadius1s[index]=str(radius1)
           self.lensScale1s[index]=str(scale1)
           self.lensOffset1s[index]=str(offset1)
           self.lensk1s[index]=str(lensk1)
           self.lensa41s[index]=str(lensa41)
           self.lensa61s[index]=str(lensa61)
           self.lensa81s[index]=str(lensa81)
           self.lensa101s[index]=str(lensa101)
           self.lensa121s[index]=str(lensa121)
           self.lensRadius2s[index]=str(radius2)
           self.lensScale2s[index]=str(scale2)
           self.lensOffset2s[index]=str(offset2)
           self.lensk2s[index]=str(lensk2)
           self.lensa42s[index]=str(lensa42)
           self.lensa62s[index]=str(lensa62)
           self.lensa82s[index]=str(lensa82)
           self.lensa102s[index]=str(lensa102)
           self.lensa122s[index]=str(lensa122)
           self.lensThickness1s[index]=str(thickness1)
           self.lensThickness2s[index]=str(thickness2)
           self.lensSurface1Types[index]=str(surface1type)
           self.lensSurface2Types[index]=str(surface2type)
           self.lensPaths[index]=str(path)

           self.lensCombo.setItemText(index, name)

           self.plotFigure.clear()
           self.plotComponents()


    def handleDeleteLens(self):
        index=self.lensCombo.currentIndex()
        self.lensNames=np.concatenate((self.lensNames[0:index],self.lensNames[index+1:]))
        self.lensPositions=np.concatenate((self.lensPositions[0:index],self.lensPositions[index+1:]))
        self.lensRadii=np.concatenate((self.lensRadii[0:index],self.lensRadii[index+1:]))
        self.lensRefrinds=np.concatenate((self.lensRefrinds[0:index],self.lensRefrinds[index+1:]))
        self.lensRadius1s=np.concatenate((self.lensRadius1s[0:index],self.lensRadius1s[index+1:]))
        self.lensScale1s=np.concatenate((self.lensScale1s[0:index],self.lensScale1s[index+1:]))
        self.lensOffset1s=np.concatenate((self.lensOffset1s[0:index],self.lensOffset1s[index+1:]))
        self.lensk1s=np.concatenate((self.lensk1s[0:index],self.lensk1s[index+1:]))
        self.lensa41s=np.concatenate((self.lensa41s[0:index],self.lensa41s[index+1:]))
        self.lensa61s=np.concatenate((self.lensa61s[0:index],self.lensa61s[index+1:]))
        self.lensa81s=np.concatenate((self.lensa81s[0:index],self.lensa81s[index+1:]))
        self.lensa10s=np.concatenate((self.lensa101s[0:index],self.lensa101s[index+1:]))
        self.lensa121s=np.concatenate((self.lensa121s[0:index],self.lensa121s[index+1:]))
        self.lensRadius2s=np.concatenate((self.lensRadius2s[0:index],self.lensRadius2s[index+1:]))
        self.lensScale2s=np.concatenate((self.lensScale2s[0:index],self.lensScale2s[index+1:]))
        self.lensOffset2s=np.concatenate((self.lensOffset2s[0:index],self.lensOffset2s[index+1:]))
        self.lensk2s=np.concatenate((self.lensk2s[0:index],self.lensk2s[index+1:]))
        self.lensa42s=np.concatenate((self.lensa42s[0:index],self.lensa42s[index+1:]))
        self.lensa62s=np.concatenate((self.lensa62s[0:index],self.lensa62s[index+1:]))
        self.lensa82s=np.concatenate((self.lensa82s[0:index],self.lensa82s[index+1:]))
        self.lensa10s=np.concatenate((self.lensa102s[0:index],self.lensa102s[index+1:]))
        self.lensa122s=np.concatenate((self.lensa122s[0:index],self.lensa122s[index+1:]))
        self.lensThickness1s=np.concatenate((self.lensThickness1s[0:index],self.lensThickness1s[index+1:]))
        self.lensThickness2s=np.concatenate((self.lensThickness2s[0:index],self.lensThickness2s[index+1:]))
        self.lensSurface1Types=np.concatenate((self.lensSurface1Types[0:index],self.lensSurface1Types[index+1:]))
        self.lensSurface2Types=np.concatenate((self.lensSurface2Types[0:index],self.lensSurface2Types[index+1:]))
        self.lensPaths=np.concatenate((self.lensPaths[0:index],self.lensPaths[index+1:]))
        self.lensFrees=np.concatenate((self.lensFrees[0:index],self.lensFrees[index+1:]))

        self.lensCombo.clear()

        for name in self.lensNames:
            self.lensCombo.addItem(str(name))

        self.plotFigure.clear()
        self.plotComponents()


    def handleAchromatButton(self):
        self.achromatWindow = AchromatDialog(self)
        if self.achromatWindow.exec_()==QtWidgets.QDialog.Accepted:
            name, position, radius, refrind1, refrind2, radius1, scale1, offset1,\
                k1, a41, a61, a81, a101, a121,\
                radius2, scale2, offset2,\
                k2, a42, a62, a82, a102, a122,\
                radius3, scale3, offset3,\
                k3, a43, a63, a83, a103, a123,\
                thickness1, thickness2, thickness3,\
                surface1type, surface2type, surface3type, path, free=self.achromatWindow.getValues()
            self.achromatNames=np.append(self.achromatNames,str(name))
            self.achromatPositions=np.append(self.achromatPositions,str(position))
            self.achromatRadii=np.append(self.achromatRadii,str(radius))
            self.achromatRefrind1s=np.append(self.achromatRefrind1s,str(refrind1))
            self.achromatRefrind2s=np.append(self.achromatRefrind2s,str(refrind2))
            self.achromatRadius1s=np.append(self.achromatRadius1s,str(radius1))
            self.achromatScale1s=np.append(self.achromatScale1s,str(scale1))
            self.achromatOffset1s=np.append(self.achromatOffset1s,str(offset1))
            self.achromatk1s=np.append(self.achromatk1s,str(k1))
            self.achromata41s=np.append(self.achromata41s,str(a41))
            self.achromata61s=np.append(self.achromata61s,str(a61))
            self.achromata81s=np.append(self.achromata81s,str(a81))
            self.achromata101s=np.append(self.achromata101s,str(a101))
            self.achromata121s=np.append(self.achromata121s,str(a121))
            self.achromatRadius2s=np.append(self.achromatRadius2s,str(radius2))
            self.achromatScale2s=np.append(self.achromatScale2s,str(scale2))
            self.achromatOffset2s=np.append(self.achromatOffset2s,str(offset2))
            self.achromatk2s=np.append(self.achromatk2s,str(k2))
            self.achromata42s=np.append(self.achromata42s,str(a42))
            self.achromata62s=np.append(self.achromata62s,str(a62))
            self.achromata82s=np.append(self.achromata82s,str(a82))
            self.achromata102s=np.append(self.achromata102s,str(a102))
            self.achromata122s=np.append(self.achromata122s,str(a122))
            self.achromatRadius3s=np.append(self.achromatRadius3s,str(radius3))
            self.achromatScale3s=np.append(self.achromatScale3s,str(scale3))
            self.achromatOffset3s=np.append(self.achromatOffset3s,str(offset3))
            self.achromatk3s=np.append(self.achromatk3s,str(k3))
            self.achromata43s=np.append(self.achromata43s,str(a43))
            self.achromata63s=np.append(self.achromata63s,str(a63))
            self.achromata83s=np.append(self.achromata83s,str(a83))
            self.achromata103s=np.append(self.achromata103s,str(a103))
            self.achromata123s=np.append(self.achromata123s,str(a123))
            self.achromatThickness1s=np.append(self.achromatThickness1s,str(thickness1))
            self.achromatThickness2s=np.append(self.achromatThickness2s,str(thickness2))
            self.achromatThickness3s=np.append(self.achromatThickness3s,str(thickness3))
            self.achromatSurface1Types=np.append(self.achromatSurface1Types,str(surface1type))
            self.achromatSurface2Types=np.append(self.achromatSurface2Types,str(surface2type))
            self.achromatSurface3Types=np.append(self.achromatSurface3Types,str(surface3type))
            self.achromatPaths=np.append(self.achromatPaths,str(path))
            self.achromatFrees=np.append(self.achromatFrees,free)

            self.achromatCombo.addItem(str(name))

            self.plotFigure.clear()
            self.plotComponents()

    def handleEditAchromat(self):
        index=self.achromatCombo.currentIndex()
        self.achromatWindow = AchromatDialog(self)
        self.achromatWindow.nameBox.setText(self.achromatNames[index])
        self.achromatWindow.positionBox.setText(self.achromatPositions[index])
        self.achromatWindow.radiusBox.setText(self.achromatRadii[index])
        self.achromatWindow.refrind1Box.setText(self.achromatRefrind1s[index])
        self.achromatWindow.refrind2Box.setText(self.achromatRefrind2s[index])
        self.achromatWindow.radius1Box.setText(self.achromatRadius1s[index])
        self.achromatWindow.scale1Box.setText(self.achromatScale1s[index])
        self.achromatWindow.offset1Box.setText(self.achromatOffset1s[index])
        self.achromatWindow.kBox1.setText(self.achromatk1s[index])
        self.achromatWindow.a4Box1.setText(self.achromata41s[index])
        self.achromatWindow.a6Box1.setText(self.achromata61s[index])
        self.achromatWindow.a8Box1.setText(self.achromata81s[index])
        self.achromatWindow.a10Box1.setText(self.achromata101s[index])
        self.achromatWindow.a12Box1.setText(self.achromata121s[index])
        self.achromatWindow.radius2Box.setText(self.achromatRadius2s[index])
        self.achromatWindow.scale2Box.setText(self.achromatScale2s[index])
        self.achromatWindow.offset2Box.setText(self.achromatOffset2s[index])
        self.achromatWindow.kBox2.setText(self.achromatk2s[index])
        self.achromatWindow.a4Box2.setText(self.achromata42s[index])
        self.achromatWindow.a6Box2.setText(self.achromata62s[index])
        self.achromatWindow.a8Box2.setText(self.achromata82s[index])
        self.achromatWindow.a10Box2.setText(self.achromata102s[index])
        self.achromatWindow.a12Box2.setText(self.achromata122s[index])
        self.achromatWindow.radius3Box.setText(self.achromatRadius3s[index])
        self.achromatWindow.scale3Box.setText(self.achromatScale3s[index])
        self.achromatWindow.offset3Box.setText(self.achromatOffset3s[index])
        self.achromatWindow.kBox3.setText(self.achromatk3s[index])
        self.achromatWindow.a4Box3.setText(self.achromata43s[index])
        self.achromatWindow.a6Box3.setText(self.achromata63s[index])
        self.achromatWindow.a8Box3.setText(self.achromata83s[index])
        self.achromatWindow.a10Box3.setText(self.achromata103s[index])
        self.achromatWindow.a12Box3.setText(self.achromata123s[index])
        self.achromatWindow.thickness1Box.setText(self.achromatThickness1s[index])
        self.achromatWindow.thickness2Box.setText(self.achromatThickness2s[index])
        self.achromatWindow.thickness3Box.setText(self.achromatThickness3s[index])
        self.achromatWindow.surface1Combo.setCurrentIndex(int(self.achromatSurface1Types[index]))
        self.achromatWindow.showFrame1(int(self.achromatSurface1Types[index]))
        self.achromatWindow.surface2Combo.setCurrentIndex(int(self.achromatSurface2Types[index]))
        self.achromatWindow.showFrame2(int(self.achromatSurface2Types[index]))
        self.achromatWindow.surface3Combo.setCurrentIndex(int(self.achromatSurface3Types[index]))
        self.achromatWindow.showFrame3(int(self.achromatSurface3Types[index]))
        self.achromatWindow.saveloadBox.setText(self.achromatPaths[index])
        if self.achromatWindow.exec_()==QtWidgets.QDialog.Accepted:
           name, position, radius, refrind1, refrind2, radius1, scale1, offset1,\
               k1, a41, a61, a81, a101, a121,\
               radius2, scale2, offset2,\
               k2, a42, a62, a82, a102, a122,\
               radius3, scale3, offset3,\
               k3, a43, a63, a83, a103, a123,\
               thickness1, thickness2, thickness3,\
               surface1type, surface2type, surface3type, path, free = self.achromatWindow.getValues()
           self.achromatNames[index]=str(name)
           self.achromatPositions[index]=str(position)
           self.achromatRadii[index]=str(radius)
           self.achromatRefrind1s[index]=str(refrind1)
           self.achromatRefrind2s[index]=str(refrind2)
           self.achromatRadius1s[index]=str(radius1)
           self.achromatScale1s[index]=str(scale1)
           self.achromatOffset1s[index]=str(offset1)
           self.achromatk1s[index]=str(k1)
           self.achromata41s[index]=str(a41)
           self.achromata61s[index]=str(a61)
           self.achromata81s[index]=str(a81)
           self.achromata101s[index]=str(a101)
           self.achromata121s[index]=str(a121)
           self.achromatRadius2s[index]=str(radius2)
           self.achromatScale2s[index]=str(scale2)
           self.achromatOffset2s[index]=str(offset2)
           self.achromatk2s[index]=str(k2)
           self.achromata42s[index]=str(a42)
           self.achromata62s[index]=str(a62)
           self.achromata82s[index]=str(a82)
           self.achromata102s[index]=str(a102)
           self.achromata122s[index]=str(a122)
           self.achromatRadius3s[index]=str(radius3)
           self.achromatScale3s[index]=str(scale3)
           self.achromatOffset3s[index]=str(offset3)
           self.achromatk3s[index]=str(k3)
           self.achromata43s[index]=str(a43)
           self.achromata63s[index]=str(a63)
           self.achromata83s[index]=str(a83)
           self.achromata103s[index]=str(a103)
           self.achromata123s[index]=str(a123)
           self.achromatThickness1s[index]=str(thickness1)
           self.achromatThickness2s[index]=str(thickness2)
           self.achromatThickness3s[index]=str(thickness3)
           self.achromatSurface1Types[index]=str(surface1type)
           self.achromatSurface2Types[index]=str(surface2type)
           self.achromatSurface3Types[index]=str(surface3type)
           self.achromatPaths[index]=str(path)

           self.achromatCombo.setItemText(index, name)

           self.plotFigure.clear()
           self.plotComponents()


    def handleDeleteAchromat(self):
        index=self.achromatCombo.currentIndex()
        self.achromatNames=np.concatenate((self.achromatNames[0:index],self.achromatNames[index+1:]))
        self.achromatPositions=np.concatenate((self.achromatPositions[0:index],self.achromatPositions[index+1:]))
        self.achromatRadii=np.concatenate((self.achromatRadii[0:index],self.achromatRadii[index+1:]))
        self.achromatRefrind1s=np.concatenate((self.achromatRefrind1s[0:index],self.achromatRefrind1s[index+1:]))
        self.achromatRefrind2s=np.concatenate((self.achromatRefrind2s[0:index],self.achromatRefrind2s[index+1:]))
        self.achromatRadius1s=np.concatenate((self.achromatRadius1s[0:index],self.achromatRadius1s[index+1:]))
        self.achromatScale1s=np.concatenate((self.achromatScale1s[0:index],self.achromatScale1s[index+1:]))
        self.achromatOffset1s=np.concatenate((self.achromatOffset1s[0:index],self.achromatOffset1s[index+1:]))
        self.achromatk1s=np.concatenate((self.achromatk1s[0:index],self.achromatk1s[index+1:1]))
        self.achromata41s=np.concatenate((self.achromata41s[0:index],self.achromata41s[index+1:1]))
        self.achromata61s=np.concatenate((self.achromata61s[0:index],self.achromata61s[index+1:1]))
        self.achromata81s=np.concatenate((self.achromata81s[0:index],self.achromata81s[index+1:1]))
        self.achromata101s=np.concatenate((self.achromata101s[0:index],self.achromata101s[index+1:1]))
        self.achromata121s=np.concatenate((self.achromata121s[0:index],self.achromata121s[index+1:1]))
        self.achromatRadius2s=np.concatenate((self.achromatRadius2s[0:index],self.achromatRadius2s[index+1:]))
        self.achromatScale2s=np.concatenate((self.achromatScale2s[0:index],self.achromatScale2s[index+1:]))
        self.achromatOffset2s=np.concatenate((self.achromatOffset2s[0:index],self.achromatOffset2s[index+1:]))
        self.achromatk2s=np.concatenate((self.achromatk2s[0:index],self.achromatk2s[index+1:1]))
        self.achromata42s=np.concatenate((self.achromata42s[0:index],self.achromata42s[index+1:1]))
        self.achromata62s=np.concatenate((self.achromata62s[0:index],self.achromata62s[index+1:1]))
        self.achromata82s=np.concatenate((self.achromata82s[0:index],self.achromata82s[index+1:1]))
        self.achromata102s=np.concatenate((self.achromata102s[0:index],self.achromata102s[index+1:1]))
        self.achromata122s=np.concatenate((self.achromata122s[0:index],self.achromata122s[index+1:1]))
        self.achromatRadius3s=np.concatenate((self.achromatRadius3s[0:index],self.achromatRadius3s[index+1:]))
        self.achromatScale3s=np.concatenate((self.achromatScale3s[0:index],self.achromatScale3s[index+1:]))
        self.achromatOffset3s=np.concatenate((self.achromatOffset3s[0:index],self.achromatOffset3s[index+1:]))
        self.achromatk3s=np.concatenate((self.achromatk3s[0:index],self.achromatk3s[index+1:1]))
        self.achromata43s=np.concatenate((self.achromata43s[0:index],self.achromata43s[index+1:1]))
        self.achromata63s=np.concatenate((self.achromata63s[0:index],self.achromata63s[index+1:1]))
        self.achromata83s=np.concatenate((self.achromata83s[0:index],self.achromata83s[index+1:1]))
        self.achromata103s=np.concatenate((self.achromata103s[0:index],self.achromata103s[index+1:1]))
        self.achromata123s=np.concatenate((self.achromata123s[0:index],self.achromata123s[index+1:1]))
        self.achromatThickness1s=np.concatenate((self.achromatThickness1s[0:index],self.achromatThickness1s[index+1:]))
        self.achromatThickness2s=np.concatenate((self.achromatThickness2s[0:index],self.achromatThickness2s[index+1:]))
        self.achromatThickness3s=np.concatenate((self.achromatThickness3s[0:index],self.achromatThickness3s[index+1:]))
        self.achromatSurface1Types=np.concatenate((self.achromatSurface1Types[0:index],self.achromatSurface1Types[index+1:]))
        self.achromatSurface2Types=np.concatenate((self.achromatSurface2Types[0:index],self.achromatSurface2Types[index+1:]))
        self.achromatSurface3Types=np.concatenate((self.achromatSurface3Types[0:index],self.achromatSurface3Types[index+1:]))
        self.achromatPaths=np.concatenate((self.achromatPaths[0:index],self.achromatPaths[index+1:]))
        self.achromatFrees=np.concatenate((self.achromatFrees[0:index],self.acrhomatFrees[index+1:]))

        self.achromatCombo.clear()

        for name in self.achromatNames:
            self.achromatCombo.addItem(str(name))

        self.plotFigure.clear()
        self.plotComponents()


    def handleZemaxButton(self):
        self.zemaxWindow = ZemaxDialog(self)
        if self.zemaxWindow.exec_()==QtWidgets.QDialog.Accepted:
            fileName, zemaxFileName, name, position, way, free = self.zemaxWindow.getValues()
            self.zemaxs=np.append(self.zemaxs,zm.zemaxlens(position, zemaxFileName, way))
            self.zemaxFileNames=np.append(self.zemaxFileNames, str(zemaxFileName))
            self.zemaxPositions=np.append(self.zemaxPositions, float(position))
            self.zemaxNames=np.append(self.zemaxNames, str(name))
            self.zemaxPaths=np.append(self.zemaxPaths, str(fileName))
            self.zemaxWays=np.append(self.zemaxWays, way)
            self.zemaxFrees=np.append(self.zemaxFrees, free)

            self.zemaxCombo.addItem(str(name))

            self.plotFigure.clear()
            self.plotComponents()

    def handleEditZemax(self):
        index=int(self.zemaxCombo.currentIndex())
        self.zemaxWindow = ZemaxDialog(self)
        self.zemaxWindow.nameBox.setText(self.zemaxNames[index])
        self.zemaxWindow.positionBox.setText(str(self.zemaxPositions[index]))
        self.zemaxWindow.zemaxFileBox.setText(self.zemaxFileNames[index])
        self.zemaxWindow.fileBox.setText(self.zemaxPaths[index])
        self.zemaxWindow.way=self.zemaxWays[index]
        if self.zemaxWindow.exec_()==QtWidgets.QDialog.Accepted:
            path, zemaxFileName, name, position, way, free = self.zemaxWindow.getValues()
            self.zemaxNames[index]=str(name)
            self.zemaxPositions[index]=str(position)
            self.zemaxFileNames[index]=str(zemaxFileName)
            self.zemaxPaths[index]=str(path)
            self.zemaxWays[index]=way
            self.zemaxs[index]=zm.zemaxlens(position, zemaxFileName, way)

            self.zemaxCombo.setItemText(index, name)

            self.plotFigure.clear()
            self.plotComponents()


    def handleDeleteZemax(self):
        index=int(self.zemaxCombo.currentIndex())
        self.zemaxNames=np.concatenate((self.zemaxNames[0:index],self.zemaxNames[index+1:]))
        self.zemaxPositions=np.concatenate((self.zemaxPositions[0:index],self.zemaxPositions[index+1:]))
        self.zemaxFileNames=np.concatenate((self.zemaxFileNames[0:index],self.zemaxFileNames[index+1:]))
        self.zemaxPaths=np.concatenate((self.zemaxPaths[0:index],self.zemaxPaths[index+1:]))
        self.zemaxs=np.concatenate((self.zemaxs[0:index],self.zemaxs[index+1:]))
        self.zemaxWays=np.concatenate((self.zemaxWays[0:index],self.zemaxWays[index+1:]))
        self.zemaxFrees=np.concatenate((self.zemaxFrees[0:index],self.zemaxFrees[index+1:]))

        self.zemaxCombo.clear()

        for name in self.zemaxNames:
            self.zemaxCombo.addItem(str(name))

        self.zemaxCombo.setCurrentIndex(len(self.zemaxNames)-1)
        self.plotFigure.clear()
        self.plotComponents()




    def handleWriteButton(self):
        #array of strings to write to a .py script which will do the raytracing
        self.outFileArray=np.array([])
        self.preamble=np.array([])
        self.raySequence=np.array([])

        self.preamble=np.append(self.preamble, 'from libraytrace import asphere, findline, addzemax, addachromat, addlens, addaperture, startraytrace, stopraytrace \n')
        self.preamble=np.append(self.preamble, 'import libraytrace as lrt\n')
        self.preamble=np.append(self.preamble, 'import numpy as np\n')
        self.preamble=np.append(self.preamble, 'import matplotlib.pyplot as plt\n')
        self.preamble=np.append(self.preamble, 'import shared\n')
        self.preamble=np.append(self.preamble, 'import warnings\n')
        self.preamble=np.append(self.preamble, 'import zemax as zm\n')
        self.preamble=np.append(self.preamble, "warnings.filterwarnings('error')\n")
        self.preamble=np.append(self.preamble, 'shared.mycount=0\n')
        self.preamble=np.append(self.preamble, 'def runRayTrace(positionArray):      #positions of optical elements in increasing order\n')
        self.preamble=np.append(self.preamble, '    shared.endPoint=' + str(self.endDistanceBox.text()) + '\n')

        totalPositions=np.concatenate((self.lensPositions, self.achromatPositions, self.zemaxPositions))
        totalPositions=totalPositions.astype(float)
        totalPositions.sort()
        print(totalPositions)
        for i in range(0,len(self.lensNames)):
            name=self.lensNames[i]
            index=np.where(totalPositions==float(self.lensPositions[i]))[0][0]
            self.preamble=np.append(self.preamble, '    '+name+'position=positionArray['+str(index)+']\n')

        for i in range(0,len(self.achromatNames)):
            name=self.achromatNames[i]
            index=np.where(totalPositions==float(self.achromatpositions[i]))[0][0]
            self.preamble=np.append(self.preamble, '    '+name+'position=positionArray['+str(index)+']\n')

        for i in range(0,len(self.zemaxNames)):
            name=self.zemaxNames[i]
            index=np.where(totalPositions==float(self.zemaxPositions[i]))[0][0]
            self.preamble=np.append(self.preamble, '    '+name+'position=positionArray['+str(index)+']\n')


        self.raySequence=np.append(self.raySequence,'####### raytracing sequence starts ########\n')
        self.raySequence=np.append(self.raySequence,'\n')

        self.raySequence=np.append(self.raySequence, '    histy = [];\n')
        self.raySequence=np.append(self.raySequence, '    for i in range(0, len(sPosys)):\n')

        self.raySequence=np.append(self.raySequence, '        source=sourceArray[i]\n')

        self.raySequence=np.append(self.raySequence, '        ta,tb,tz,ty = startraytrace(sPoszs[i], sPosys[i], sNRays[i], sNumApers[i], source);\n')


        sharedFile=open('shared.py', 'w')
        sharedFile.close()

        outFile=open('temp.py', 'w')

        self.preamble=np.append(self.preamble, '    sPosys=np.array([])\n')
        self.preamble=np.append(self.preamble, '    sPoszs=np.array([])\n')
        self.preamble=np.append(self.preamble, '    sNRays=np.array([])\n')
        self.preamble=np.append(self.preamble, '    sNumApers=np.array([])\n')
        self.preamble=np.append(self.preamble, '    sourceArray=np.array([])\n')

        for i in range(0, len(self.sourceNames)):
            name=self.sourceNames[i]
            posy=self.sourcePosys[i]
            posz=self.sourcePoszs[i]
            nRays=self.sourceNRays[i]
            numAper=self.sourceNumApers[i]

            self.preamble=np.append(self.preamble, '    '+name+'=lrt.source()\n')
            self.preamble=np.append(self.preamble, '    '+name+'.wavelength='+str(self.sourceWavelengths[i])+'\n')
            self.preamble=np.append(self.preamble, '    sourceArray=np.append(sourceArray,'+name+')\n')
            self.preamble=np.append(self.preamble, '    sPosys=np.append(sPosys,'+posy+')\n')
            self.preamble=np.append(self.preamble, '    sPoszs=np.append(sPoszs,'+posz+')\n')
            self.preamble=np.append(self.preamble, '    sNRays=np.append(sNRays,'+nRays+')\n')
            self.preamble=np.append(self.preamble, '    sNumApers=np.append(sNumApers,'+numAper+')\n')




        for i in range(0, len(self.lensNames)):
            name=self.lensNames[i]
            position=self.lensPositions[i]
            radius=self.lensRadii[i]
            refrind=self.lensRefrinds[i]
            radius1=self.lensRadius1s[i]
            scale1=self.lensScale1s[i]
            offset1=self.lensOffset1s[i]
            k1=self.lensk1s[i]
            a41=self.lensa41s[i]
            a61=self.lensa61s[i]
            a81=self.lensa81s[i]
            a101=self.lensa101s[i]
            a121=self.lensa121s[i]
            radius2=self.lensRadius2s[i]
            scale2=self.lensScale2s[i]
            offset2=self.lensOffset2s[i]
            k2=self.lensk2s[i]
            a42=self.lensa42s[i]
            a62=self.lensa62s[i]
            a82=self.lensa82s[i]
            a102=self.lensa102s[i]
            a122=self.lensa122s[i]
            thickness1=self.lensThickness1s[i]
            thickness2=self.lensThickness2s[i]
            surface1type=self.lensSurface1Types[i]
            surface2type=self.lensSurface2Types[i]

            self.preamble=np.append(self.preamble, "    "+name+"radius="+radius+";\n")
            if int(surface1type)==0:   #surface 1 is an asphere
                surface1def="    "+name+"radius1="+radius1+";\n"+\
                    "    "+name+"scale1="+scale1+";\n"+\
                    "    "+name+"offset1="+offset1+";\n"+\
                    "    "+name+"k1="+k1+";\n"+\
                    "    "+name+"a41="+a41+";\n"+\
                    "    "+name+"a61="+a61+";\n"+\
                    "    "+name+"a81="+a81+";\n"+\
                    "    "+name+"a101="+a101+";\n"+\
                    "    "+name+"a121="+a121+";\n"+\
                    "    "+name+"f1= lambda y:"+name+"scale1*asphere(y,"\
                    +name+"radius1,"+name+"k1,np.array([0,0,0,0,"+name+"a41,0,"+name+"a61,0,"+name+"a81,0,"+name+"a101,0,"+name+"a121]))+"+name+"offset1"+";\n"
            elif int(surface1type)==1:  #surface 1 is flat
                surface1def="    "+name+"thickness1="+thickness1+';\n'+\
                    "    "+name+"f1= lambda y: 0.0*y+"+name+"thickness1;\n"
            else:
                print("surface1type", surface1type)
            if int(surface2type)==0:   #surface 2 is an asphere
                surface2def="    "+name+"radius2="+radius2+";\n"+\
                    "    "+name+"scale2="+scale2+";\n"+\
                    "    "+name+"offset2="+offset2+";\n"+\
                    "    "+name+"k2="+k2+";\n"+\
                    "    "+name+"a42="+a42+";\n"+\
                    "    "+name+"a62="+a62+";\n"+\
                    "    "+name+"a82="+a82+";\n"+\
                    "    "+name+"a102="+a102+";\n"+\
                    "    "+name+"a122="+a122+";\n"+\
                    "    "+name+"f2= lambda y: "+name+"scale2*asphere(y,"\
                    +name+"radius2,"+name+"k2,np.array([0,0,0,0,"+name+"a42,0,"+name+"a62,0,"+name+"a82,0,"+name+"a102,0,"+name+"a122]))+"+name+"offset2"+";\n"
            elif int(surface2type)==1:  #surface 2 is flat
                surface2def="    "+name+"thickness2="+thickness2+';\n'+\
                    "    "+name+"f2= lambda y: 0.0*y+"+name+"thickness2;\n"
            else:
                print("surface2type", surface2type)


            self.preamble=np.append(self.preamble," \n")
            self.preamble=np.append(self.preamble,surface1def+"\n")
            self.preamble=np.append(self.preamble," \n")
            self.preamble=np.append(self.preamble,surface2def+"\n")


            self.preamble=np.append(self.preamble," \n")
            #self.preamble=np.append(self.preamble,"    "+name+"position="+position+";\n")
            self.preamble=np.append(self.preamble,"    "+name+"radius="+radius+";\n")
            self.preamble=np.append(self.preamble,"    "+name+"refrind="+refrind+";\n")
            self.preamble=np.append(self.preamble,"    "+name+"center=0.0;\n")

        for i in range(0, len(self.achromatNames)):
            name=self.achromatNames[i]
            position=self.achromatPositions[i]
            radius=self.achromatRadii[i]
            refrind1=self.achromatRefrind1s[i]
            refrind2=self.achromatRefrind2s[i]
            radius1=self.achromatRadius1s[i]
            scale1=self.achromatScale1s[i]
            offset1=self.achromatOffset1s[i]
            k1=self.achromatk1s[i]
            a41=self.achromata41s[i]
            a61=self.achromata61s[i]
            a81=self.achromata81s[i]
            a101=self.achromata101s[i]
            a121=self.achromata121s[i]
            radius2=self.achromatRadius2s[i]
            scale2=self.achromatScale2s[i]
            offset2=self.achromatOffset2s[i]
            k2=self.achromatk2s[i]
            a42=self.achromata42s[i]
            a62=self.achromata62s[i]
            a82=self.achromata82s[i]
            a102=self.achromata102s[i]
            a122=self.achromata122s[i]
            radius3=self.achromatRadius3s[i]
            scale3=self.achromatScale3s[i]
            offset3=self.achromatOffset3s[i]
            k3=self.achromatk3s[i]
            a43=self.achromata43s[i]
            a63=self.achromata63s[i]
            a83=self.achromata83s[i]
            a103=self.achromata103s[i]
            a123=self.achromata123s[i]
            thickness1=self.achromatThickness1s[i]
            thickness2=self.achromatThickness2s[i]
            thickness3=self.achromatThickness3s[i]
            surface1type=self.achromatSurface1Types[i]
            surface2type=self.achromatSurface2Types[i]
            surface3type=self.achromatSurface3Types[i]

            self.preamble=np.append(self.preamble, "    "+name+"radius="+radius+";\n")
            if int(surface1type)==0:   #surface 1 is an asphere
                surface1def="    "+name+"radius1="+radius1+";\n"+\
                    "    "+name+"scale1="+scale1+";\n"+\
                    "    "+name+"offset1="+offset1+";\n"+\
                    "    "+name+"k1="+k1+";\n"+\
                    "    "+name+"a41="+a41+";\n"+\
                    "    "+name+"a61="+a61+";\n"+\
                    "    "+name+"a81="+a81+";\n"+\
                    "    "+name+"a101="+a101+";\n"+\
                    "    "+name+"a121="+a121+";\n"+\
                    "    "+name+"fac1= lambda y:"+name+"scale1*asphere(y,"\
                    +name+"radius1,"+name+"k1,np.array([0,0,0,0,"+name+"a41,0,"+name+"a61,0,"+name+"a81,0,"+name+"a101,0,"+name+"a121]))+"+name+"offset1"+";\n"
            if int(surface1type)==1:  #surface 1 is flat
                surface1def="    "+name+"thickness1="+thickness1+';\n'+\
                    "    "+name+"fac1= lambda y:0.0*y+"+name+"thickness1;\n"
            if int(surface2type)==0:   #surface 2 is an asphere
                surface2def="    "+name+"radius2="+radius2+";\n"+\
                    "    "+name+"scale2="+scale2+";\n"+\
                    "    "+name+"offset2="+offset2+";\n"+\
                    "    "+name+"k2="+k2+";\n"+\
                    "    "+name+"a42="+a42+";\n"+\
                    "    "+name+"a62="+a62+";\n"+\
                    "    "+name+"a82="+a82+";\n"+\
                    "    "+name+"a102="+a102+";\n"+\
                    "    "+name+"a122="+a122+";\n"+\
                    "    "+name+"fac2= lambda y:"+name+"scale2*asphere(y,"\
                    +name+"radius2,"+name+"k2,np.array([0,0,0,0,"+name+"a42,0,"+name+"a62,0,"+name+"a82,0,"+name+"a102,0,"+name+"a122]))+"+name+"offset2"+";\n"
            if int(surface2type)==1:  #surface 2 is flat
                surface2def="    "+name+"thickness2="+thickness2+';\n'+\
                    "    "+name+"fac2= lambda y: 0.0*y+"+name+"thickness2;\n"
            if int(surface3type)==0:   #surface 3 is an asphere
                surface3def="    "+name+"radius3="+radius3+";\n"+\
                    "    "+name+"scale3="+scale3+";\n"+\
                    "    "+name+"offset3="+offset3+";\n"+\
                    "    "+name+"k3="+k3+";\n"+\
                    "    "+name+"a43="+a43+";\n"+\
                    "    "+name+"a63="+a63+";\n"+\
                    "    "+name+"a83="+a83+";\n"+\
                    "    "+name+"a103="+a103+";\n"+\
                    "    "+name+"a123="+a123+";\n"+\
                    "    "+name+"fac3= lambda y: "+name+"scale3*asphere(y,"\
                    +name+"radius3,"+name+"k3,np.array([0,0,0,0,"+name+"a43,0,"+name+"a63,0,"+name+"a83,0,"+name+"a103,0,"+name+"a123]))+"+name+"offset3"+";\n"
            if int(surface3type)==1:  #surface 3 is flat
                surface3def="    "+name+"thickness3="+thickness3+';\n'+\
                    "    "+name+"fac3= lambda y:0.0*y+"+name+"thickness3;\n"


            self.preamble=np.append(self.preamble," \n")
            self.preamble=np.append(self.preamble,surface1def+"\n")
            self.preamble=np.append(self.preamble," \n")
            self.preamble=np.append(self.preamble,surface2def+"\n")
            self.preamble=np.append(self.preamble," \n")
            self.preamble=np.append(self.preamble,surface3def+"\n")

            self.preamble=np.append(self.preamble," \n")
#            self.preamble=np.append(self.preamble,"    "+name+"position="+position+";\n")
            self.preamble=np.append(self.preamble,"    "+name+"radius="+radius+";\n")
            self.preamble=np.append(self.preamble,"    "+name+"refrind1="+refrind1+";\n")
            self.preamble=np.append(self.preamble,"    "+name+"refrind2="+refrind2+";\n")


        for i in range(0, len(self.zemaxs)):
            name=self.zemaxNames[i]
            position=self.zemaxPositions[i]
            fileName=self.zemaxFileNames[i]
            way=self.zemaxWays[i]
#            self.preamble=np.append(self.preamble, "    "+name+"position="+str(position)+"\n")
            self.preamble=np.append(self.preamble, "    "+name+"fileName="+'"'+fileName+'"'+"\n")
            self.preamble=np.append(self.preamble, "    "+name+"zemax=zm.zemaxlens("+name+"position,"+name+"fileName, "+str(way)+") \n")

        self.preamble=np.append(self.preamble,'    totalVariance=0\n')
        self.preamble=np.append(self.preamble,'####### preamble ends #######\n')
        self.preamble=np.append(self.preamble,'\n')

        writtenLenses=np.array([])
        writtenAchromats=np.array([])
        writtenZemaxs=np.array([])
        tempLensNames=self.lensNames
        tempAchromatNames=self.achromatNames
        tempZemaxNames=self.zemaxNames
        nLenses=len(self.lensNames)
        nAchromats=len(self.achromatNames)
        nZemaxs=len(self.zemaxNames)
        totalPositions=np.concatenate((self.lensPositions, self.achromatPositions, self.zemaxPositions))   #so lenses are totalPositions[0:len(nLenses)],
                                                                                                     #achromats are totalPositions[len(nLenses):len(nLenses)+len(nAchromats)]
                                                                                                     #zemaxs are totalPositions[len(nLenses)+len(nAchromats):len(totalPositions)]
        totalPositions=totalPositions.astype(float)
        k=len(totalPositions)
        while k > 0:

            currentIndex=np.argmin(totalPositions)
            if currentIndex < nLenses:
                name=tempLensNames[currentIndex]
                self.raySequence=np.append(self.raySequence,"        ta,tb,tz,ty = addlens(ta, tb, tz, ty,"+name+"position,"\
                                           +name+"f1,"+name+"f2,"+name+"radius,"+name+"refrind,"+name+"center, source);\n")
                nLenses=nLenses-1
                tempLensNames=np.delete(tempLensNames, currentIndex)
            elif nLenses <= currentIndex and currentIndex < nLenses + nAchromats:
                name=tempAchromatNames[currentIndex-nLenses]
                self.raySequence=np.append(self.raySequence,"        ta,tb,tz,ty = addachromat(ta, tb, tz, ty,"+name+"position,"\
                                           +name+"fac1,"+name+"fac2,"+name+"fac3,"+name+"radius,"+name+"refrind1,"+name+"refrind2, source);\n")
                nAchromats=nAchromats-1
                tempAchromatNames=np.delete(tempAchromatNames, currentIndex-nLenses)
            else:
                name=tempZemaxNames[currentIndex-nLenses-nAchromats]
                self.raySequence=np.append(self.raySequence,"        ta,tb,tz,ty = addzemax(ta, tb, tz, ty,"+name+"zemax, source);\n")
                tempZemaxNames=np.delete(tempZemaxNames, currentIndex-nLenses-nAchromats)


            totalPositions=np.delete(totalPositions, currentIndex)
            k=k-1



        for i in range(0,len(self.preamble)):
            outFile.write(self.preamble[i])

        for i in range(0,len(self.raySequence)):
            outFile.write(self.raySequence[i])

        endDistance=self.endDistanceBox.text()
        outFile.write("        thisty=stopraytrace(ta,tb,tz,ty,"+endDistance+',source)\n')
        if self.focus==True:
            outFile.write('        totalVariance=totalVariance+source.getVariance('+str(self.region)+')\n')
        else:
            outFile.write('        totalVariance=totalVariance+source.getCollimate('+str(self.region)+')\n')
        outFile.write('    print("total variance is:", totalVariance)\n')
        outFile.write('    \n')
        outFile.write('    return totalVariance\n')
        outFile.close()
        logfile=open('/tmp/rtlogfile','a')
        logfile.write(totalVariance,'\n')
        logfile.close()

    def handleRunButton(self):
        import temp
        reload(temp)
        self.plotFigure.clear()
        shared.startzarray=np.array([])
        shared.stopzarray=np.array([])
        shared.startyarray=np.array([])
        shared.stopyarray=np.array([])
        totalPositions=np.concatenate((self.lensPositions, self.achromatPositions, self.zemaxPositions))
        totalPositions=totalPositions.astype(float)
        totalPositions.sort()
        temp.runRayTrace(totalPositions)
        for i in range(0, len(shared.startzarray)):
            self.plotFigure.plot([shared.startzarray[i], shared.stopzarray[i]],\
                                 [shared.startyarray[i], shared.stopyarray[i]], pen='r')

        self.plotComponents()

    def handleOptimiseButton(self):
        import temp
        reload(temp)
        self.plotFigure.clear()
        shared.startzarray=np.array([])
        shared.stopzarray=np.array([])
        shared.startyarray=np.array([])
        shared.stopyarray=np.array([])
        totalPositions=np.concatenate((self.lensPositions, self.achromatPositions, self.zemaxPositions))
        allFrees=np.concatenate((self.lensFrees, self.achromatFrees, self.zemaxFrees))
        totalPositions=totalPositions.astype(float)

        a=np.vstack((totalPositions, allFrees)).T
        a=np.array(sorted(a, key=lambda x:x[0])).T
        totalPositions=a[0]
        allFrees=a[1]

        varyArray=allFrees
        def f(x,a):
            xind=0
            aind=0
            parameterArray=np.array([])
            for i in range(0,len(varyArray)):
                if varyArray[i]==0:
                    parameterArray=np.append(parameterArray, a[aind])
                    aind=aind+1
                else:
                    parameterArray=np.append(parameterArray, x[xind])
                    xind=xind+1
            return temp.runRayTrace(parameterArray)

        x0=np.array([])
        a=np.array([])
        for i in range(0, len(totalPositions)):
            if varyArray[i]==0:
                a=np.append(a, totalPositions[i])
            else:
                x0=np.append(x0, totalPositions[i])

        print(x0)
        print(a)
        print(f(x0, a))
        res=minimize(f, x0, args=(a,), method='Nelder-Mead')
        print(res.x)

        j=0
        for i in range(0,len(totalPositions)):
            if varyArray[i]==1:
                totalPositions[i]=res.x[j]
                j=j+1

        oldPositions=np.concatenate((self.lensPositions, self.achromatPositions, self.zemaxPositions))
        oldPositions=oldPositions.astype(float)
        oldPositions.sort()

        print(oldPositions)
        print(self.zemaxPositions)

        for i in range(0, len(totalPositions)):
            if totalPositions[i] != oldPositions[i]:  #i.e. the position of component i has changed
                if len(np.where(self.lensPositions.astype(float)==oldPositions[i])[0])==1:  #component is a lens
                    index=np.where(self.lensPositions.astype(float)==oldPositions[i])[0][0]
                    self.lensPositions[index]=totalPositions[i]

                    self.lensWindow = LensDialog(self)
                    self.lensWindow.nameBox.setText(self.lensNames[index])
                    self.lensWindow.positionBox.setText(str(self.lensPositions[index]))
                    self.lensWindow.radiusBox.setText(self.lensRadii[index])
                    self.lensWindow.refrindBox.setText(self.lensRefrinds[index])
                    self.lensWindow.radius1Box.setText(self.lensRadius1s[index])
                    self.lensWindow.scale1Box.setText(self.lensScale1s[index])
                    self.lensWindow.offset1Box.setText(self.lensOffset1s[index])
                    self.lensWindow.kBox1.setText(self.lensk1s[index])
                    self.lensWindow.a4Box1.setText(self.lensa41s[index])
                    self.lensWindow.a6Box1.setText(self.lensa61s[index])
                    self.lensWindow.a8Box1.setText(self.lensa81s[index])
                    self.lensWindow.a10Box1.setText(self.lensa101s[index])
                    self.lensWindow.a12Box1.setText(self.lensa121s[index])
                    self.lensWindow.radius2Box.setText(self.lensRadius2s[index])
                    self.lensWindow.scale2Box.setText(self.lensScale2s[index])
                    self.lensWindow.offset2Box.setText(self.lensOffset2s[index])
                    self.lensWindow.kBox2.setText(self.lensk2s[index])
                    self.lensWindow.a4Box2.setText(self.lensa42s[index])
                    self.lensWindow.a6Box2.setText(self.lensa62s[index])
                    self.lensWindow.a8Box2.setText(self.lensa82s[index])
                    self.lensWindow.a10Box2.setText(self.lensa102s[index])
                    self.lensWindow.a12Box2.setText(self.lensa122s[index])
                    self.lensWindow.thickness1Box.setText(self.lensThickness1s[index])
                    self.lensWindow.thickness2Box.setText(self.lensThickness2s[index])
                    self.lensWindow.surface1Combo.setCurrentIndex(int(self.lensSurface1Types[index]))
                    self.lensWindow.showFrame1(int(self.lensSurface1Types[index]))
                    self.lensWindow.surface2Combo.setCurrentIndex(int(self.lensSurface2Types[index]))
                    self.lensWindow.showFrame2(int(self.lensSurface2Types[index]))
                    self.lensWindow.saveloadBox.setText(self.lensPaths[index])

                    self.lensWindow.writeSave()

                elif len(np.where(self.achromatPositions.astype(float)==oldPositions[i])[0])==1:  #component is an achromat
                    index=np.where(self.achromatPositions.astype(float)==oldPositions[i])[0][0]

                    self.achromatPositions[index]=totalPositions[i]
                    self.achromatWindow = AchromatDialog(self)
                    self.achromatWindow.nameBox.setText(self.achromatNames[index])
                    self.achromatWindow.positionBox.setText(self.achromatPositions[index])
                    self.achromatWindow.radiusBox.setText(self.achromatRadii[index])
                    self.achromatWindow.refrind1Box.setText(self.achromatRefrind1s[index])
                    self.achromatWindow.refrind2Box.setText(self.achromatRefrind2s[index])
                    self.achromatWindow.radius1Box.setText(self.achromatRadius1s[index])
                    self.achromatWindow.scale1Box.setText(self.achromatScale1s[index])
                    self.achromatWindow.offset1Box.setText(self.achromatOffset1s[index])
                    self.achromatWindow.kBox1.setText(self.achromatk1s[index])
                    self.achromatWindow.a4Box1.setText(self.achromata41s[index])
                    self.achromatWindow.a6Box1.setText(self.achromata61s[index])
                    self.achromatWindow.a8Box1.setText(self.achromata81s[index])
                    self.achromatWindow.a10Box1.setText(self.achromata101s[index])
                    self.achromatWindow.a12Box1.setText(self.achromata121s[index])
                    self.achromatWindow.radius2Box.setText(self.achromatRadius2s[index])
                    self.achromatWindow.scale2Box.setText(self.achromatScale2s[index])
                    self.achromatWindow.offset2Box.setText(self.achromatOffset2s[index])
                    self.achromatWindow.kBox2.setText(self.achromatk2s[index])
                    self.achromatWindow.a4Box2.setText(self.achromata42s[index])
                    self.achromatWindow.a6Box2.setText(self.achromata62s[index])
                    self.achromatWindow.a8Box2.setText(self.achromata82s[index])
                    self.achromatWindow.a10Box2.setText(self.achromata102s[index])
                    self.achromatWindow.a12Box2.setText(self.achromata122s[index])
                    self.achromatWindow.radius3Box.setText(self.achromatRadius3s[index])
                    self.achromatWindow.scale3Box.setText(self.achromatScale3s[index])
                    self.achromatWindow.offset3Box.setText(self.achromatOffset3s[index])
                    self.achromatWindow.kBox3.setText(self.achromatk3s[index])
                    self.achromatWindow.a4Box3.setText(self.achromata43s[index])
                    self.achromatWindow.a6Box3.setText(self.achromata63s[index])
                    self.achromatWindow.a8Box3.setText(self.achromata83s[index])
                    self.achromatWindow.a10Box3.setText(self.achromata103s[index])
                    self.achromatWindow.a12Box3.setText(self.achromata123s[index])
                    self.achromatWindow.thickness1Box.setText(self.achromatThickness1s[index])
                    self.achromatWindow.thickness2Box.setText(self.achromatThickness2s[index])
                    self.achromatWindow.thickness3Box.setText(self.achromatThickness3s[index])
                    self.achromatWindow.surface1Combo.setCurrentIndex(int(self.achromatSurface1Types[index]))
                    self.achromatWindow.showFrame1(int(self.achromatSurface1Types[index]))
                    self.achromatWindow.surface2Combo.setCurrentIndex(int(self.achromatSurface2Types[index]))
                    self.achromatWindow.showFrame2(int(self.achromatSurface2Types[index]))
                    self.achromatWindow.surface3Combo.setCurrentIndex(int(self.achromatSurface3Types[index]))
                    self.achromatWindow.showFrame3(int(self.achromatSurface3Types[index]))
                    self.achromatWindow.saveloadBox.setText(self.achromatPaths[index])

                    self.achromatWindow.writeSave()

                elif len(np.where(self.zemaxPositions.astype(float)==oldPositions[i])[0])==1:  #component is an zemax
                    index=np.where(self.zemaxPositions.astype(float)==oldPositions[i])[0][0]

                    self.zemaxs[index]=zm.zemaxlens(totalPositions[i], self.zemaxFileNames[index], self.zemaxWays[index])
                    self.zemaxPositions[index]=totalPositions[i]
                    self.zemaxWindow = ZemaxDialog(self)
                    self.zemaxWindow.nameBox.setText(self.zemaxNames[index])
                    self.zemaxWindow.positionBox.setText(str(self.zemaxPositions[index]))
                    self.zemaxWindow.zemaxFileBox.setText(self.zemaxFileNames[index])
                    self.zemaxWindow.fileBox.setText(self.zemaxPaths[index])
                    self.zemaxWindow.way=self.zemaxWays[index]
                    self.zemaxWindow.writeSave()
                else:
                    print("something has gone wrong")

        self.plotComponents()


    def handleSettingsButton(self):
        self.settingsWindow=OptimiseDialog(self)
        self.settingsWindow.regionBox.setText(str(self.region))
        totalPositions=np.concatenate((self.lensPositions, self.achromatPositions, self.zemaxPositions))
        totalPositions=totalPositions.astype(float)
        allNames=np.concatenate((self.lensNames, self.achromatNames, self.zemaxNames))
        allFrees=np.concatenate((self.lensFrees, self.achromatFrees, self.zemaxFrees))
        a=np.vstack((totalPositions,allNames, allFrees)).T
        a=np.array(sorted(a, key=lambda x:x[0])).T
        totalPositions=a[0]
        allNames=a[1]
        allFrees=a[2]

        for i in range(0, len(allNames)):
            checkBox=QtWidgets.QCheckBox(self.settingsWindow.verticalLayoutWidget)
            checkBox.setObjectName('checkBox'+str(i))
            checkBox.setText(allNames[i])
            self.settingsWindow.verticalLayout.addWidget(checkBox)
            if allFrees[i]==True:
                checkBox.setChecked(True)

        if self.focus==True:
            self.settingsWindow.focusButton.setChecked(True)
            self.settingsWindow.collimateButton.setChecked(False)
        else:
            self.settingsWindow.focusButton.setChecked(False)
            self.settingsWindow.collimateButton.setChecked(True)

        if self.settingsWindow.exec_()==QtWidgets.QDialog.Accepted:
#            checkBoxes = self.settingsWindow.scrollAreaWidgetContents.children()
            for i in range(0, len(allNames)):
                checkBox = self.settingsWindow.findChild(QtWidgets.QCheckBox, 'checkBox'+str(i))

                if checkBox.checkState()==2:
                    free=True
                else:
                    free=False

                print(checkBox.text(), free)

                if len(np.where(self.lensNames==allNames[i])[0])==1:  #component is a lens
                    self.lensFrees[np.where(self.lensNames==allNames[i])[0][0]]=free
                elif len(np.where(self.achromatNames==allNames[i])[0])==1:  #component is an achromat
                    self.achromatFrees[np.where(self.achromatNames==allNames[i])[0][0]]=free
                elif len(np.where(self.zemaxNames==allNames[i])[0])==1:  #component is a zemax
                    self.zemaxFrees[np.where(self.zemaxNames==allNames[i])[0][0]]=free
                else:
                    print("something has gone wrong")

                self.region=int(self.settingsWindow.regionBox.text())

            print(self.lensFrees)
            print(self.zemaxFrees)

            if self.settingsWindow.focusButton.isChecked()==True:
                self.focus=True
            else:
                self.focus=False


    def plotSources(self):
        for i in range(0, len(self.sourceNames)):
            name=self.sourceNames[i]
            posy=self.sourcePosys[i]
            posz=self.sourcePoszs[i]
            nRays=self.sourceNRays[i]
            numAper=self.sourceNumApers[i]

            sourcesPlot=pg.ScatterPlotItem()
            sourcesPlot.setData(pos=[[float(posz),float(posy)]], size=7, symbol='o', pen='r', brush= 'r')
            self.plotFigure.addItem(sourcesPlot)
            nameLabel=pg.TextItem(name, color=(255,0,0),anchor=(1,0.5))
            nameLabel.setPos(float(posz)-5,float(posy))
            self.plotFigure.addItem(nameLabel)

    def plotlenses(self):
        for i in range(0, len(self.lensNames)):

            name=self.lensNames[i]
            position=self.lensPositions[i]
            radius=self.lensRadii[i]
            refrind=self.lensRefrinds[i]
            radius1=self.lensRadius1s[i]
            scale1=self.lensScale1s[i]
            offset1=self.lensOffset1s[i]
            k1=self.lensk1s[i]
            a41=self.lensa41s[i]
            a61=self.lensa61s[i]
            a81=self.lensa81s[i]
            a101=self.lensa101s[i]
            a121=self.lensa121s[i]
            radius2=self.lensRadius2s[i]
            scale2=self.lensScale2s[i]
            offset2=self.lensOffset2s[i]
            k2=self.lensk2s[i]
            a42=self.lensa42s[i]
            a62=self.lensa62s[i]
            a82=self.lensa82s[i]
            a102=self.lensa102s[i]
            a122=self.lensa122s[i]
            thickness1=self.lensThickness1s[i]
            thickness2=self.lensThickness2s[i]
            surface1type=self.lensSurface1Types[i]
            surface2type=self.lensSurface2Types[i]
            print(thickness1)
            Z=float(str(position))
            if int(surface1type)==0:  #surface 1 is an asphere
                f1=lambda y: float(str(scale1))*lrt.asphere(y,float(str(radius1)),float(str(k1)),np.array([0,0,0,0,float(str(a41)),0,float(str(a61)),0,float(str(a81)),0,float(str(a101)),0,float(str(a121))]))+float(str(offset1))
            elif int(surface1type)==1: #surface 1 is flat
                f1=lambda y: 0.0*y + float(str(thickness1))
            if int(surface2type)==0:  #surface 2 is an asphere
                f2=lambda y: float(str(scale2))*lrt.asphere(y,float(str(radius2)),float(str(k2)),np.array([0,0,0,0,float(str(a42)),0,float(str(a62)),0,float(str(a82)),0,float(str(a102)),0,float(str(a122))]))+float(str(offset2))
            elif int(surface2type)==1: #surface 2 is flat
                f2=lambda y: 0.0*y + float(str(thickness2))
            R=float(str(radius))
            #print("The positions of lens ", i, " at 23 mm are ", f1(23), f2(23))
            C=0.0
            my,mz1,mz2=lrt.plotlens(Z, f1,f2,R,C)
            self.plotFigure.plot(mz1, my, pen='k')
            self.plotFigure.plot(mz2, my, pen='k')
            nameLabel=pg.TextItem(name, color=(0,60,158),anchor=(0.5,0))
            nameLabel.setPos(float(position), -1.2*float(radius))
            self.plotFigure.addItem(nameLabel)

    def plotAchromats(self):
        for i in range(0, len(self.achromatNames)):
            name=self.achromatNames[i]
            position=self.achromatPositions[i]
            radius=self.achromatRadii[i]
            refrind1=self.achromatRefrind1s[i]
            refrind2=self.achromatRefrind2s[i]
            radius1=self.achromatRadius1s[i]
            scale1=self.achromatScale1s[i]
            offset1=self.achromatOffset1s[i]
            k1=self.achromatk1s[i]
            a41=self.achromata41s[i]
            a61=self.achromata61s[i]
            a81=self.achromata81s[i]
            a101=self.achromata101s[i]
            a121=self.achromata121s[i]
            radius2=self.achromatRadius2s[i]
            scale2=self.achromatScale2s[i]
            offset2=self.achromatOffset2s[i]
            k2=self.achromatk2s[i]
            a42=self.achromata42s[i]
            a62=self.achromata62s[i]
            a82=self.achromata82s[i]
            a102=self.achromata102s[i]
            a122=self.achromata122s[i]
            radius3=self.achromatRadius3s[i]
            scale3=self.achromatScale3s[i]
            offset3=self.achromatOffset3s[i]
            k3=self.achromatk3s[i]
            a43=self.achromata43s[i]
            a63=self.achromata63s[i]
            a83=self.achromata83s[i]
            a103=self.achromata103s[i]
            a123=self.achromata123s[i]
            thickness1=self.achromatThickness1s[i]
            thickness2=self.achromatThickness2s[i]
            thickness3=self.achromatThickness3s[i]
            surface1type=self.achromatSurface1Types[i]
            surface2type=self.achromatSurface2Types[i]
            surface3type=self.achromatSurface3Types[i]
            if int(surface1type)==0:  #surface 1 is an asphere
                f1=lambda y: float(str(scale1))*lrt.asphere(y,float(str(radius1)),float(str(k1)),np.array([0,0,0,0,float(str(a41)),0,float(str(a61)),0,float(str(a81)),0,float(str(a101)),0,float(str(a121))]))+float(str(offset1))
            elif int(surface1type)==1: #surface 1 is flat
                f1=lambda y: 0.0*y + float(str(thickness1))
            if int(surface2type)==0:  #surface 2 is an asphere
                f2=lambda y: float(str(scale2))*lrt.asphere(y,float(str(radius2)),float(str(k2)),np.array([0,0,0,0,float(str(a42)),0,float(str(a62)),0,float(str(a82)),0,float(str(a102)),0,float(str(a122))]))+float(str(offset2))
            elif int(surface2type)==1: #surface 2 is flat
                f2=lambda y: 0.0*y + float(str(thickness2))
            if int(surface3type)==0:  #surface 3 is an asphere
                f3=lambda y: float(str(scale3))*lrt.asphere(y,float(str(radius3)),float(str(k3)),np.array([0,0,0,0,float(str(a43)),0,float(str(a63)),0,float(str(a83)),0,float(str(a103)),0,float(str(a123))]))+float(str(offset3))
            elif int(surface2type)==1: #surface 3 is flat
                f3=lambda y: 0.0*y + float(str(thickness3))
            Z=float(position)
            R=float(radius)
            my,mz1, mz2, mz3=lrt.plotachromat(Z,f1,f2,f3,R)
            self.plotFigure.plot(mz1, my, pen='k')
            self.plotFigure.plot(mz2, my, pen='k')
            self.plotFigure.plot(mz3, my, pen='k')
            nameLabel=pg.TextItem(name, color=(0,60,158),anchor=(0.5,0))
            nameLabel.setPos(float(position), -1.2*float(radius))
            self.plotFigure.addItem(nameLabel)


    def plotZemaxs(self):
        for i in range(0, len(self.zemaxs)):
            name=self.zemaxNames[i]
            position=self.zemaxs[i].Z
            for j in range(0, len(self.zemaxs[i].surfaces)):
                radius=self.zemaxs[i].surfaces[j].radius
                y=np.arange(-radius, radius*1.01, radius*0.01)
                z=self.zemaxs[i].surfaces[j].z(y)

                self.plotFigure.plot(z,y,pen='k')

            nameLabel=pg.TextItem(str(name), color=(0,60,158),anchor=(0.5,0))
            nameLabel.setPos(float(position), -1.2*float(radius))
            self.plotFigure.addItem(nameLabel)



    def plotComponents(self):
        self.plotlenses()
        self.plotAchromats()
        self.plotSources()
        self.plotZemaxs()

    def handleFileSaveAs(self):
        savefname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File','','*.prj')
        print(savefname)
        sname=savefname.split('/')[-1]
        print(sname)
        self.projectName=sname[:-4]
        print(self.projectName)
        self.handleSaveButton()

    def handleSaveButton(self):
        projectfn=self.projectName+'.prj'
        projectFile=open(projectfn, 'w')

        projectFile.write('#### project file storing associated optical components ####\n')

        for i in range(0, len(self.sourcePaths)):
            projectFile.write('source       ' + str(self.sourcePaths[i]) + '\n')

        for i in range(0, len(self.lensPaths)):
            projectFile.write('lens         ' + str(self.lensPaths[i]) + '\n')

        for i in range(0, len(self.achromatPaths)):
            projectFile.write('achromat     ' + str(self.achromatPaths[i]) + '\n')

        for i in range(0, len(self.zemaxPaths)):
            projectFile.write('zemax lens   ' + str(self.zemaxPaths[i]) + '\n')

        projectFile.write('end point    ' + str(self.endDistanceBox.text()) + '\n')

        projectFile.write('region       ' + str(self.region) + '\n')

        projectFile.write('focus        ' + str(self.focus) + '\n')

        projectFile.close()


    def loadSource(self, fileName):
        sourceFile=open(fileName, 'r')

        lines=sourceFile.readlines()
        a=0
        b=0
        c=0
        d=0
        e=0
        f=0
        for line in lines:
            if line[0:20]=='name                ':
                self.sourceNames=np.append(self.sourceNames, line[20:-1])
                a=a+1
            elif line[0:20]=='y position          ':
                self.sourcePosys=np.append(self.sourcePosys, line[20:-1])
                b=b+1
            elif line[0:20]=='z position          ':
                self.sourcePoszs=np.append(self.sourcePoszs, line[20:-1])
                c=c+1
            elif line[0:20]=='number of rays      ':
                self.sourceNRays=np.append(self.sourceNRays, line[20:-1])
                d=d+1
            elif line[0:20]=='numerical aperture  ':
                self.sourceNumApers=np.append(self.sourceNumApers, line[20:-1])
                e=e+1
            elif line[0:20]=='wavelength          ':
                self.sourceWavelengths=np.append(self.sourceWavelengths, line[20:-1])
                f=f+1

        if a != 1 or b != 1 or c != 1 or d != 1 or e != 1 or f != 1:
            print("invalid source file")
        else:
            self.sourcePaths=np.append(self.sourcePaths, fileName)
            self.sourceCombo.addItem(self.sourceNames[-1])


    def loadLens(self, fileName):
        lensFile=open(fileName, 'r')

        lines=lensFile.readlines()
        a=0
        b=0
        c=0
        d=0
        e1=0
        f1=0
        g1=0
        h1=0
        i1=0
        j1=0
        k1=0
        l1=0
        m1=0
        n1=0
        o1=0
        e2=0
        f2=0
        g2=0
        h2=0
        i2=0
        j2=0
        k2=0
        l2=0
        m2=0
        n2=0
        o2=0
        p=0
        for line in lines:
            if line[0:12]=='name        ':
                self.lensNames=np.append(self.lensNames, line[12:-1])
                a=a+1
            elif line[0:12]=='position    ':
                self.lensPositions=np.append(self.lensPositions, line[12:-1])
                b=b+1
            elif line[0:12]=='radius      ':
                self.lensRadii=np.append(self.lensRadii, line[12:-1])
                c=c+1
            elif line[0:12]=='refrind     ':
                self.lensRefrinds=np.append(self.lensRefrinds, line[12:-1])
                d=d+1
            elif line[0:12]=='radius1     ':
                self.lensRadius1s=np.append(self.lensRadius1s, line[12:-1])
                e1=e1+1
            elif line[0:12]=='scale1      ':
                self.lensScale1s=np.append(self.lensScale1s, line[12:-1])
                f1=f1+1
            elif line[0:12]=='offset1     ':
                self.lensOffset1s=np.append(self.lensOffset1s, line[12:-1])
                g1=g1+1
            elif line[0:12]=='k1          ':
                self.lensk1s=np.append(self.lensk1s, line[12:-1])
                j1=j1+1
            elif line[0:12]=='a41         ':
                self.lensa41s=np.append(self.lensa41s, line[12:-1])
                k1=k1+1
            elif line[0:12]=='a61         ':
                self.lensa61s=np.append(self.lensa61s, line[12:-1])
                l1=l1+1
            elif line[0:12]=='a81         ':
                self.lensa81s=np.append(self.lensa81s, line[12:-1])
                m1=m1+1
            elif line[0:12]=='a101        ':
                self.lensa101s=np.append(self.lensa101s, line[12:-1])
                n1=n1+1
            elif line[0:12]=='a121        ':
                self.lensa121s=np.append(self.lensa121s, line[12:-1])
                o1=o1+1
            elif line[0:12]=='radius2     ':
                self.lensRadius2s=np.append(self.lensRadius2s, line[12:-1])
                e2=e2+1
            elif line[0:12]=='scale2      ':
                self.lensScale2s=np.append(self.lensScale2s, line[12:-1])
                f2=f2+1
            elif line[0:12]=='offset2     ':
                self.lensOffset2s=np.append(self.lensOffset2s, line[12:-1])
                g2=g2+1
            elif line[0:12]=='k2          ':
                self.lensk2s=np.append(self.lensk2s, line[12:-1])
                j2=j2+1
            elif line[0:12]=='a42         ':
                self.lensa42s=np.append(self.lensa42s, line[12:-1])
                k2=k2+1
            elif line[0:12]=='a62         ':
                self.lensa62s=np.append(self.lensa62s, line[12:-1])
                l2=l2+1
            elif line[0:12]=='a82         ':
                self.lensa82s=np.append(self.lensa82s, line[12:-1])
                m2=m2+1
            elif line[0:12]=='a102        ':
                self.lensa102s=np.append(self.lensa102s, line[12:-1])
                n2=n2+1
            elif line[0:12]=='a122        ':
                self.lensa122s=np.append(self.lensa122s, line[12:-1])
                o2=o2+1
            elif line[0:12]=='thickness1  ':
                self.lensThickness1s=np.append(self.lensThickness1s, line[12:-1])
                h1=h1+1
            elif line[0:12]=='thickness2  ':
                self.lensThickness2s=np.append(self.lensThickness2s, line[12:-1])
                h2=h2+1
            elif line[0:12]=='surface1    ' and line[12:-1]=='Asphere':
                self.lensSurface1Types=np.append(self.lensSurface1Types, 0)
                i1=i1+1
            elif line[0:12]=='surface1    ' and line[12:-1]=='Flat':
                self.lensSurface1Types=np.append(self.lensSurface1Types, 1)
                i1=i1+1
            elif line[0:12]=='surface2    ' and line[12:-1]=='Asphere':
                self.lensSurface2Types=np.append(self.lensSurface2Types, 0)
                i2=i2+1
            elif line[0:12]=='surface2    ' and line[12:-1]=='Flat':
                self.lensSurface2Types=np.append(self.lensSurface2Types, 1)
                i2=i2+1
            elif line[0:12]=='free        ':
                if line[12:-1]=='True':
                    self.lensFrees=np.append(self.lensFrees, True)
                    p=p+1
                elif line[12:-1]=='False':
                    self.lensFrees=np.append(self.lensFrees, False)
                    p=p+1


        if a != 1 or b != 1 or c != 1 or d != 1 or e1 != 1 or \
           e2 != 1 or f1 != 1 or f2 != 1 or g1 != 1 or g2 != 1 or \
                 h1 != 1 or h2 != 1 or i1 != 1 or i2 != 1 or j1 != 1 or \
                       j2 != 1 or k1 != 1 or k2 != 1 or l1 != 1 or l2 != 1 or \
                             m1 != 1 or m2 != 1 or n1 != 1 or n2 != 1 or o1 != 1 or o2 != 1 or\
                                   p != 1:
            print("invalid lens file")
        else:
            self.lensPaths=np.append(self.lensPaths, fileName)
            self.lensCombo.addItem(self.lensNames[-1])

    def loadAchromat(self, fileName):
        achromatFile=open(fileName, 'r')

        lines=achromatFile.readlines()
        a=0
        b=0
        c=0
        d1=0
        d2=0
        e1=0
        f1=0
        g1=0
        h1=0
        i1=0
        j1=0
        k1=0
        l1=0
        m1=0
        n1=0
        o1=0
        e2=0
        f2=0
        g2=0
        h2=0
        i2=0
        j2=0
        k2=0
        l2=0
        m2=0
        n2=0
        o2=0
        e3=0
        f3=0
        g3=0
        h3=0
        i3=0
        j3=0
        k3=0
        l3=0
        m3=0
        n3=0
        o3=0
        p=0
        for line in lines:
            if line[0:12]=='name        ':
                self.achromatNames=np.append(self.achromatNames, line[12:-1])
                a=a+1
            elif line[0:12]=='position    ':
                self.achromatPositions=np.append(self.achromatPositions, line[12:-1])
                b=b+1
            elif line[0:12]=='radius      ':
                self.achromatRadii=np.append(self.achromatRadii, line[12:-1])
                c=c+1
            elif line[0:12]=='refrind1    ':
                self.achromatRefrind1s=np.append(self.achromatRefrind1s, line[12:-1])
                d1=d1+1
            elif line[0:12]=='refrind2    ':
                self.achromatRefrind2s=np.append(self.achromatRefrind2s, line[12:-1])
                d2=d2+1
            elif line[0:12]=='radius1     ':
                self.achromatRadius1s=np.append(self.achromatRadius1s, line[12:-1])
                e1=e1+1
            elif line[0:12]=='scale1      ':
                self.achromatScale1s=np.append(self.achromatScale1s, line[12:-1])
                f1=f1+1
            elif line[0:12]=='offset1     ':
                self.achromatOffset1s=np.append(self.achromatOffset1s, line[12:-1])
                g1=g1+1
            elif line[0:12]=='k1          ':
                self.achromatk1s=np.append(self.achromatk1s, line[12:-1])
                j1=j1+1
            elif line[0:12]=='a41         ':
                self.achromata41s=np.append(self.achromata41s, line[12:-1])
                k1=k1+1
            elif line[0:12]=='a61         ':
                self.achromata61s=np.append(self.achromata61s, line[12:-1])
                l1=l1+1
            elif line[0:12]=='a81         ':
                self.achromata81s=np.append(self.achromata81s, line[12:-1])
                m1=m1+1
            elif line[0:12]=='a101        ':
                self.achromata101s=np.append(self.achromata101s, line[12:-1])
                n1=n1+1
            elif line[0:12]=='a121        ':
                self.achromata121s=np.append(self.achromata121s, line[12:-1])
                o1=o1+1
            elif line[0:12]=='radius2     ':
                self.achromatRadius2s=np.append(self.achromatRadius2s, line[12:-1])
                e2=e2+1
            elif line[0:12]=='scale2      ':
                self.achromatScale2s=np.append(self.achromatScale2s, line[12:-1])
                f2=f2+1
            elif line[0:12]=='offset2     ':
                self.achromatOffset2s=np.append(self.achromatOffset2s, line[12:-1])
                g2=g2+1
            elif line[0:12]=='k2          ':
                self.achromatk2s=np.append(self.achromatk2s, line[12:-1])
                j2=j2+1
            elif line[0:12]=='a42         ':
                self.achromata42s=np.append(self.achromata42s, line[12:-1])
                k2=k2+1
            elif line[0:12]=='a62         ':
                self.achromata62s=np.append(self.achromata62s, line[12:-1])
                l2=l2+1
            elif line[0:12]=='a82         ':
                self.achromata82s=np.append(self.achromata82s, line[12:-1])
                m2=m2+1
            elif line[0:12]=='a102        ':
                self.achromata102s=np.append(self.achromata102s, line[12:-1])
                n2=n2+1
            elif line[0:12]=='a122        ':
                self.achromata122s=np.append(self.achromata122s, line[12:-1])
                o2=o2+1
            elif line[0:12]=='radius3     ':
                self.achromatRadius3s=np.append(self.achromatRadius3s, line[12:-1])
                e3=e3+1
            elif line[0:12]=='scale3      ':
                self.achromatScale3s=np.append(self.achromatScale3s, line[12:-1])
                f3=f3+1
            elif line[0:12]=='offset3     ':
                self.achromatOffset3s=np.append(self.achromatOffset3s, line[12:-1])
                g3=g3+1
            elif line[0:12]=='k3          ':
                self.achromatk3s=np.append(self.achromatk3s, line[12:-1])
                j3=j3+1
            elif line[0:12]=='a43         ':
                self.achromata43s=np.append(self.achromata43s, line[12:-1])
                k3=k3+1
            elif line[0:12]=='a63         ':
                self.achromata63s=np.append(self.achromata63s, line[12:-1])
                l3=l3+1
            elif line[0:12]=='a83         ':
                self.achromata83s=np.append(self.achromata83s, line[12:-1])
                m3=m3+1
            elif line[0:12]=='a103        ':
                self.achromata103s=np.append(self.achromata103s, line[12:-1])
                n3=n3+1
            elif line[0:12]=='a123        ':
                self.achromata123s=np.append(self.achromata123s, line[12:-1])
                o3=o3+1
            elif line[0:12]=='thickness1  ':
                self.achromatThickness1s=np.append(self.achromatThickness1s, line[12:-1])
                h1=h1+1
            elif line[0:12]=='thickness2  ':
                self.achromatThickness2s=np.append(self.achromatThickness2s, line[12:-1])
                h2=h2+1
            elif line[0:12]=='thickness3  ':
                self.achromatThickness3s=np.append(self.achromatThickness3s, line[12:-1])
                h3=h3+1
            elif line[0:12]=='surface1    ' and line[12:-1]=='Asphere':
                self.achromatSurface1Types=np.append(self.achromatSurface1Types, 0)
                i1=i1+1
            elif line[0:12]=='surface1    ' and line[12:-1]=='Flat':
                self.achromatSurface1Types=np.append(self.achromatSurface1Types, 1)
                i1=i1+1
            elif line[0:12]=='surface2    ' and line[12:-1]=='Asphere':
                self.achromatSurface2Types=np.append(self.achromatSurface2Types, 0)
                i2=i2+1
            elif line[0:12]=='surface2    ' and line[12:-1]=='Flat':
                self.achromatSurface2Types=np.append(self.achromatSurface2Types, 1)
                i2=i2+1
            elif line[0:12]=='surface3    ' and line[12:-1]=='Asphere':
                self.achromatSurface3Types=np.append(self.achromatSurface3Types, 0)
                i3=i3+1
            elif line[0:12]=='surface3    ' and line[12:-1]=='Flat':
                self.achromatSurface3Types=np.append(self.achromatSurface3Types, 1)
                i3=i3+1
            elif line[0:12]=='free        ':
                if line[12:-1]=='True':
                    self.achromatFrees=np.append(self.achromatFrees, True)
                    p=p+1
                elif line[12:-1]=='False':
                    self.achromatFrees=np.append(self.achromatFrees, False)
                    p=p+1



        if a != 1 or b != 1 or c != 1 or d1 != 1 or d2 != 1 or e1 != 1 or \
           e2 != 1 or e3 != 1 or f1 != 1 or f2 != 1 or f3 != 1 \
                 or g1 != 1 or g2 != 1 or g3 != 1 or h1 != 1 or \
                          h2 != 1 or h3 != 1 or i1 != 1 or i2 != 1 \
                                or i3 != 1 or j1 != 1 or j2 != 1 or j3 != 1 \
                                         or k1 != 1 or k2 != 1 or k3 != 1 or l1 != 1 \
                                                  or l2 != 1 or l3 != 1 or m1 != 1 \
                                                           or m2 != 1 or m3 != 1 \
                                                                    or n1 != 1 or n2 != 1 or n3 != 1 \
                                                                             or o1 != 1 or o2 != 1 or o3 != 1 or \
                                                                                      p != 1:
            print("invalid achromat file")
            print(a, b, c, d1, d2, e1, f1, g1, e2, f2, g2, e3, f3, g3, h1, h2, h3, i1, i2, i3)
        else:
            self.achromatPaths=np.append(self.achromatPaths, fileName)
            self.achromatCombo.addItem(self.achromatNames[-1])

    def loadZemax(self, fileName):
        zemaxFile=open(fileName, 'r')

        lines=zemaxFile.readlines()

        a=b=c=d=e=0
        for line in lines:
            if line[0:12]=='name        ':
                self.zemaxNames=np.append(self.zemaxNames, line[12:-1])
                a=a+1
            elif line[0:12]=='position    ':
                position=float(line[12:-1])
                self.zemaxPositions=np.append(self.zemaxPositions, position)
                b=b+1
            elif line[0:12]=='zemax file  ':
                zmxFile=line[12:-1]
                self.zemaxFileNames=np.append(self.zemaxFileNames, zmxFile)
                c=c+1
            elif line[0:12]=='way         ':
                if line[12:-1]=='True':
                    way=True
                    d=d+1
                elif line[12:-1]=='False':
                    way=False
                    d=d+1
                else:
                    a=2
            elif line[0:12]=='free        ':
                if line[12:-1]=='True':
                    self.zemaxFrees=np.append(self.zemaxFrees, True)
                    e=e+1
                elif line[12:-1]=='False':
                    self.zemaxFrees=np.append(self.zemaxFrees, False)
                    e=e+1




        if a != 1 or b != 1 or c !=1 or d != 1 or e != 1:
            print("invalid zemax file")
        else:
            self.zemaxPaths=np.append(self.zemaxPaths, fileName)
            self.zemaxCombo.addItem(self.zemaxNames[-1])
            self.zemaxs=np.append(self.zemaxs, zm.zemaxlens(position, zmxFile, way))
            self.zemaxWays=np.append(self.zemaxWays, way)


    def handleExitButton(self):
        self.close()



class SourceDialog(QtWidgets.QDialog, Ui_SourceDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.sourceButtonBox.accepted.connect(self.writeSave)
        self.loadButton.clicked.connect(self.fileLoad)
        self.saveButton.clicked.connect(self.fileSave)
        self.cwd=os.getcwd()

    def getValues(self):
        return self.nameBox.text(), self.posyBox.text(), self.poszBox.text(), self.nRaysBox.text(), self.numAperBox.text(), self.wavelengthBox.text(), self.saveloadBox.text()

    def writeSave(self):
        saveFile=open(str(self.saveloadBox.text()), 'w')

        saveFile.write('#### source details saved here ####\n')

        saveFile.write('name' + '                ' + str(self.nameBox.text()) + '\n')
        saveFile.write('y position' + '          ' + str(self.posyBox.text()) + '\n')
        saveFile.write('z position' + '          ' + str(self.poszBox.text()) + '\n')
        saveFile.write('number of rays' + '      ' + str(self.nRaysBox.text()) + '\n')
        saveFile.write('numerical aperture' + '  ' + str(self.numAperBox.text()) + '\n')
        saveFile.write('wavelength' + '          ' + str(self.wavelengthBox.text()) + '\n')
        saveFile.close()

    def fileSave(self):
        self.saveDialog = QtWidgets.QFileDialog(self)
        if self.saveDialog.exec_()==QtWidgets.QFileDialog.Accepted:
            self.fileStringList = self.saveDialog.selectedFiles()
            self.saveloadBox.setText(self.fileStringList[0][len(self.cwd)+1:])


    def fileLoad(self):
        fn,filter=QtWidgets.QFileDialog.getOpenFileName()
        self.saveloadBox.setText(fn[len(self.cwd)+1:])

        openFile=open(str(self.saveloadBox.text()), 'r')

        lines=openFile.readlines()
        for line in lines:
            if line[0:20]=='name                ':
                self.nameBox.setText(line[20:-1])
            elif line[0:20]=='y position          ':
                self.posyBox.setText(line[20:-1])
            elif line[0:20]=='z position          ':
                self.poszBox.setText(line[20:-1])
            elif line[0:20]=='number of rays      ':
                self.nRaysBox.setText(line[20:-1])
            elif line[0:20]=='numerical aperture  ':
                self.numAperBox.setText(line[20:-1])
            elif line[0:20]=='wavelength          ':
                self.wavelengthBox.setText(line[20:-1])


class LensDialog(QtWidgets.QDialog, Ui_LensDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lensButtonBox.accepted.connect(self.writeSave)
        self.loadButton.clicked.connect(self.fileLoad)
        self.saveButton.clicked.connect(self.fileSave)
        self.flipButton.clicked.connect(self.handleFlipButton)

        self.surface1Combo.activated.connect(self.showFrame1)
        self.surface1AsphereFrame.setHidden(False)
        self.surface1FlatFrame.setHidden(True)

        self.surface2Combo.activated.connect(self.showFrame2)
        self.surface2AsphereFrame.setHidden(False)
        self.surface2FlatFrame.setHidden(True)

        self.free=False
        self.cwd=os.getcwd()


    def showFrame1(self, index):
        if index==0:
            self.surface1AsphereFrame.setHidden(False)
            self.surface1FlatFrame.setHidden(True)
        if index==1:
            self.surface1AsphereFrame.setHidden(True)
            self.surface1FlatFrame.setHidden(False)

    def showFrame2(self, index):
        if index==0:
            self.surface2AsphereFrame.setHidden(False)
            self.surface2FlatFrame.setHidden(True)
        if index==1:
            self.surface2AsphereFrame.setHidden(True)
            self.surface2FlatFrame.setHidden(False)


    def getValues(self):
        surface1index=self.surface1Combo.currentIndex()
        surface2index=self.surface2Combo.currentIndex()
        name=self.nameBox.text()
        position=self.positionBox.text()
        radius=self.radiusBox.text()
        refrind=self.refrindBox.text()
        radius1=self.radius1Box.text()
        scale1=self.scale1Box.text()
        offset1=self.offset1Box.text()
        k1=self.kBox1.text()
        a41=self.a4Box1.text()
        a61=self.a6Box1.text()
        a81=self.a8Box1.text()
        a101=self.a10Box1.text()
        a121=self.a12Box1.text()
        radius2=self.radius2Box.text()
        scale2=self.scale2Box.text()
        offset2=self.offset2Box.text()
        k2=self.kBox2.text()
        a42=self.a4Box2.text()
        a62=self.a6Box2.text()
        a82=self.a8Box2.text()
        a102=self.a10Box2.text()
        a122=self.a12Box2.text()
        thickness1=self.thickness1Box.text()
        thickness2=self.thickness2Box.text()
        path=self.saveloadBox.text()
        free=self.free
        return name, position, radius, refrind, radius1, scale1, offset1, \
            k1, a41, a61, a81, a101, a121,\
            radius2, scale2, offset2, \
            k2, a42, a62, a82, a102, a122,\
            thickness1, thickness2, surface1index, surface2index, path, free

    def handleFlipButton(self):
        surface1index=self.surface1Combo.currentIndex()
        surface2index=self.surface2Combo.currentIndex()
        radius1=self.radius2Box.text()
        scale1=str(-float(self.scale2Box.text()))
        k1=self.kBox2.text()
        a41=self.a4Box2.text()
        a61=self.a6Box2.text()
        a81=self.a8Box2.text()
        a101=self.a10Box2.text()
        a121=self.a12Box2.text()
        radius2=self.radius1Box.text()
        scale2=str(-float(self.scale1Box.text()))
        k2=self.kBox1.text()
        a42=self.a4Box1.text()
        a62=self.a6Box1.text()
        a82=self.a8Box1.text()
        a102=self.a10Box1.text()
        a122=self.a12Box1.text()

        if int(surface1index)==1:  #flat
            offset1=self.thickness1Box.text()
            thickness1=self.thickness1Box.text()
        elif int(surface1index)==0: #asphere
            offset1=self.offset1Box.text()
            thickness1=self.offset1Box.text()

        if int(surface2index)==1:  #flat
            offset2=self.thickness2Box.text()
            thickness2=self.thickness2Box.text()
        elif int(surface2index)==0: #asphere
            offset2=self.offset2Box.text()
            thickness2=self.offset2Box.text()



        self.radius1Box.setText(radius1)
        self.scale1Box.setText(scale1)
        self.offset1Box.setText(offset1)
        self.kBox1.setText(k1)
        self.a4Box1.setText(a41)
        self.a6Box1.setText(a61)
        self.a8Box1.setText(a81)
        self.a10Box1.setText(a101)
        self.a12Box1.setText(a121)
        self.radius2Box.setText(radius2)
        self.scale2Box.setText(scale2)
        self.offset2Box.setText(offset2)
        self.kBox2.setText(k2)
        self.a4Box2.setText(a42)
        self.a6Box2.setText(a62)
        self.a8Box2.setText(a82)
        self.a10Box2.setText(a102)
        self.a12Box2.setText(a122)
        self.thickness1Box.setText(thickness1)
        self.thickness2Box.setText(thickness2)

        self.surface1Combo.setCurrentIndex(surface2index)
        self.surface2Combo.setCurrentIndex(surface1index)
        self.showFrame1(surface2index)
        self.showFrame2(surface1index)




    def writeSave(self):
        surface1index=self.surface1Combo.currentIndex()
        surface2index=self.surface2Combo.currentIndex()

        saveFile=open(str(self.saveloadBox.text()), 'w')

        saveFile.write('#### lens details saved here ####\n')

        saveFile.write('name' + '        ' + str(self.nameBox.text()) + '\n')
        saveFile.write('position' + '    ' + str(self.positionBox.text()) + '\n')
        saveFile.write('radius' + '      ' + str(self.radiusBox.text()) + '\n')
        saveFile.write('refrind' + '     ' + str(self.refrindBox.text()) + '\n')

        saveFile.write('#### surface 1 ####' + '\n')
        saveFile.write('surface1' + '    ' + str(self.surface1Combo.currentText() + '\n'))

        saveFile.write('radius1' + '     ' + str(self.radius1Box.text()) + '\n')
        saveFile.write('scale1' + '      ' + str(self.scale1Box.text()) + '\n')
        saveFile.write('offset1' + '     ' + str(self.offset1Box.text()) + '\n')
        saveFile.write('k1' + '          ' + str(self.kBox1.text()) + '\n')
        saveFile.write('a41' + '         ' + str(self.a4Box1.text()) + '\n')
        saveFile.write('a61' + '         ' + str(self.a6Box1.text()) + '\n')
        saveFile.write('a81' + '         ' + str(self.a8Box1.text()) + '\n')
        saveFile.write('a101' + '        ' + str(self.a10Box1.text()) + '\n')
        saveFile.write('a121' + '        ' + str(self.a12Box1.text()) + '\n')

        saveFile.write('thickness1' + '  ' + str(self.thickness1Box.text() + '\n'))

        saveFile.write('#### surface 2 ####' + '\n')
        saveFile.write('surface2' + '    ' + str(self.surface2Combo.currentText() + '\n'))

        saveFile.write('radius2' + '     ' + str(self.radius2Box.text()) + '\n')
        saveFile.write('scale2' + '      ' + str(self.scale2Box.text()) + '\n')
        saveFile.write('offset2' + '     ' + str(self.offset2Box.text()) + '\n')
        saveFile.write('k2' + '          ' + str(self.kBox2.text()) + '\n')
        saveFile.write('a42' + '         ' + str(self.a4Box2.text()) + '\n')
        saveFile.write('a62' + '         ' + str(self.a6Box2.text()) + '\n')
        saveFile.write('a82' + '         ' + str(self.a8Box2.text()) + '\n')
        saveFile.write('a102' + '        ' + str(self.a10Box2.text()) + '\n')
        saveFile.write('a122' + '        ' + str(self.a12Box2.text()) + '\n')

        saveFile.write('thickness2' + '  ' + str(self.thickness2Box.text() + '\n'))

        saveFile.write('free' + '        ' + str(self.free) + '\n')

        saveFile.close()

    def fileSave(self):
        self.saveDialog = QtWidgets.QFileDialog(self)
        if self.saveDialog.exec_()==QtWidgets.QFileDialog.Accepted:
            self.fileStringList = self.saveDialog.selectedFiles()
            self.saveloadBox.setText(self.fileStringList[0][len(self.cwd)+1:])

    def fileLoad(self):
        fn,filter=QtWidgets.QFileDialog.getOpenFileName()
        self.saveloadBox.setText(fn[len(self.cwd)+1:])
        openFile=open(str(self.saveloadBox.text()), 'r')

        lines=openFile.readlines()
        for line in lines:
            if line[0:12]=='name        ':
                self.nameBox.setText(line[12:-1])
            elif line[0:12]=='position    ':
                self.positionBox.setText(line[12:-1])
            elif line[0:12]=='radius      ':
                self.radiusBox.setText(line[12:-1])
            elif line[0:12]=='refrind     ':
                self.refrindBox.setText(line[12:-1])
            elif line[0:12]=='radius1     ':
                self.radius1Box.setText(line[12:-1])
            elif line[0:12]=='scale1      ':
                self.scale1Box.setText(line[12:-1])
            elif line[0:12]=='offset1     ':
                self.offset1Box.setText(line[12:-1])
            elif line[0:12]=='k1          ':
                self.kBox1.setText(line[12:-1])
            elif line[0:12]=='a41         ':
                self.a4Box1.setText(line[12:-1])
            elif line[0:12]=='a61         ':
                self.a6Box1.setText(line[12:-1])
            elif line[0:12]=='a81         ':
                self.a8Box1.setText(line[12:-1])
            elif line[0:12]=='a101         ':
                self.a10Box1.setText(line[12:-1])
            elif line[0:12]=='a121         ':
                self.a12Box1.setText(line[12:-1])
            elif line[0:12]=='radius2     ':
                self.radius2Box.setText(line[12:-1])
            elif line[0:12]=='scale2      ':
                self.scale2Box.setText(line[12:-1])
            elif line[0:12]=='offset2     ':
                self.offset2Box.setText(line[12:-1])
            elif line[0:12]=='k2          ':
                self.kBox2.setText(line[12:-1])
            elif line[0:12]=='a42         ':
                self.a4Box2.setText(line[12:-1])
            elif line[0:12]=='a62         ':
                self.a6Box2.setText(line[12:-1])
            elif line[0:12]=='a82         ':
                self.a8Box2.setText(line[12:-1])
            elif line[0:12]=='a102         ':
                self.a10Box2.setText(line[12:-1])
            elif line[0:12]=='a122         ':
                self.a12Box2.setText(line[12:-1])
            elif line[0:12]=='thickness1  ':
                self.thickness1Box.setText(line[12:-1])
            elif line[0:12]=='thickness2  ':
                self.thickness2Box.setText(line[12:-1])
            elif line[0:12]=='surface1    ' and line[12:-1]=='Asphere':
                self.surface1Combo.setCurrentIndex(0)
                self.showFrame1(0)
            elif line[0:12]=='surface1    ' and line[12:-1]=='Flat':
                self.surface1Combo.setCurrentIndex(1)
                self.showFrame1(1)
            elif line[0:12]=='surface2    ' and line[12:-1]=='Asphere':
                self.surface2Combo.setCurrentIndex(0)
                self.showFrame2(0)
            elif line[0:12]=='surface2    ' and line[12:-1]=='Flat':
                self.surface2Combo.setCurrentIndex(1)
                self.showFrame2(1)
            elif line[0:12]=='free        ':
                if line[12:-1]=='True':
                    self.free=True
                elif line[12:-1]=='False':
                    self.free=False




class AchromatDialog(QtWidgets.QDialog, Ui_AchromatDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.achromatButtonBox.accepted.connect(self.writeSave)
        self.loadButton.clicked.connect(self.fileLoad)
        self.saveButton.clicked.connect(self.fileSave)
        self.flipButton.clicked.connect(self.handleFlipButton)

        self.surface1Combo.activated.connect(self.showFrame1)
        self.surface1AsphereFrame.setHidden(False)
        self.surface1FlatFrame.setHidden(True)

        self.surface2Combo.activated.connect(self.showFrame2)
        self.surface2AsphereFrame.setHidden(False)
        self.surface2FlatFrame.setHidden(True)

        self.surface3Combo.activated.connect(self.showFrame3)
        self.surface3AsphereFrame.setHidden(False)
        self.surface3FlatFrame.setHidden(True)

        self.free=False
        self.cwd=os.getcwd()

    def showFrame1(self, index):
        if index==0:
            self.surface1AsphereFrame.setHidden(False)
            self.surface1FlatFrame.setHidden(True)
        if index==1:
            self.surface1AsphereFrame.setHidden(True)
            self.surface1FlatFrame.setHidden(False)

    def showFrame2(self, index):
        if index==0:
            self.surface2AsphereFrame.setHidden(False)
            self.surface2FlatFrame.setHidden(True)
        if index==1:
            self.surface2AsphereFrame.setHidden(True)
            self.surface2FlatFrame.setHidden(False)

    def showFrame3(self, index):
        if index==0:
            self.surface3AsphereFrame.setHidden(False)
            self.surface3FlatFrame.setHidden(True)
        if index==1:
            self.surface3AsphereFrame.setHidden(True)
            self.surface3FlatFrame.setHidden(False)

    def getValues(self):
        surface1index=self.surface1Combo.currentIndex()
        surface2index=self.surface2Combo.currentIndex()
        surface3index=self.surface3Combo.currentIndex()
        name=self.nameBox.text()
        position=self.positionBox.text()
        radius=self.radiusBox.text()
        refrind1=self.refrind1Box.text()
        refrind2=self.refrind2Box.text()
        radius1=self.radius1Box.text()
        scale1=self.scale1Box.text()
        offset1=self.offset1Box.text()
        k1=self.kBox1.text()
        a41=self.a4Box1.text()
        a61=self.a4Box1.text()
        a81=self.a4Box1.text()
        a101=self.a4Box1.text()
        a121=self.a4Box1.text()
        radius2=self.radius2Box.text()
        scale2=self.scale2Box.text()
        offset2=self.offset2Box.text()
        k2=self.kBox2.text()
        a42=self.a4Box2.text()
        a62=self.a4Box2.text()
        a82=self.a4Box2.text()
        a102=self.a4Box2.text()
        a122=self.a4Box2.text()
        radius3=self.radius3Box.text()
        scale3=self.scale3Box.text()
        offset3=self.offset3Box.text()
        k3=self.kBox3.text()
        a43=self.a4Box3.text()
        a63=self.a4Box3.text()
        a83=self.a4Box3.text()
        a103=self.a4Box3.text()
        a123=self.a4Box3.text()
        thickness1=self.thickness1Box.text()
        thickness2=self.thickness2Box.text()
        thickness3=self.thickness3Box.text()
        path=self.saveloadBox.text()
        free=self.free

        return name, position, radius, refrind1, refrind2, radius1, scale1, offset1,\
            k1, a41, a61, a81, a101, a121, \
            radius2, scale2, offset2, \
            k2, a42, a62, a82, a102, a122, \
            radius3, scale3, offset3,\
            k3, a43, a63, a83, a103, a123, \
            thickness1, thickness2, thickness3, surface1index, surface2index, surface3index, path, free

    def handleFlipButton(self):
        surface1index=self.surface1Combo.currentIndex()
        surface2index=self.surface2Combo.currentIndex()
        surface3index=self.surface3Combo.currentIndex()
        radius1=self.radius3Box.text()
        scale1=str(-float(self.scale3Box.text()))
        k1=self.kBox3.text()
        a41=self.a4Box3.text()
        a61=self.a6Box3.text()
        a81=self.a8Box3.text()
        a101=self.a10Box3.text()
        a121=self.a12Box3.text()
        radius2=self.radius2Box.text()
        scale2=str(-float(self.scale2Box.text()))
        k2=self.kBox2.text()
        a42=self.a4Box2.text()
        a62=self.a6Box2.text()
        a82=self.a8Box2.text()
        a102=self.a10Box2.text()
        a122=self.a12Box2.text()
        radius3=self.radius1Box.text()
        scale3=str(-float(self.scale1Box.text()))
        k3=self.kBox1.text()
        a43=self.a4Box1.text()
        a63=self.a6Box1.text()
        a83=self.a8Box1.text()
        a103=self.a10Box1.text()
        a123=self.a12Box1.text()


        if int(surface1index)==1:  #flat
            offset1=self.thickness1Box.text()
            thickness1=self.thickness1Box.text()
        elif int(surface1index)==0: #asphere
            offset1=self.offset1Box.text()
            thickness1=self.offset1Box.text()

        if int(surface3index)==1:  #flat
            offset3=self.thickness3Box.text()
            thickness3=self.thickness3Box.text()
        elif int(surface3index)==0: #asphere
            offset3=self.offset3Box.text()
            thickness3=self.offset3Box.text()

        if int(surface2index)==1:  #flat
            offset2=str(float(offset1)+float(offset3)-float(self.thickness2Box.text()))
            thickness2=str(float(offset1)+float(offset3)-float(self.thickness2Box.text()))
        elif int(surface2index)==0: #asphere
            offset2=str(float(offset1)+float(offset3)-float(self.offset2Box.text()))
            thickness2=str(float(offset1)+float(offset3)-float(self.offset2Box.text()))



        self.radius1Box.setText(radius1)
        self.scale1Box.setText(scale1)
        self.offset1Box.setText(offset1)
        self.kBox1.setText(k1)
        self.a4Box1.setText(a41)
        self.a6Box1.setText(a61)
        self.a8Box1.setText(a81)
        self.a10Box1.setText(a101)
        self.a12Box1.setText(a121)
        self.radius2Box.setText(radius2)
        self.scale2Box.setText(scale2)
        self.offset2Box.setText(offset2)
        self.kBox2.setText(k2)
        self.a4Box2.setText(a42)
        self.a6Box2.setText(a62)
        self.a8Box2.setText(a82)
        self.a10Box2.setText(a102)
        self.a12Box2.setText(a122)
        self.radius3Box.setText(radius3)
        self.scale3Box.setText(scale3)
        self.offset3Box.setText(offset3)
        self.kBox3.setText(k3)
        self.a4Box3.setText(a43)
        self.a6Box3.setText(a63)
        self.a8Box3.setText(a83)
        self.a10Box3.setText(a103)
        self.a12Box3.setText(a123)

        self.thickness1Box.setText(thickness1)
        self.thickness2Box.setText(thickness2)
        self.thickness3Box.setText(thickness3)

        self.surface1Combo.setCurrentIndex(surface3index)
        self.surface2Combo.setCurrentIndex(surface2index)
        self.surface3Combo.setCurrentIndex(surface1index)
        self.showFrame1(surface3index)
        self.showFrame2(surface2index)
        self.showFrame3(surface1index)


    def writeSave(self):
        surface1index=self.surface1Combo.currentIndex()
        surface2index=self.surface2Combo.currentIndex()
        surface3index=self.surface3Combo.currentIndex()

        saveFile=open(str(self.saveloadBox.text()), 'w')

        saveFile.write('#### achromat details saved here ####\n')

        saveFile.write('name' + '        ' + str(self.nameBox.text()) + '\n')
        saveFile.write('position' + '    ' + str(self.positionBox.text()) + '\n')
        saveFile.write('radius' + '      ' + str(self.radiusBox.text()) + '\n')
        saveFile.write('refrind1' + '    ' + str(self.refrind1Box.text()) + '\n')
        saveFile.write('refrind2' + '    ' + str(self.refrind2Box.text()) + '\n')

        saveFile.write('#### surface 1 ####' + '\n')
        saveFile.write('surface1' + '    ' + str(self.surface1Combo.currentText() + '\n'))

        saveFile.write('radius1' + '     ' + str(self.radius1Box.text()) + '\n')
        saveFile.write('scale1' + '      ' + str(self.scale1Box.text()) + '\n')
        saveFile.write('offset1' + '     ' + str(self.offset1Box.text()) + '\n')
        saveFile.write('k1' + '          ' + str(self.kBox1.text()) + '\n')
        saveFile.write('a41' + '         ' + str(self.a4Box1.text()) + '\n')
        saveFile.write('a61' + '         ' + str(self.a6Box1.text()) + '\n')
        saveFile.write('a81' + '         ' + str(self.a8Box1.text()) + '\n')
        saveFile.write('a101' + '        ' + str(self.a10Box1.text()) + '\n')
        saveFile.write('a121' + '        ' + str(self.a12Box1.text()) + '\n')

        saveFile.write('thickness1' + '  ' + str(self.thickness1Box.text() + '\n'))

        saveFile.write('#### surface 2 ####' + '\n')
        saveFile.write('surface2' + '    ' + str(self.surface2Combo.currentText() + '\n'))

        saveFile.write('radius2' + '     ' + str(self.radius2Box.text()) + '\n')
        saveFile.write('scale2' + '      ' + str(self.scale2Box.text()) + '\n')
        saveFile.write('offset2' + '     ' + str(self.offset2Box.text()) + '\n')
        saveFile.write('k2' + '          ' + str(self.kBox2.text()) + '\n')
        saveFile.write('a42' + '         ' + str(self.a4Box2.text()) + '\n')
        saveFile.write('a62' + '         ' + str(self.a6Box2.text()) + '\n')
        saveFile.write('a82' + '         ' + str(self.a8Box2.text()) + '\n')
        saveFile.write('a102' + '        ' + str(self.a10Box2.text()) + '\n')
        saveFile.write('a122' + '        ' + str(self.a12Box2.text()) + '\n')


        saveFile.write('thickness2' + '  ' + str(self.thickness2Box.text() + '\n'))

        saveFile.write('#### surface 3 ####' + '\n')
        saveFile.write('surface3' + '    ' + str(self.surface3Combo.currentText() + '\n'))

        saveFile.write('radius3' + '     ' + str(self.radius3Box.text()) + '\n')
        saveFile.write('scale3' + '      ' + str(self.scale3Box.text()) + '\n')
        saveFile.write('offset3' + '     ' + str(self.offset3Box.text()) + '\n')
        saveFile.write('k3' + '          ' + str(self.kBox3.text()) + '\n')
        saveFile.write('a43' + '         ' + str(self.a4Box3.text()) + '\n')
        saveFile.write('a63' + '         ' + str(self.a6Box3.text()) + '\n')
        saveFile.write('a83' + '         ' + str(self.a8Box3.text()) + '\n')
        saveFile.write('a103' + '        ' + str(self.a10Box3.text()) + '\n')
        saveFile.write('a123' + '        ' + str(self.a12Box3.text()) + '\n')

        saveFile.write('thickness3' + '  ' + str(self.thickness3Box.text() + '\n'))

        saveFile.write('free' + '        ' + str(self.free) + '\n')


        saveFile.close()

    def fileSave(self):
        self.saveDialog = QtWidgets.QFileDialog(self)
        if self.saveDialog.exec_()==QtWidgets.QFileDialog.Accepted:
            self.fileStringList = self.saveDialog.selectedFiles()
            self.saveloadBox.setText(self.fileStringList[0][len(self.cwd)+1:])

    def fileLoad(self):
        self.saveloadBox.setText(QtWidgets.QFileDialog.getOpenFileName()[len(self.cwd)+1:])

        openFile=open(str(self.saveloadBox.text()), 'r')

        lines=openFile.readlines()
        for line in lines:
            if line[0:12]=='name        ':
                self.nameBox.setText(line[12:-1])
            elif line[0:12]=='position    ':
                self.positionBox.setText(line[12:-1])
            elif line[0:12]=='radius      ':
                self.radiusBox.setText(line[12:-1])
            elif line[0:12]=='refrind1    ':
                self.refrind1Box.setText(line[12:-1])
            elif line[0:12]=='refrind2    ':
                self.refrind2Box.setText(line[12:-1])
            elif line[0:12]=='radius1     ':
                self.radius1Box.setText(line[12:-1])
            elif line[0:12]=='scale1      ':
                self.scale1Box.setText(line[12:-1])
            elif line[0:12]=='offset1     ':
                self.offset1Box.setText(line[12:-1])
            elif line[0:12]=='k1          ':
                self.kBox1.setText(line[12:-1])
            elif line[0:12]=='a41         ':
                self.a4Box1.setText(line[12:-1])
            elif line[0:12]=='a61         ':
                self.a6Box1.setText(line[12:-1])
            elif line[0:12]=='a81         ':
                self.a8Box1.setText(line[12:-1])
            elif line[0:12]=='a101         ':
                self.a10Box1.setText(line[12:-1])
            elif line[0:12]=='a121         ':
                self.a12Box1.setText(line[12:-1])
            elif line[0:12]=='radius2     ':
                self.radius2Box.setText(line[12:-1])
            elif line[0:12]=='scale2      ':
                self.scale2Box.setText(line[12:-1])
            elif line[0:12]=='offset2     ':
                self.offset2Box.setText(line[12:-1])
            elif line[0:12]=='k2          ':
                self.kBox2.setText(line[12:-1])
            elif line[0:12]=='a42         ':
                self.a4Box2.setText(line[12:-1])
            elif line[0:12]=='a62         ':
                self.a6Box2.setText(line[12:-1])
            elif line[0:12]=='a82         ':
                self.a8Box2.setText(line[12:-1])
            elif line[0:12]=='a102         ':
                self.a10Box2.setText(line[12:-1])
            elif line[0:12]=='a122         ':
                self.a12Box2.setText(line[12:-1])
            elif line[0:12]=='radius3     ':
                self.radius3Box.setText(line[12:-1])
            elif line[0:12]=='scale3      ':
                self.scale3Box.setText(line[12:-1])
            elif line[0:12]=='offset3     ':
                self.offset3Box.setText(line[12:-1])
            elif line[0:12]=='k3          ':
                self.kBox3.setText(line[12:-1])
            elif line[0:12]=='a43         ':
                self.a4Box3.setText(line[12:-1])
            elif line[0:12]=='a63         ':
                self.a6Box3.setText(line[12:-1])
            elif line[0:12]=='a83         ':
                self.a8Box3.setText(line[12:-1])
            elif line[0:12]=='a103         ':
                self.a10Box3.setText(line[12:-1])
            elif line[0:12]=='a123         ':
                self.a12Box3.setText(line[12:-1])
            elif line[0:12]=='thickness1  ':
                self.thickness1Box.setText(line[12:-1])
            elif line[0:12]=='thickness2  ':
                self.thickness2Box.setText(line[12:-1])
            elif line[0:12]=='thickness3  ':
                self.thickness3Box.setText(line[12:-1])
            elif line[0:12]=='surface1    ' and line[12:-1]=='Asphere':
                self.surface1Combo.setCurrentIndex(0)
                self.showFrame1(0)
            elif line[0:12]=='surface1    ' and line[12:-1]=='Flat':
                self.surface1Combo.setCurrentIndex(1)
                self.showFrame1(1)
            elif line[0:12]=='surface2    ' and line[12:-1]=='Asphere':
                self.surface2Combo.setCurrentIndex(0)
                self.showFrame2(0)
            elif line[0:12]=='surface2    ' and line[12:-1]=='Flat':
                self.surface2Combo.setCurrentIndex(1)
                self.showFrame2(1)
            elif line[0:12]=='surface3    ' and line[12:-1]=='Asphere':
                self.surface3Combo.setCurrentIndex(0)
                self.showFrame3(0)
            elif line[0:12]=='surface3    ' and line[12:-1]=='Flat':
                self.surface3Combo.setCurrentIndex(1)
                self.showFrame3(1)
            elif line[0:12]=='free        ':
                if line[12:-1]=='True':
                    self.free=True
                elif line[12:-1]=='False':
                    self.free=False



class ZemaxDialog(QtWidgets.QDialog, Ui_ZemaxDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.zemaxButtonBox.accepted.connect(self.writeSave)
        self.fileButton.clicked.connect(self.handleFileButton)
        self.loadButton.clicked.connect(self.fileLoad)
        self.zemaxFileButton.clicked.connect(self.handleZemaxFileButton)
        self.flipButton.clicked.connect(self.handleFlipButton)
        self.way=True
        self.free=False
        self.cwd=os.getcwd()



    def getValues(self):
        fileName=str(self.fileBox.text())
        zemaxFileName=str(self.zemaxFileBox.text())
        name=str(self.nameBox.text())
        position=float(self.positionBox.text())
        free=self.free
        return fileName, zemaxFileName, name, position, self.way, free

    def handleFileButton(self):
        self.saveDialog = QtWidgets.QFileDialog(self)
        if self.saveDialog.exec_()==QtWidgets.QFileDialog.Accepted:
            self.fileStringList = self.saveDialog.selectedFiles()
            self.fileBox.setText(self.fileStringList[0][len(self.cwd)+1:])

    def handleZemaxFileButton(self):
        self.fileDialog = QtWidgets.QFileDialog(self)
        if self.fileDialog.exec_()==QtWidgets.QFileDialog.Accepted:
            self.fileStringList = self.fileDialog.selectedFiles()
            #print(self.fileStringList)
            self.zemaxFileBox.setText(self.fileStringList[0][len(self.cwd)+1:])

    def writeSave(self):
        saveFile=open(str(self.fileBox.text()), 'w')

        saveFile.write('#### achromat details saved here ####\n')

        saveFile.write('name' + '        ' + str(self.nameBox.text()) + '\n')
        saveFile.write('zemax file' + '  ' + str(self.zemaxFileBox.text()) + '\n')
        saveFile.write('position' + '    ' + str(self.positionBox.text()) + '\n')
        saveFile.write('way' + '         ' + str(self.way) + '\n')
        saveFile.write('free' + '        ' + str(self.free) + '\n')

        saveFile.close()

    def fileLoad(self):
        self.fileBox.setText(str(QtWidgets.QFileDialog.getOpenFileName())[len(self.cwd)+1:])

        openFile=open(str(self.fileBox.text()), 'r')

        lines=openFile.readlines()
        for line in lines:
            if line[0:12]=='name        ':
                self.nameBox.setText(line[12:-1])
            elif line[0:12]=='zemax file  ':
                self.zemaxFileBox.setText(line[12:-1])
            elif line[0:12]=='position    ':
                self.positionBox.setText(line[12:-1])
            elif line[0:12]=='way         ':
                if line[12:]=='True':
                    self.way=True
                elif line[12:]=='False':
                    self.way=False
            elif line[0:12]=='free        ':
                if line[12:-1]=='True':
                    self.free=True
                elif line[12:-1]=='False':
                    self.free=False


    def handleFlipButton(self):
        self.way=not self.way



class OptimiseDialog(QtWidgets.QDialog, Ui_OptimiseDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)




if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec_())
    window.show()
    sys.exit(app.exec_())
