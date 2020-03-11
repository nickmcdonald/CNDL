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

from menu import Preset, loadPreset


class CNDLMenuBar(QMenuBar):

    def __init__(self, app):
        super().__init__(app.view)
        self.app = app

        self.fileMenu = self.addMenu('&File')
        presetMenu = self.fileMenu.addMenu("Load Preset")
        for preset in Preset:
            action = QAction(preset.value)
            action.triggered.connect(self.setPreset)
            presetMenu.addAction(action)

        self.viewMenu = self.addMenu('&View')

        showSplashscreen = QAction("Show Splash Screen")
        self.viewMenu.addAction(showSplashscreen)

        self.helpMenu = self.addMenu('&Help')

        self.aboutMenu = self.addMenu('&About')
        self.aboutMenu.addAction("CNDL v1.0").setEnabled(False)
        self.aboutMenu.addAction("By Lazy Morning Games").setEnabled(False)
        self.aboutMenu.addAction("Website").triggered.connect(self.openWebsite)

    def openWebsite(self):
        os.system("start \"\" https://cndl.io")

    def setPreset(self, other):
        help(other)
        loadPreset(self.app.scene, Preset(self.presetCB.currentText()))
