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

from menu import Preset, loadPreset, CNDLSplashScreen, TutorialSplashScreen


class CNDLMenuBar(QMenuBar):

    def __init__(self, app):
        super().__init__(app.view)
        self.app = app
        self.preset = Preset.EMPTY
        self.fileMenu = self.addMenu('&File')

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
        self.aboutMenu.addAction("CNDL v1.0").setEnabled(False)
        self.aboutMenu.addAction("By Lazy Morning Games").setEnabled(False)
        self.aboutMenu.addAction("Website").triggered.connect(self.openWebsite)

    def openWebsite(self):
        os.system("start \"\" https://cndl.io")

    def setPresetEmpty(self):
        loadPreset(self.app.scene, Preset.EMPTY)

    def setPresetSpotlight(self):
        loadPreset(self.app.scene, Preset.SPOTLIGHT)

    def setPresetLampshade(self):
        loadPreset(self.app.scene, Preset.LAMPSHADE)

    def showSplashscreen(self):
        CNDLSplashScreen(self.app).show()

    def showTutorial(self):
        TutorialSplashScreen(self.app).show()
