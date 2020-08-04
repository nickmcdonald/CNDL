########################################################
#
# Copyright (C) 2020-2021 Nick McDonald <nick@lazymorninggames.com>
#
# This file is part of CNDL.
#
# CNDL can not be copied and/or distributed without the express
#
# permission of Nick McDonald
########################################################

import os

from qtpy.QtWidgets import (QMenuBar, QAction)
from qtpy.QtGui import QIcon

from menu import (Preset, loadPreset, CNDLSplashScreen, TutorialSplashScreen,
                  LicenseSplashScreen, saveCNDLFile, openCNDLFile)
from version import VERSION


class CNDLMenuBar(QMenuBar):

    def __init__(self, app):
        super().__init__(app.view)
        self.app = app
        self.preset = Preset.EMPTY
        self.fileMenu = self.addMenu('&File')

        self.workingFile = None
        saveFile = QAction(QIcon(), "Save", self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.triggered.connect(self.saveFile)
        self.fileMenu.addAction(saveFile)

        saveFileAs = QAction(QIcon(), "Save As...", self)
        saveFileAs.setShortcut("Ctrl+Shift+S")
        saveFileAs.triggered.connect(self.saveFileAs)
        self.fileMenu.addAction(saveFileAs)

        openFile = QAction(QIcon(), "Open...", self)
        openFile.setShortcut("Ctrl+O")
        openFile.triggered.connect(self.openFile)
        self.fileMenu.addAction(openFile)

        presetMenu = self.fileMenu.addMenu("Load Preset")
        action = QAction(QIcon(), Preset.EMPTY.value, self)
        action.triggered.connect(self.setPresetEmpty)
        presetMenu.addAction(action)
        action = QAction(QIcon(), Preset.SPOTLIGHT.value, self)
        action.triggered.connect(self.setPresetSpotlight)
        presetMenu.addAction(action)
        action = QAction(QIcon(), Preset.LAMPSHADE.value, self)
        action.triggered.connect(self.setPresetLampshade)
        presetMenu.addAction(action)
        exit = QAction(QIcon(), '&Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        exit.triggered.connect(self.app.quit)
        self.fileMenu.addAction(exit)

        self.viewMenu = self.addMenu('&View')

        zoomOut = QAction(QIcon(), "Zoom Out", self)
        zoomOut.setShortcut("Down")
        zoomOut.triggered.connect(self.app.view.scale_down)
        self.viewMenu.addAction(zoomOut)

        zoomIn = QAction(QIcon(), "Zoom In", self)
        zoomIn.setShortcut("Up")
        zoomIn.triggered.connect(self.app.view.scale_up)
        self.viewMenu.addAction(zoomIn)

        showSplashscreen = QAction(QIcon(), "Show Splash Screen", self)
        showSplashscreen.triggered.connect(self.showSplashscreen)
        self.viewMenu.addAction(showSplashscreen)

        self.helpMenu = self.addMenu('&Help')
        showTutorial = QAction(QIcon(), "Show Tutorial", self)
        showTutorial.triggered.connect(self.showTutorial)
        self.helpMenu.addAction(showTutorial)

        self.aboutMenu = self.addMenu('&About')
        self.aboutMenu.addAction(VERSION).setEnabled(False)
        self.aboutMenu.addAction("By Lazy Morning Games").setEnabled(False)
        self.aboutMenu.addAction("Show License").triggered.connect(self.showLicense)
        self.aboutMenu.addAction("Website").triggered.connect(self.openWebsite)

    def openWebsite(self):
        os.system("start \"\" https://cndl.io")

    def setPresetEmpty(self):
        loadPreset(self.app.scene, Preset.EMPTY)
        self.workingFile = None

    def setPresetSpotlight(self):
        loadPreset(self.app.scene, Preset.SPOTLIGHT)
        self.workingFile = None

    def setPresetLampshade(self):
        loadPreset(self.app.scene, Preset.LAMPSHADE)
        self.workingFile = None

    def showSplashscreen(self):
        CNDLSplashScreen(self.app).show()

    def showTutorial(self):
        TutorialSplashScreen(self.app).show()

    def showLicense(self):
        LicenseSplashScreen(self.app).show()

    def saveFileAs(self):
        self.workingFile = saveCNDLFile(self.app.scene)

    def saveFile(self):
        self.workingFile = saveCNDLFile(self.app.scene, self.workingFile)

    def openFile(self):
        self.workingFile = openCNDLFile(self.app.scene)
