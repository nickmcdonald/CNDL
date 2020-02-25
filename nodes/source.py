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


from ies import parseIesData, blankIesData

from nodes import IesNodeData

from preview import Preview2D

from qtpy.QtWidgets import QWidget, QPushButton
from qtpy.QtWidgets import QFileDialog, QGroupBox, QFormLayout

from qtpynodeeditor import NodeData, NodeDataModel, PortType
from qtpy.QtGui import QColor


class IesSourceDataModel(NodeDataModel):
    name = "IesDefaultSource"
    caption_visible = False
    num_ports = {PortType.input: 0, PortType.output: 1}
    port_caption = {'output': {0: 'Result'}}
    data_type = IesNodeData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies = IesNodeData(blankIesData())

        self._form = QGroupBox("Ies Source")
        self._form.setStyleSheet("background-color:rgba(0,0,0,0%);")
        self._layout = QFormLayout()
        self._form.setLayout(self._layout)
        self._preview = Preview2D(self._ies.ies)
        self._layout.addRow(self._preview)

        self.update()

    def save(self) -> dict:
        # save the state
        doc = super().save()
        if self._ies:
            doc['ies'] = self._ies.ies
        return doc

    def restore(self, state: dict):
        # restore the state
        pass

    def out_data(self, port: int) -> NodeData:
        '''
        The data output from this node
        Parameters
        ----------
        port : int
        Returns
        -------
        value : NodeData
        '''
        return self._ies

    def embedded_widget(self) -> QWidget:
        return self._form

    def update(self):
        self._preview.update(self._ies.ies)
        self.data_updated.emit(0)


class IesDefaultSourceDataModel(IesSourceDataModel):
    name = "Default Source"

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._open_file_button = QPushButton("create")
        self._open_file_button.clicked.connect(self.on_file_button)
        self._layout.addRow("create", self._open_file_button)
        self._ies = IesNodeData(blankIesData())

    def on_file_button(self):
        self.update()


class IesFileSourceDataModel(IesSourceDataModel):
    name = "File Source"

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies = None

        self._open_file_button = QPushButton("Open File")
        self._open_file_button.clicked.connect(self.on_file_button)
        self._layout.addRow("Select File", self._open_file_button)

    def on_file_button(self):
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptOpen)
        dlg.setFileMode(QFileDialog.AnyFile)
        # dlg.setFilter(u'IES files (*.ies)')

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')
            with f:
                data = f.read()
                self._ies = IesNodeData(parseIesData(data))
                self.update()
