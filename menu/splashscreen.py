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
                            QFormLayout, QComboBox, QLabel, QSpacerItem,
                            QScrollArea, QWidget, QVBoxLayout)
from qtpy.QtGui import QPixmap
from qtpy.QtCore import QPoint, Qt

from menu import Preset, loadPreset
from version import VERSION


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
        self.presetCB.setCurrentIndex(1)
        self.layout.addRow("Preset", self.presetCB)

        self.layout.addItem(QSpacerItem(10, 10))

        self.tutorialButton = QPushButton("Show Tutorial")
        self.tutorialButton.clicked.connect(self.showTutorial)
        self.layout.addRow(self.tutorialButton)

        self.layout.addItem(QSpacerItem(30, 30))

        label = QPushButton("Please Support us on Patreon")
        label.clicked.connect(self.showPatreon)
        self.layout.addRow(label)

        label = QLabel("or via another method listed on our website")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addRow(label)

        label = QLabel(VERSION)
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


class LicenseSplashScreen(QSplashScreen):

    def __init__(self, app):
        self.app = app
        monitor = get_monitors()[0]
        if monitor.height <= 1100:
            pixmap = QPixmap("img/splashscreen_empty1080p.png")
        elif monitor.height <= 1500:
            pixmap = QPixmap("img/splashscreen_empty1440p.png")
        else:
            pixmap = QPixmap("img/splashscreen_empty4K.png")

        super().__init__(app.view, pixmap=pixmap)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QVBoxLayout()

        self.layout.addWidget(self.scroll)

        object = QLabel("TextLabel")
        object.setText('''
###############################################################################

# CNDL #

Copyright (C) 2020-2021 Lazy Morning Games <nick@lazymorninggames.com>

###############################################################################

# qtpynodeeditor #

Copyright (c) 2019, Ken Lauer
All rights reserved.

qtpynodeeditor is a derivative work of NodeEditor by Dmitry Pinaev. It follows
in the footsteps of the original and is licensed by the BSD 3-clause license.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the
distribution.
    * Neither the name of copyright holder, nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

###############################################################################
        ''')
        self.vbox.addWidget(object)

        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
