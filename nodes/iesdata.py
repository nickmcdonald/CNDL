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


from ies import IesData

from qtpynodeeditor import NodeData, NodeDataType

import threading


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
