from ies import IesData

from qtpynodeeditor import NodeData, NodeDataType

import threading


class IesNodeData(NodeData):
    'Node data holding Ies data'
    data_type = NodeDataType("ies", "")

    def __init__(self, ies: IesData = None):
        self._ies = ies
        self._lock = threading.RLock()

    @property
    def lock(self):
        return self._lock

    @property
    def data(self) -> IesData:
        'The ies data'
        return self._ies

    def ies_as_text(self) -> str:
        'Ies as a string'
        return self._ies.getIesOutput(False)
