from ies import normalizeIesData

from nodes import IesNodeData

from preview import Preview2D

from qtpy.QtWidgets import QWidget, QGroupBox, QFormLayout

from qtpynodeeditor import NodeDataModel
from qtpynodeeditor import Port, NodeValidationState


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

    def validation_state(self) -> NodeValidationState:
        return self._validation_state

    def validation_message(self) -> str:
        return self._validation_message


class NormalizeNode(AlterNode):
    name = "Normalize"
    caption_visible = True

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._validation_state = NodeValidationState.warning
        self._validation_message = 'Missing or invalid input'

    def update(self):
        if self._in:
            self._validation_state = NodeValidationState.valid
            self._validation_message = ''
            self._out = IesNodeData(normalizeIesData(self._in.data))
        else:
            self._validation_state = NodeValidationState.warning
            self._validation_message = 'Missing or invalid input'
            self._out = None
        super().update()
