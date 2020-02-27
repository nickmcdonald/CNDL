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


from ies import MixMethod, normalizeIesData, applyIesDataNoise

from nodes import IesNodeData

from preview import Preview2D

from qtpy.QtWidgets import QWidget, QGroupBox, QFormLayout, QComboBox, QSlider
from qtpy.QtCore import Qt

from qtpynodeeditor import NodeDataModel
from qtpynodeeditor import Port


class AlterOperationDataModel(NodeDataModel):
    caption_visible = True
    num_ports = {'input': 1, 'output': 1}
    port_caption_visible = True
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


class NormalizeModel(AlterOperationDataModel):
    name = "Normalize"

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)

    def update(self):
        if self._in:
            self._out = IesNodeData(normalizeIesData(self._in.data))
        else:
            self._out = None
        super().update()


class NoiseModel(AlterOperationDataModel):
    name = "Noise"

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._methodCB = QComboBox()
        self._layout.addRow(self._methodCB)
        for method in MixMethod:
            self._methodCB.addItem(method.value)
        self._methodCB.currentIndexChanged.connect(self.update)

        self._latscale = QSlider(Qt.Horizontal)
        self._layout.addRow(self._latscale)
        self._latscale.setMinimum(0)
        self._latscale.setMaximum(100)
        self._latscale.setValue(20)
        self._latscale.valueChanged.connect(self.update)

        self._latintensity = QSlider(Qt.Horizontal)
        self._layout.addRow(self._latintensity)
        self._latintensity.setMinimum(0)
        self._latintensity.setMaximum(100)
        self._latintensity.setValue(20)
        self._latintensity.valueChanged.connect(self.update)

        self._longscale = QSlider(Qt.Horizontal)
        self._layout.addRow(self._longscale)
        self._longscale.setMinimum(0)
        self._longscale.setMaximum(360)
        self._longscale.setValue(0)
        self._longscale.valueChanged.connect(self.update)

        self._longintensity = QSlider(Qt.Horizontal)
        self._layout.addRow(self._longintensity)
        self._longintensity.setMinimum(0)
        self._longintensity.setMaximum(100)
        self._longintensity.setValue(20)
        self._longintensity.valueChanged.connect(self.update)

    def update(self):
        if self._in:
            self._out = IesNodeData(applyIesDataNoise(
                           self._in.data,
                           self._latscale.value,
                           self._latintensity.value,
                           self._longscale.value,
                           self._longintensity.value,
                           MixMethod(self._methodCB.currentText())))
        super().update()
