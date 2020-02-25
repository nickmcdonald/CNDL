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


import contextlib

from ies import mixIesData, MixMethod

from nodes import IesNodeData

from preview import Preview2D

from qtpy.QtWidgets import QWidget, QGroupBox, QFormLayout, QComboBox

from qtpynodeeditor import NodeData, NodeDataModel
from qtpynodeeditor import NodeValidationState, Port


class CombineOperationDataModel(NodeDataModel):
    caption_visible = True
    num_ports = {'input': 2, 'output': 1}
    port_caption_visible = True
    data_type = IesNodeData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies1 = None
        self._ies2 = None
        self._result = None

        self._form = QGroupBox()
        self._layout = QFormLayout()
        self._form.setLayout(self._layout)
        self._preview = Preview2D(None)
        self._layout.addRow(self._preview)

        self._validation_state = NodeValidationState.warning
        self._validation_message = 'Uninitialized'

    @property
    def caption(self):
        return self.name

    def _check_inputs(self):
        ies1_ok = self._ies1 is not None and self._ies1.data_type.id in ('ies')
        ies2_ok = self._ies2 is not None and self._ies2.data_type.id in ('ies')

        if not ies1_ok or not ies2_ok:
            self._validation_state = NodeValidationState.warning
            self._validation_message = "Missing or incorrect inputs"
            self._result = None
            self.data_updated.emit(0)
            return False

        self._validation_state = NodeValidationState.valid
        self._validation_message = ''
        return True

    @contextlib.contextmanager
    def _compute_lock(self):
        if not self._ies1 or not self._ies2:
            raise RuntimeError('inputs unset')

        with self._ies1.lock:
            with self._ies2.lock:
                yield

        self.data_updated.emit(0)

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
        return self._result

    def set_in_data(self, data: NodeData, port: Port):
        '''
        New data at the input of the node
        Parameters
        ----------
        data : NodeData
        port_index : int
        '''
        if port.index == 0:
            self._ies1 = data
        elif port.index == 1:
            self._ies2 = data

        if self._check_inputs():
            with self._compute_lock():
                self.compute()
                self.update()

    def embedded_widget(self) -> QWidget:
        return self._form

    def validation_state(self) -> NodeValidationState:
        return self._validation_state

    def validation_message(self) -> str:
        return self._validation_message

    def update(self):
        self._preview.update(self._result.ies)

    def compute(self):
        ...


class MixModel(CombineOperationDataModel):
    name = "Mix"

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._methodCB = QComboBox()
        self._layout.addRow(self._methodCB)

        for method in MixMethod:
            self._methodCB.addItem(method.value)

    def selectionchange(self, i):
        for count in range(self.cb.count()):
            self.cb.currentText()

    def compute(self):
        self._result = IesNodeData(mixIesData(self._ies1.ies,
                                              self._ies2.ies,
                                              MixMethod(self._methodCB.currentText())))
