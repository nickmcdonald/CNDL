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

from nodes import IesFileSourceDataModel, IesDefaultSourceDataModel
from nodes import AdditionModel, IesDisplayModel

import theme.styles as styles


def main(app):
    style = nodeeditor.StyleCollection.from_json(styles.DEFAULT)

    registry = nodeeditor.DataModelRegistry()

    models = (IesFileSourceDataModel,
              IesDefaultSourceDataModel,
              AdditionModel,
              IesDisplayModel)

    for model in models:
        registry.register_model(model, category='Operations', style=style)

    scene = nodeeditor.FlowScene(registry=registry, style=style)

    view = nodeeditor.FlowView(scene)
    view.setWindowTitle("CNDL")
    monitor = get_monitors()[0]
    view.resize(monitor.width - monitor.width / 10,
                monitor.height - monitor.height / 10)
    view.move(monitor.width / 30, monitor.height / 30)

    view.show()

    return scene, view


if __name__ == '__main__':
    log.basicConfig(level='DEBUG')
    app = QApplication([])
    app.setWindowIcon(QIcon('img/LogoBold.png'))
    scene, view = main(app)
    view.show()
    app.exec_()
