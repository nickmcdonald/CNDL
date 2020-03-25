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

import json

from qtpy.QtWidgets import QFileDialog

from qtpynodeeditor import FlowScene


def saveCNDLFile(scene: FlowScene, filename: str = None) -> str:
    if filename is None:
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilter('CNDL files (*.cndl)')

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            if(len(filenames) > 0):
                print(filenames[0])
                with open(filenames[0], 'w') as f:
                    json.dump(scene.__getstate__(), f,
                              default=lambda o: '<not serializable>')
                    return filenames[0]
    else:
        with open(filename, 'w') as f:
            json.dump(scene.__getstate__(), f,
                      default=lambda o: '<not serializable>')
            return filename

    return None


def openCNDLFile(scene: FlowScene) -> str:
    dlg = QFileDialog()
    dlg.setAcceptMode(QFileDialog.AcceptOpen)
    dlg.setFileMode(QFileDialog.ExistingFile)
    dlg.setNameFilter('CNDL files (*.cndl)')

    if dlg.exec_():
        filenames = dlg.selectedFiles()
        if(len(filenames) > 0):
            with open(filenames[0], 'rt') as f:
                doc = json.load(f)
                scene.__setstate__(doc)
                return filenames[0]

    return None
