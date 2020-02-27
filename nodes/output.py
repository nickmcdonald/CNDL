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

from render import Renderer

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from qtpy.QtWidgets import QWidget, QLabel
from qtpy.QtGui import QPixmap

from qtpynodeeditor import NodeData, NodeDataModel
from qtpynodeeditor import PortType, NodeValidationState, Port

from nodes import IesNodeData


class DisplayUpdateHandler(PatternMatchingEventHandler):

    def __init__(self, update_method):
        super().__init__(patterns=["*/render/img/image.png"])

        self.update = update_method

    def on_modified(self, e):
        self.update()


class IesDisplayModel(NodeDataModel):
    name = "IESDisplay"
    data_type = IesNodeData.data_type
    caption_visible = False
    num_ports = {PortType.input: 1, PortType.output: 0}
    port_caption = {'input': {0: 'Ies'}}

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies = IesNodeData()
        self._label = QLabel()
        self._label.setPixmap(QPixmap('img/RenderPlaceholder.png'))
        self._render_passes = 2
        self._renderer = Renderer()
        self._validation_state = NodeValidationState.warning
        self._validation_message = 'Uninitialized'

        event_handler = DisplayUpdateHandler(self.update_image)

        observer = Observer()
        observer.schedule(event_handler, os.getcwd(), recursive=True)
        observer.start()

    def set_in_data(self, data: NodeData, port: Port):
        '''
        New data propagated to the input
        '''
        self._ies = data
        ies_ok = (self._ies is not None and self._ies.data_type.id in ('ies'))

        if ies_ok:
            self._validation_state = NodeValidationState.valid
            self._validation_message = ''
            self._renderer.render(self._ies.data, 1000, self._render_passes)

        else:
            self._validation_state = NodeValidationState.warning
            self._validation_message = "Missing or incorrect inputs"
            self._label.setPixmap(QPixmap('img/RenderPlaceholder.png'))

    def update_image(self):
        self._label.setPixmap(QPixmap('render/img/image.png'))

    def embedded_widget(self) -> QWidget:
        return self._label
