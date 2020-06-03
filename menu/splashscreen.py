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
from screeninfo import get_monitors

from qtpy.QtWidgets import (QSplashScreen, QGroupBox, QPushButton,
                            QFormLayout, QComboBox, QLabel, QSpacerItem)
from qtpy.QtGui import QPixmap
from qtpy.QtCore import QPoint, Qt

from menu import Preset, loadPreset


class CNDLSplashScreen(QSplashScreen):

    def __init__(self, app):
        self.app = app
        monitor = get_monitors()[0]

        if monitor.height <= 1100:
            pixmap = QPixmap("img/splashscreen1080p.png")
            height = 512
            width = 906
        elif monitor.height <= 1500:
            pixmap = QPixmap("img/splashscreen1440p.png")
            height = 768
            width = 1359
        else:
            pixmap = QPixmap("img/splashscreen4K.png")
            height = 1024
            width = 1812
        super().__init__(app.view, pixmap=pixmap)

        self.items = QGroupBox(self)
        self.layout = QFormLayout()
        self.items.setLayout(self.layout)

        if monitor.height <= 1100:
            self.items.move(QPoint(width/2 - width/4, height / 2))
            self.items.resize(width/2, height / 2)
        elif monitor.height <= 1500:
            self.items.move(QPoint(width/2 - width/8, height / 2))
            self.items.resize(width/4, height / 2)
        else:
            self.items.move(QPoint(width/2 - width/8, height / 2))
            self.items.resize(width/4, height / 2)

        self.presetCB = QComboBox()
        for preset in Preset:
            self.presetCB.addItem(preset.value)
        self.presetCB.currentIndexChanged.connect(self.setPreset)
        self.layout.addRow("Preset", self.presetCB)

        self.layout.addItem(QSpacerItem(10, 10))

        self.tutorialButton = QPushButton("Show Tutorial")
        self.tutorialButton.clicked.connect(self.showTutorial)
        self.layout.addRow(self.tutorialButton)

        self.layout.addItem(QSpacerItem(30, 30))

        label = QLabel("CNDL is no longer free for professional use")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addRow(label)

        label = QPushButton("Please Support us on Patreon")
        label.clicked.connect(self.showPatreon)
        self.layout.addRow(label)

        label = QLabel("or via another method listed on our website")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addRow(label)

        label = QLabel("CNDL v1.1.1")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addRow(label)

        label = QLabel("Created by Lazy Morning Games")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addRow(label)

    def showTutorial(self):
        TutorialSplashScreen(self.app).show()

    def setPreset(self):
        loadPreset(self.app.scene, Preset(self.presetCB.currentText()))

    def showPatreon(self):
        os.system("start \"\" https://www.patreon.com/lazymorninggames")


class TutorialSplashScreen(QSplashScreen):

    def __init__(self, app):
        self.app = app
        monitor = get_monitors()[0]
        if monitor.height <= 1100:
            pixmap = QPixmap("img/Tutorial1080p.png")
        elif monitor.height <= 1500:
            pixmap = QPixmap("img/Tutorial1440p.png")
        else:
            pixmap = QPixmap("img/Tutorial4K.png")
        super().__init__(app.view, pixmap=pixmap)
