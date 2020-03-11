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


import logging as log
from screeninfo import get_monitors

import qtpynodeeditor as nodeeditor
from qtpy.QtWidgets import (QApplication, QMenuBar, QHBoxLayout)
from qtpy.QtGui import QIcon
from qtpy.QtCore import QPointF

from nodes import (FileNode,
                   PointlightNode,
                   SpotlightNode,
                   NoiseNode,
                   MixNode,
                   DisplayNode,
                   NormalizeNode)

from menu import CNDLSplashScreen, CNDLMenuBar

from multiprocessing import freeze_support

freeze_support()


def processStyle(style: str) -> str:
    style = style.replace("NODECOLOR", "#505050")
    style = style.replace("THEMECOLORHARD", "#f4ac62")
    style = style.replace("THEMECOLORMAIN", "#f4cba1")
    style = style.replace("THEMECOLORSOFT", "#f4e0cb")
    style = style.replace("SOLIDBACKGROUNDCOLOR", "#555555")
    style = style.replace("TEXTCOLORMAIN", "#C0C0C0")
    style = style.replace("TEXTCOLORDARK", "#808080")
    style = style.replace("ALTBACKGROUNDCOLOR", "#323232")
    style = style.replace("DISABLEDTEXTCOLOR", "#787878")
    style = style.replace("BORDERCOLOR", "#FF0000")
    return style


class CNDL(QApplication):

    def __init__(self):
        super().__init__([])
        self.setWindowIcon(QIcon('img/CNDL.ico'))

        f = open("ui/theme.qss", 'r')
        style = f.read()
        f.close()

        self.setStyleSheet(processStyle(style))

        f = open("ui/editortheme.json", 'r')
        style = f.read()
        f.close()
        style = nodeeditor.StyleCollection.from_json(processStyle(style))

        registry = nodeeditor.DataModelRegistry()
        models = (FileNode,
                  PointlightNode,
                  SpotlightNode,
                  NoiseNode)
        for model in models:
            registry.register_model(model, category='Inputs', style=style)

        models = (MixNode, NormalizeNode)
        for model in models:
            registry.register_model(model, category='Operations', style=style)

        registry.register_model(DisplayNode, category='Outputs', style=style)

        self.scene = nodeeditor.FlowScene(registry=registry, style=style)

        self.view = nodeeditor.FlowView(self.scene)
        self.view.setWindowTitle("CNDL")
        monitor = get_monitors()[0]
        self.view.resize(monitor.width - monitor.width / 10,
                         monitor.height - monitor.height / 10)
        self.view.move(monitor.width / 30, monitor.height / 30)

        if monitor.height < 1100:
            self.view.scale_down()
            self.view.scale_down()
            self.view.scale_down()
            self.view.scale_down()
        elif monitor.height < 1500:
            self.view.scale_down()
            self.view.scale_down()

        displayNode = self.scene.create_node(DisplayNode)
        displayNode.position += QPointF(self.view.geometry().width() / 2,
                                        self.view.geometry().height() / 3)

        CNDLMenuBar(self)

        self.view.show()
        CNDLSplashScreen(self).show()



if __name__ == '__main__':
    log.basicConfig(level='DEBUG')
    app = CNDL()
    app.exec_()
