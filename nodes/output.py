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
                            QCheckBox)
from qtpy.QtGui import QPixmap, QDoubleValidator

from qtpynodeeditor import NodeData, NodeDataModel
from qtpynodeeditor import PortType, Port

from nodes import IesNodeData


class DisplayUpdateHandler(PatternMatchingEventHandler):

    def __init__(self, update_method):
        super().__init__(patterns=["*/render/img/image.png"])

        self.update = update_method

    def on_modified(self, e):
        self.update()


class DisplayNode(NodeDataModel):
    name = "IESDisplay"
    data_type = IesNodeData.data_type
    caption_visible = False
    num_ports = {PortType.input: 1, PortType.output: 0}
    port_caption = {'input': {0: 'Ies'}}

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies = None

        self._tabs = QTabWidget()

        self._render_view = QLabel()
        self._render_view.setPixmap(QPixmap('img/RenderPlaceholder.png'))
        self._render_passes = 2
        self._renderer = Renderer()
        event_handler = DisplayUpdateHandler(self.update_image)
        observer = Observer()
        observer.schedule(event_handler, os.getcwd(), recursive=True)
        observer.start()

        self._tabs.addTab(self._render_view, "Render")

        self._export_form = QGroupBox()
        self._layout = QFormLayout()
        self._export_form.setLayout(self._layout)

        self._brightness_text = QLineEdit()
        self._brightness_text.setText("80")
        self._brightness_text.setValidator(QDoubleValidator())
        self._layout.addRow("Brightness (Candelas)", self._brightness_text)

        self._export_file_button = QPushButton("Export")
        self._export_file_button.clicked.connect(self.on_file_button)
        self._export_file_button.setEnabled(False)
        self._export_file_text = QLineEdit()
        self._export_file_text.setReadOnly(True)
        self._layout.addRow(self._export_file_button, self._export_file_text)
        self._auto_export = QCheckBox()
        self._auto_export.setChecked(False)
        self._layout.addRow("Auto Export", self._auto_export)

        self._tabs.addTab(self._export_form, "Export")

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
                    f.write(self._ies.data.getIesOutput(80))
            f.close()

    def set_in_data(self, data: NodeData, port: Port):
        '''
        New data propagated to the input
        '''
        self._ies = data
        ies_ok = (self._ies is not None and self._ies.data_type.id in ('ies'))

        if ies_ok:
            self._export_file_button.setEnabled(True)
            self._renderer.render(self._ies.data, 1000, self._render_passes)
            if self._auto_export.isChecked():
                self.export()
        else:
            self._export_file_button.setEnabled(False)
            self._render_view.setPixmap(QPixmap('img/RenderPlaceholder.png'))

    def update_image(self):
        self._render_view.setPixmap(QPixmap('render/img/image.png'))

    def embedded_widget(self) -> QWidget:
        return self._tabs
