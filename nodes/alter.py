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


from ies import normalizeIesData

from nodes import IesNodeData

from preview import Preview2D

from qtpy.QtWidgets import QWidget, QGroupBox, QFormLayout

from qtpynodeeditor import NodeDataModel
from qtpynodeeditor import Port


class AlterNode(NodeDataModel):
    caption_visible = False
    num_ports = {'input': 1, 'output': 1}
    data_type = IesNodeData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._in = None
        self._out = None

        self._form = QGroupBox()
        self._layout = QFormLayout()
        self._form.setLayout(self._layout)
        self._preview = Preview2D(None)
        self._layout.addRow(self._preview)

    @property
    def caption(self):
        return self.name

    def out_data(self, port: int) -> IesNodeData:
        '''
        The output data as a result of this calculation
        Parameters
        ----------
        port : int
        Returns
        -------
        value : NodeData
        '''
        return self._out

    def set_in_data(self, data: IesNodeData, port: Port):
        '''
        New data at the input of the node
        Parameters
        ----------
        data : NodeData
        port_index : int
        '''
        self._in = data
        self.update()

    def embedded_widget(self) -> QWidget:
        return self._form

    def update(self):
        if self._out:
            self._preview.update(self._out.data)
        else:
            self._preview.update(None)
        self.data_updated.emit(0)


class NormalizeNode(AlterNode):
    name = "Normalize"
    caption_visible = True

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)

    def update(self):
        if self._in:
            self._out = IesNodeData(normalizeIesData(self._in.data))
        else:
            self._out = None
        super().update()
