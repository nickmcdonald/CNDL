import logging as log
import contextlib
import threading
import os

from screeninfo import get_monitors

from ies import IesData, readIesData
from render import render

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from qtpy.QtWidgets import QWidget, QApplication, QLabel, QPushButton
from qtpy.QtWidgets import QFileDialog, QGroupBox, QFormLayout
from qtpy.QtGui import QPixmap

import qtpynodeeditor as nodeeditor
from qtpynodeeditor import (NodeData, NodeDataModel, NodeDataType)
from qtpynodeeditor import (PortType, NodeValidationState, Port)

import theme.styles as styles


class IesNodeData(NodeData):
    'Node data holding Ies data'
    data_type = NodeDataType("ies", "IES")

    def __init__(self, ies=IesData(600, 50, 1, 0)):
        self._ies = ies
        self._lock = threading.RLock()

    @property
    def lock(self):
        return self._lock

    @property
    def ies(self) -> IesData:
        'The ies data'
        return self._ies

    def ies_as_text(self) -> str:
        'Ies as a string'
        return self._ies.getIesOutput(False)


class MathOperationDataModel(NodeDataModel):
    caption_visible = True
    num_ports = {
        'input': 2,
        'output': 1,
    }
    port_caption_visible = True
    data_type = IesNodeData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies1 = None
        self._ies2 = None
        self._result = None
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

    def validation_state(self) -> NodeValidationState:
        return self._validation_state

    def validation_message(self) -> str:
        return self._validation_message

    def compute(self):
        ...


class AdditionModel(MathOperationDataModel):
    name = "Addition"

    def compute(self):
        self._result = IesData(600, 50, 1, 0)


class IesSourceDataModel(NodeDataModel):
    name = "IesSource"
    caption_visible = False
    num_ports = {PortType.input: 0,
                 PortType.output: 1,
                 }
    port_caption = {'output': {0: 'Result'}}
    data_type = IesNodeData.data_type

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies = None

        self._form = QGroupBox("Ies File Source")
        self._layout = QFormLayout()
        self._form.setLayout(self._layout)
        self._open_file_button = QPushButton("Open File")
        self._open_file_button.clicked.connect(self.on_file_button)
        self._layout.addRow("Select File", self._open_file_button)

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
                self._ies = IesNodeData(readIesData(data))


class DisplayUpdateHandler(PatternMatchingEventHandler):

    def __init__(self, update_method):
        super().__init__(patterns=["*/render/img/image.png"])

        self.update = update_method

    def on_modified(self, e):
        log.debug(e)
        self.update()


class IesDisplayModel(NodeDataModel):
    name = "IESDisplay"
    data_type = IesNodeData.data_type
    caption_visible = False
    num_ports = {PortType.input: 1,
                 PortType.output: 0,
                 }
    port_caption = {'input': {0: 'Ies'}}

    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._ies = IesNodeData()
        self._label = QLabel()
        self._label.setMargin(3)
        self._label.setPixmap(QPixmap('render/img/image.png'))
        self._samples = 20
        self._validation_state = NodeValidationState.warning
        self._validation_message = 'Uninitialized'

        event_handler = DisplayUpdateHandler(self.update_image)

        observer = Observer()
        observer.schedule(event_handler, os.getcwd(), recursive=True)
        observer.start()

    def set_in_data(self, data: NodeData, port: Port):
        '''
        New data propagated to the input
        '''
        self._ies = data
        ies_ok = (self._ies is not None and self._ies.data_type.id in ('ies'))

        if ies_ok:
            self._validation_state = NodeValidationState.valid
            self._validation_message = ''
            render(self._ies.ies, self._samples)

        else:
            self._validation_state = NodeValidationState.warning
            self._validation_message = "Missing or incorrect inputs"
            self._label.clear()

    def update_image(self):
        self._label.setPixmap(QPixmap('render/img/image.png'))

    def embedded_widget(self) -> QWidget:
        return self._label


def main(app):
    style = nodeeditor.StyleCollection.from_json(styles.DEFAULT)

    registry = nodeeditor.DataModelRegistry()

    models = (AdditionModel, IesSourceDataModel, IesDisplayModel)
    for model in models:
        registry.register_model(model, category='Operations', style=style)

    scene = nodeeditor.FlowScene(registry=registry, style=style)

    view = nodeeditor.FlowView(scene)
    view.setWindowTitle("CNDL")
    monitor = get_monitors()[0]
    view.resize(monitor.width - monitor.width / 10,
                monitor.height - monitor.height / 10)
    view.move(monitor.width / 30, monitor.height / 30)

    view.show()

    return scene, view


if __name__ == '__main__':
    log.basicConfig(level='DEBUG')
    app = QApplication([])
    scene, view = main(app)
    view.show()
    app.exec_()
