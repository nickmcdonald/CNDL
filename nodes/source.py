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


from ies import parseIesData, blankIesData, spotlightIesData
from ies import FalloffMethod, LightDirection

from nodes import IesNodeData

from preview import Preview2D

from qtpy.QtWidgets import QWidget, QPushButton, QSlider
from qtpy.QtWidgets import QFileDialog, QGroupBox, QFormLayout, QComboBox

from qtpynodeeditor import NodeData, NodeDataModel, PortType

from qtpy.QtCore import Qt


class IesSourceDataModel(NodeDataModel):
    name = "IesDefaultSource"
    caption_visible = False
    num_ports = {PortType.input: 0, PortType.output: 1}
    port_caption = {'output': {0: 'Result'}}
    data_type = IesNodeData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies = IesNodeData(blankIesData())

        self._form = QGroupBox()
        self._layout = QFormLayout()
        self._form.setLayout(self._layout)
        self._preview = Preview2D(self._ies.ies)
        self._layout.addRow(self._preview)

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


class IesBlankSourceDataModel(IesSourceDataModel):
    name = "Blank Source"

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies = IesNodeData(blankIesData())

        self._intensitySlider = QSlider(Qt.Horizontal)
        self._layout.addRow(self._intensitySlider)
        self._intensitySlider.setMinimum(0)
        self._intensitySlider.setMaximum(100)
        self._intensitySlider.setValue(0)
        self._intensitySlider.valueChanged.connect(self.update)

        self.update()

    def update(self):
        self._ies = IesNodeData(blankIesData(
                    intensity=self._intensitySlider.value() / 100
        ))
        super().update()


class IesSpotlightSourceDataModel(IesSourceDataModel):
    name = "Spotlight Source"

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies = IesNodeData(spotlightIesData(45, 0.2))

        self._methodCB = QComboBox()
        self._layout.addRow(self._methodCB)
        for method in FalloffMethod:
            self._methodCB.addItem(method.value)
        self._methodCB.currentIndexChanged.connect(self.update)

        self._dirCB = QComboBox()
        self._layout.addRow(self._dirCB)
        for direction in LightDirection:
            self._dirCB.addItem(direction.value)
        self._dirCB.currentIndexChanged.connect(self.update)

        self._angleSlider = QSlider(Qt.Horizontal)
        self._layout.addRow(self._angleSlider)
        self._angleSlider.setMinimum(0)
        self._angleSlider.setMaximum(90)
        self._angleSlider.setValue(45)
        self._angleSlider.valueChanged.connect(self.update)

        self._falloffSlider = QSlider(Qt.Horizontal)
        self._layout.addRow(self._falloffSlider)
        self._falloffSlider.setMinimum(0)
        self._falloffSlider.setMaximum(100)
        self._falloffSlider.setValue(20)
        self._falloffSlider.valueChanged.connect(self.update)

        self.update()

    def update(self):
        self._ies = IesNodeData(spotlightIesData(
                    self._angleSlider.value(),
                    self._falloffSlider.value() / 100.0,
                    falloffMethod=FalloffMethod(self._methodCB.currentText()),
                    lightDirection=LightDirection(self._dirCB.currentText())
        ))
        super().update()


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
