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

from screeninfo import get_monitors

from qtpy.QtWidgets import (QSplashScreen, QGroupBox,
                            QFormLayout, QComboBox)
from qtpy.QtGui import QPixmap
from qtpy.QtCore import QPoint

from menu import Preset, loadPreset


class CNDLSplashScreen(QSplashScreen):

    def __init__(self, view, scene):
        self.view = view
        self.scene = scene
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
        super().__init__(view, pixmap=pixmap)

        self.items = QGroupBox(self)
        self.layout = QFormLayout()
        self.items.setLayout(self.layout)

        self.items.move(QPoint(width/2 - width/8, height / 2))
        self.items.resize(width/4, height / 2)

        self.presetCB = QComboBox()
        for preset in Preset:
            self.presetCB.addItem(preset.value)
        self.presetCB.currentIndexChanged.connect(self.setPreset)
        self.layout.addRow("Preset", self.presetCB)

    def setPreset(self):
        loadPreset(self.scene, Preset(self.presetCB.currentText()))
