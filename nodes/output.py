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


from render import Renderer

from qtpy.QtWidgets import QWidget, QLabel
from qtpy.QtGui import QPixmap, QImage

from qtpynodeeditor import NodeData, NodeDataModel
from qtpynodeeditor import PortType, NodeValidationState, Port

from nodes import IesNodeData


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
        self._renderer = Renderer(self.update_image)
        self._validation_state = NodeValidationState.warning
        self._validation_message = 'Uninitialized'

    def set_in_data(self, data: NodeData, port: Port):
        '''
        New data propagated to the input
        '''
        self._ies = data
        ies_ok = (self._ies is not None and self._ies.data_type.id in ('ies'))

        if ies_ok:
            self._renderer.render(self._ies.data, 1000)

        else:
            self._label.setPixmap(QPixmap('img/RenderPlaceholder.png'))

    def update_image(self, image, size):
        qim = QImage(image, size[0], size[1], QImage.Format_RGB888)
        self._label.setPixmap(QPixmap.fromImage(qim.mirrored(False, True)))

    def embedded_widget(self) -> QWidget:
        return self._label
