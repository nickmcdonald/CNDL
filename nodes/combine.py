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


from ies import mixIesData, MixMethod

from nodes import IesNodeData

from preview import Preview2D

from qtpy.QtWidgets import QWidget, QGroupBox, QFormLayout, QComboBox

from qtpynodeeditor import NodeData, NodeDataModel
from qtpynodeeditor import Port


class CombineNode(NodeDataModel):
    caption_visible = False
    num_ports = {'input': 2, 'output': 1}
    data_type = IesNodeData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._in1 = None
        self._in2 = None
        self._out = None

        self._form = QGroupBox()
        self._layout = QFormLayout()
        self._form.setLayout(self._layout)
        self._preview = Preview2D(None)
        self._layout.addRow(self._preview)

    @property
    def caption(self):
        return self.name

    def out_data(self, port: int) -> NodeData:
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

    def set_in_data(self, data: NodeData, port: Port):
        '''
        New data at the input of the node
        Parameters
        ----------
        data : NodeData
        port_index : int
        '''
        if port.index == 0:
            self._in1 = data
        elif port.index == 1:
            self._in2 = data
        self.update()

    def embedded_widget(self) -> QWidget:
        return self._form

    def update(self):
        if self._out:
            self._preview.update(self._out.data)
        else:
            self._preview.update(None)
        self.data_updated.emit(0)


class MixNode(CombineNode):
    name = "Mix"
    caption_visible = True

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._methodCB = QComboBox()
        self._layout.addRow(self._methodCB)
        for method in MixMethod:
            self._methodCB.addItem(method.value)
        self._methodCB.currentIndexChanged.connect(self.update)

    def update(self):
        if self._in1 and self._in2:
            self._out = IesNodeData(mixIesData(
                           self._in1.data,
                           self._in2.data,
                           MixMethod(self._methodCB.currentText())
            ))
        else:
            self._out = None
        super().update()

    def setMixMethod(self, method: MixMethod):
        self._methodCB.setCurrentText(method.value)
