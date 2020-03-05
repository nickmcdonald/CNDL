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
from qtpy.QtWidgets import QApplication
from qtpy.QtGui import QIcon
from qtpy.QtCore import QPointF

from nodes import (FileNode,
                   BlankNode,
                   SpotlightNode,
                   NoiseNode,
                   MixNode,
                   DisplayNode,
                   NormalizeNode)

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


def main(app):
    f = open("ui/editortheme.json", 'r')
    stylesheet = f.read()
    f.close()
    style = nodeeditor.StyleCollection.from_json(processStyle(stylesheet))
    registry = nodeeditor.DataModelRegistry()

    models = (FileNode,
              BlankNode,
              SpotlightNode,
              NoiseNode,
              MixNode,
              DisplayNode,
              NormalizeNode)

    for model in models:
        registry.register_model(model, category='Operations', style=style)

    scene = nodeeditor.FlowScene(registry=registry, style=style)

    view = nodeeditor.FlowView(scene)
    view.setWindowTitle("CNDL")
    monitor = get_monitors()[0]
    view.resize(monitor.width - monitor.width / 10,
                monitor.height - monitor.height / 10)
    view.move(monitor.width / 30, monitor.height / 30)

    displayNode = scene.create_node(DisplayNode)
    displayNode.position += QPointF(view.geometry().width() / 2,
                                    view.geometry().height() / 3)

    view.show()

    return scene, view


if __name__ == '__main__':
    log.basicConfig(level='DEBUG')
    app = QApplication([])
    app.setWindowIcon(QIcon('img/CNDL.ico'))

    f = open("ui/theme.qss", 'r')
    stylesheet = f.read()
    f.close()

    app.setStyleSheet(processStyle(stylesheet))

    scene, view = main(app)
    view.show()
    app.exec_()
