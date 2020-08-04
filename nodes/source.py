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


from ies import parseIesData, blankIesData, spotlightIesData, noiseIesData
from ies import FalloffMethod, LightDirection

from nodes import IesNodeData

from preview import Preview2D

from qtpy.QtWidgets import (QWidget, QPushButton, QSlider, QLineEdit,
                            QFileDialog, QGroupBox, QFormLayout, QComboBox)

from qtpynodeeditor import (NodeData, NodeDataModel, PortType,
                            NodeValidationState)

from qtpy.QtCore import Qt

import os
import random


class SourceNode(NodeDataModel):
    caption_visible = False
    num_ports = {PortType.input: 0, PortType.output: 1}
    data_type = IesNodeData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._out = IesNodeData(None)

        self._form = QGroupBox()
        self._layout = QFormLayout()
        self._form.setLayout(self._layout)
        self._preview = Preview2D(self._out.data)
        self._layout.addRow(self._preview)

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
        return self._out

    def embedded_widget(self) -> QWidget:
        return self._form

    def update(self):
        if self._out:
            self._preview.update(self._out.data)
        else:
            self._preview.update(None)
        self.data_updated.emit(0)


class PointlightNode(SourceNode):
    name = "Pointlight"
    caption_visible = True

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._out = None

        self._intensitySlider = QSlider(Qt.Horizontal)
        self._intensitySlider.setMinimum(0)
        self._intensitySlider.setMaximum(100)
        self._intensitySlider.setValue(100)
        self._intensitySlider.valueChanged.connect(self.update)
        self._layout.addRow("Intensity", self._intensitySlider)

        self.update()

        def save(self) -> dict:
            doc = super().save()
            doc['intensitySlider'] = self._intensitySlider.value()
            return doc

        def restore(self, state: dict):
            self._intensitySlider.setValue(state['intensitySlider'])

    def update(self):
        self._out = IesNodeData(blankIesData(
                    intensity=self._intensitySlider.value() / 100
        ))
        super().update()

    def setIntensity(self, intensity: int):
        self._intensitySlider.setValue(intensity)


class SpotlightNode(SourceNode):
    name = "Spotlight"
    caption_visible = True

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._out = None

        self._methodCB = QComboBox()
        for method in FalloffMethod:
            self._methodCB.addItem(method.value)
        self._methodCB.currentIndexChanged.connect(self.update)
        self._methodCB.setToolTip("Select the interpolation method for the" +
                                  "falloff on the edges of the spotlight")
        self._layout.addRow("Falloff Method", self._methodCB)

        self._dirCB = QComboBox()
        for direction in LightDirection:
            self._dirCB.addItem(direction.value)
        self._dirCB.currentIndexChanged.connect(self.update)
        self._dirCB.setToolTip("Select whether the light points up, or down")
        self._layout.addRow("Direction", self._dirCB)

        self._angleSlider = QSlider(Qt.Horizontal)
        self._angleSlider.setMinimum(0)
        self._angleSlider.setMaximum(90)
        self._angleSlider.setValue(45)
        self._angleSlider.valueChanged.connect(self.update)
        self._layout.addRow("Angle", self._angleSlider)

        self._falloffSlider = QSlider(Qt.Horizontal)
        self._falloffSlider.setMinimum(0)
        self._falloffSlider.setMaximum(100)
        self._falloffSlider.setValue(20)
        self._falloffSlider.valueChanged.connect(self.update)
        self._layout.addRow("Falloff", self._falloffSlider)

        self.update()

    def save(self) -> dict:
        doc = super().save()
        doc['methodCB'] = self._methodCB.currentText()
        doc['dirCB'] = self._dirCB.currentText()
        doc['angleSlider'] = self._angleSlider.value()
        doc['falloffSlider'] = self._falloffSlider.value()
        return doc

    def restore(self, state: dict):
        self._methodCB.setCurrentText(state['methodCB'])
        self._dirCB.setCurrentText(state['dirCB'])
        self._angleSlider.setValue(state['angleSlider'])
        self._falloffSlider.setValue(state['falloffSlider'])

    def update(self):
        self._out = IesNodeData(spotlightIesData(
                    self._angleSlider.value(),
                    self._falloffSlider.value() / 100.0,
                    falloffMethod=FalloffMethod(self._methodCB.currentText()),
                    lightDirection=LightDirection(self._dirCB.currentText())
        ))
        super().update()

    def setAngle(self, angle: int):
        self._angleSlider.setValue(angle)

    def setFalloff(self, falloff: int):
        self._falloffSlider.setValue(falloff)

    def setFalloffMethod(self, method: FalloffMethod):
        self._methodCB.setCurrentText(method.value)

    def setLightDiretion(self, direction: LightDirection):
        self._dirCB.setCurrentText(direction.value)


class FileNode(SourceNode):
    name = "File Input"
    caption_visible = True

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._out = None

        self._open_file_button = QPushButton("Open File")
        self._open_file_button.clicked.connect(self.on_file_button)
        self._open_file_button.setToolTip("Open new IES file")
        self._open_file_text = QLineEdit()
        self._open_file_text.setReadOnly(True)
        self._layout.addRow(self._open_file_button, self._open_file_text)
        self._validation_state = NodeValidationState.warning
        self._validation_message = 'No file selected'

    def save(self) -> dict:
        doc = super().save()
        doc['open_file_text'] = self._open_file_text.text()
        return doc

    def restore(self, state: dict):
        self._open_file_text.setText(state['open_file_text'])
        self._loadFile(state['open_file_text'])
        self.update()

    def validation_state(self) -> NodeValidationState:
        return self._validation_state

    def validation_message(self) -> str:
        return self._validation_message

    def on_file_button(self):
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptOpen)
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter('IES files (*.ies)')

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self._open_file_text.setText(filenames[0])
            self._loadFile(filenames[0])
            self.update()
            return

        self._validation_state = NodeValidationState.warning
        self._validation_message = 'No file selected'

    def _loadFile(self, filename):
        f = open(filename, 'r')
        with f:
            data = f.read()
            try:
                self._out = IesNodeData(parseIesData(data))
                self._validation_state = NodeValidationState.valid
                self._validation_message = ''
            except Exception:
                self._out = None
                self._validation_state = NodeValidationState.warning
                self._validation_message = 'Invalid IES file'


class FolderNode(SourceNode):
    name = "Folder Input"
    caption_visible = True

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._out = None

        self._open_folder_button = QPushButton("Open Folder")
        self._open_folder_button.clicked.connect(self.on_folder_button)
        self._open_folder_button.setToolTip("Open folder")
        self._open_folder_text = QLineEdit()
        self._open_folder_text.setReadOnly(True)
        self._layout.addRow(self._open_folder_button, self._open_folder_text)

        self._filesCB = QComboBox()
        self._filesCB.currentIndexChanged.connect(self.update)
        self._filesCB.setToolTip("Select IES File")
        self._filesCB.setEnabled(False)
        self._layout.addRow("IES File", self._filesCB)

        self._validation_state = NodeValidationState.warning
        self._validation_message = 'No folder selected'

    def save(self) -> dict:
        doc = super().save()
        doc['open_folder_text'] = self._open_folder_text.text()
        return doc

    def restore(self, state: dict):
        self._open_folder_text.setText(state['open_folder_text'])
        folderPath = state['open_folder_text']
        files = [f for f in os.listdir(folderPath) if f.endswith(".ies")]
        self._filesCB.clear()
        self._filesCB.addItems(files)
        self._filesCB.setEnabled(True)
        self.update()

    def validation_state(self) -> NodeValidationState:
        return self._validation_state

    def validation_message(self) -> str:
        return self._validation_message

    def on_folder_button(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)

        if dlg.exec_():
            folderPath = dlg.selectedFiles()[0]
            self._open_folder_text.setText(folderPath)
            files = [f for f in os.listdir(folderPath) if f.endswith(".ies")]
            self._filesCB.clear()
            self._filesCB.addItems(files)
            self._filesCB.setEnabled(True)
            self.update()
            return

        self._validation_state = NodeValidationState.warning
        self._validation_message = 'No file selected'

    def update(self):
        self._loadFile(self._open_folder_text.text() + "/" +
                       self._filesCB.currentText())
        super().update()

    def _loadFile(self, filename):
        f = open(filename, 'r')
        print(filename)
        with f:
            data = f.read()
            try:
                self._out = IesNodeData(parseIesData(data))
                self._validation_state = NodeValidationState.valid
                self._validation_message = ''
            except Exception:
                self._out = None
                self._validation_state = NodeValidationState.warning
                self._validation_message = 'Invalid IES file'


class NoiseNode(SourceNode):
    name = "Noise"
    caption_visible = True

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)

        self._latscale = QSlider(Qt.Horizontal)
        self._latscale.setMinimum(5)
        self._latscale.setMaximum(100)
        self._latscale.setValue(30)
        self._latscale.valueChanged.connect(self.update)
        self._layout.addRow("Scale", self._latscale)

        self._latintensity = QSlider(Qt.Horizontal)
        self._latintensity.setMinimum(0)
        self._latintensity.setMaximum(100)
        self._latintensity.setValue(30)
        self._latintensity.valueChanged.connect(self.update)
        self._layout.addRow("Intensity", self._latintensity)

        self._seed = 0
        self._seed_button = QPushButton("Random Seed")
        self._seed_button.clicked.connect(self.on_seed_button)
        self._seed_button.setToolTip("Set a new random seed for the noise")
        self._layout.addRow(self._seed_button)

        self.update()

    def save(self) -> dict:
        doc = super().save()
        doc['seed'] = self._seed
        doc['latscale'] = self._latscale.value()
        doc['latintensity'] = self._latintensity.value()
        return doc

    def restore(self, state: dict):
        self._seed = state['seed']
        self._latscale.setValue(state['latscale'])
        self._latintensity.setValue(state['latintensity'])

    def on_seed_button(self):
        random.seed()
        self._seed = random.randrange(0, 1000, 1)
        self.update()

    def update(self):
        self._out = IesNodeData(noiseIesData(
                                self._latscale.value(),
                                self._latintensity.value() / 100,
                                1,
                                1,
                                seed=self._seed))
        super().update()
