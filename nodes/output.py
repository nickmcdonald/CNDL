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

from qtpy.QtWidgets import (QWidget, QLabel, QFileDialog, QTabWidget,
                            QPushButton, QGroupBox, QFormLayout, QLineEdit,
                            QCheckBox, QSlider, QSpacerItem)
from qtpy.QtGui import QPixmap, QDoubleValidator
from qtpy.QtCore import Qt

from qtpynodeeditor import NodeData, NodeDataModel
from qtpynodeeditor import PortType, Port

from nodes import IesNodeData


class DisplayUpdateHandler(PatternMatchingEventHandler):

    def __init__(self, update_method):
        super().__init__(patterns=["*/img/render/renderimage.png"])

        self.update = update_method

    def on_modified(self, e):
        self.update()


class DisplayNode(NodeDataModel):
    name = "Output Render Display"
    caption_visible = False
    port_caption_visible = False
    data_type = IesNodeData.data_type
    num_ports = {PortType.input: 1, PortType.output: 0}

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies = None

        self._tabs = QTabWidget()

        self._render_form = QGroupBox()
        self._render_layout = QFormLayout()
        self._render_form.setLayout(self._render_layout)

        self._render_view = QLabel()
        self._render_view.setPixmap(QPixmap('img/RenderPlaceholder.png'))
        self._render_passes = 2
        self._renderer = Renderer()
        event_handler = DisplayUpdateHandler(self.update_image)
        observer = Observer()
        observer.schedule(event_handler, os.getcwd(), recursive=True)
        observer.start()
        self._light_z_pos = QSlider(Qt.Vertical)
        self._light_z_pos.setMinimum(-60)
        self._light_z_pos.setMaximum(60)
        self._light_z_pos.setValue(30)
        self._light_z_pos.valueChanged.connect(self.update)
        self._render_layout.addRow(self._render_view, self._light_z_pos)

        self._render_controls_form = QGroupBox()
        self._render_controls_layout = QFormLayout()
        self._render_controls_form.setLayout(self._render_controls_layout)

        self._light_x_pos = QSlider(Qt.Horizontal)
        self._light_x_pos.setMinimum(-60)
        self._light_x_pos.setMaximum(60)
        self._light_x_pos.setValue(0)
        self._light_x_pos.valueChanged.connect(self.update)
        self._render_controls_layout.addRow("Position X", self._light_x_pos)

        self._light_y_pos = QSlider(Qt.Horizontal)
        self._light_y_pos.setMinimum(-5)
        self._light_y_pos.setMaximum(60)
        self._light_y_pos.setValue(0)
        self._light_y_pos.valueChanged.connect(self.update)
        self._render_controls_layout.addRow("Position Y", self._light_y_pos)

        self._render_controls_layout.addItem(QSpacerItem(10, 10))

        self._light_x_rot = QSlider(Qt.Horizontal)
        self._light_x_rot.setMinimum(-180)
        self._light_x_rot.setMaximum(180)
        self._light_x_rot.setValue(0)
        self._light_x_rot.valueChanged.connect(self.update)
        self._render_controls_layout.addRow("Rotation X", self._light_x_rot)

        self._light_y_rot = QSlider(Qt.Horizontal)
        self._light_y_rot.setMinimum(-180)
        self._light_y_rot.setMaximum(180)
        self._light_y_rot.setValue(0)
        self._light_y_rot.valueChanged.connect(self.update)
        self._render_controls_layout.addRow("Rotation Y", self._light_y_rot)

        self._light_z_rot = QSlider(Qt.Horizontal)
        self._light_z_rot.setMinimum(-180)
        self._light_z_rot.setMaximum(180)
        self._light_z_rot.setValue(0)
        self._light_z_rot.valueChanged.connect(self.update)
        self._render_controls_layout.addRow("Rotation Z", self._light_z_rot)

        self._render_layout.addRow(self._render_controls_form)

        self._tabs.addTab(self._render_form, "Render")

        self._export_form = QGroupBox()
        self._export_layout = QFormLayout()
        self._export_form.setLayout(self._export_layout)

        self._brightness_text = QLineEdit()
        self._brightness_text.setText("100")
        self._brightness_text.setToolTip("The <strong>peak</strong> " +
                                         "brightness of the light in Candelas")
        self._brightness_text.setValidator(QDoubleValidator())
        self._export_layout.addRow("Brightness (Candelas)",
                                   self._brightness_text)

        self._export_file_button = QPushButton("Export")
        self._export_file_button.clicked.connect(self.on_file_button)
        self._export_file_button.setEnabled(False)
        self._export_file_button.setToolTip("Select new export file name")
        self._export_file_text = QLineEdit()
        self._export_file_text.setReadOnly(True)
        self._export_layout.addRow(self._export_file_button,
                                   self._export_file_text)
        self._auto_export = QCheckBox()
        self._auto_export.setChecked(False)
        self._auto_export.setWindowFlags(Qt.ToolTip)
        self._auto_export.setToolTip("Automatically re-export when you make" +
                                     "a change")
        self._export_layout.addRow("Auto Export", self._auto_export)

        self._comp_mode = QCheckBox()
        self._comp_mode.setChecked(False)
        self._comp_mode.setWindowFlags(Qt.ToolTip)
        self._comp_mode.setToolTip("Some renderers (notably Arnold) have " +
                                   "improper ies file support. This should " +
                                   "fix it.\nIf you still have issues after," +
                                   " please email nick@lazymorninggames.com")
        self._export_layout.addRow("Compatibility Mode", self._comp_mode)

        self._tabs.addTab(self._export_form, "Export")

    def setLightPositionX(self, val):
        self._light_x_pos.setValue(val)

    def setLightPositionY(self, val):
        self._light_y_pos.setValue(val)

    def setLightPositionZ(self, val):
        self._light_z_pos.setValue(val)

    def setLightRotationX(self, val):
        self._light_x_rot.setValue(val)

    def setLightRotationY(self, val):
        self._light_y_rot.setValue(val)

    def setLightRotationZ(self, val):
        self._light_z_rot.setValue(val)

    def save(self) -> dict:
        doc = super().save()
        doc['light_x_pos'] = self._light_x_pos.value()
        doc['light_y_pos'] = self._light_y_pos.value()
        doc['light_z_pos'] = self._light_z_pos.value()
        doc['light_x_rot'] = self._light_x_rot.value()
        doc['light_y_rot'] = self._light_y_rot.value()
        doc['light_z_rot'] = self._light_z_rot.value()
        doc['brightness_text'] = self._brightness_text.text()
        doc['export_file_text'] = self._export_file_text.text()
        doc['auto_export'] = self._auto_export.isChecked()
        return doc

    def restore(self, state: dict):
        self._light_x_pos.setValue(state['light_x_pos'])
        self._light_y_pos.setValue(state['light_y_pos'])
        self._light_z_pos.setValue(state['light_z_pos'])
        self._light_x_rot.setValue(state['light_x_rot'])
        self._light_y_rot.setValue(state['light_y_rot'])
        self._light_z_rot.setValue(state['light_z_rot'])
        self._brightness_text.setText(state['brightness_text'])
        self._export_file_text.setText(state['export_file_text'])
        self._auto_export.setChecked(state['auto_export'])

    def on_file_button(self):
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilter('IES files (*.ies)')

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            if(len(filenames) > 0):
                self._export_file_text.setText(filenames[0])
                self.export()

    def export(self):
        if len(self._export_file_text.text()) < 1:
            return
        f = open(self._export_file_text.text(), 'w')
        with f:
            if self._ies:
                try:
                    f.write(self._ies.data.getIesOutput(float(
                            self._brightness_text.text())))
                except ValueError:
                    f.write(self._ies.data.getIesOutput(100))
            f.close()

    def execute_render(self):
        self._renderer.render(self._ies.data,
                              position=[self._light_x_pos.value() * -0.09,
                                        0.5 + self._light_y_pos.value() * 0.09,
                                        3 + self._light_z_pos.value() * 0.049],
                              rotation=[self._light_x_rot.value(),
                                        self._light_y_rot.value(),
                                        self._light_z_rot.value()],
                              samples=self._render_passes)

    def set_in_data(self, data: NodeData, port: Port):
        '''
        New data propagated to the input
        '''
        self._ies = data
        self.update()

    def update(self):
        ies_ok = (self._ies is not None and self._ies.data_type.id in ('ies'))

        if ies_ok:
            self._export_file_button.setEnabled(True)
            self.execute_render()
            if self._auto_export.isChecked():
                self.export()
        else:
            self._export_file_button.setEnabled(False)
            self._render_view.setPixmap(QPixmap('img/RenderPlaceholder.png'))

    def update_image(self):
        self._render_view.setPixmap(QPixmap('img/render/renderimage.png'))

    def embedded_widget(self) -> QWidget:
        return self._tabs
