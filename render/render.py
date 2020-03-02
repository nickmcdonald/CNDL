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

from multiprocessing import Value, Event
from threading import Thread
from array import array
from enum import Enum
from PIL import Image

from scipy.spatial.transform import Rotation

import pyluxcore as lux


class RenderState(Enum):
    WAITING = 1
    RENDERING = 2
    INTERRUPT = 3


def luxRender(notify, samples, state):

    while(True):

        if state.value != RenderState.INTERRUPT.value:
            state.value = RenderState.WAITING.value
            wasNotified = notify.wait(3)
            if not wasNotified:
                break
            notify.clear()
        state.value = RenderState.RENDERING.value
        session = None
        try:
            props = lux.Properties("scenes/basicIES/basicIES.cfg")
            config = lux.RenderConfig(props)
            session = lux.RenderSession(config)
            session.Start()
            previousPass = -1
            while True:
                if state.value == RenderState.INTERRUPT.value:
                    break
                session.UpdateStats()
                stats = session.GetStats()

        while(True):

            if state.value != RenderState.INTERRUPT.value:
                state.value = RenderState.WAITING.value
                wasNotified = notify.wait(3)
                if not wasNotified:
                    break
                notify.clear()
            state.value = RenderState.RENDERING.value

            try:
                props = lux.Properties("scenes/basicIES/basicIES.cfg")
                config = lux.RenderConfig(props)
                session = lux.RenderSession(config)
                session.Start()
                i = 0
                while i < 10:
                    i += 1
                    if state.value == RenderState.INTERRUPT.value:
                        break

                    session.WaitNewFrame()

                    film = session.GetFilm()
                    # img = GetImagePipelineImage(film)
                    # img.save("xxxxxx.png")
                    # self._outputCallback(img)

                    imageBufferFloat = array('f', [0.0] * (film.GetWidth() * film.GetHeight() * 3))
                    film.GetOutputFloat(lux.FilmOutputType.RGB_IMAGEPIPELINE, imageBufferFloat)
                    imageBufferUChar = array('B', [max(0, min(255, int(v * 255.0 + 0.5))) for v in imageBufferFloat])
                    size = (film.GetWidth(), film.GetHeight())
                    self._outputCallback(imageBufferUChar, size)

                    # data = array('f', [0.0] * (film.GetWidth() * film.GetHeight() * 3))
                    # film.GetOutputFloat(lux.FilmOutputType.RGB_IMAGEPIPELINE, data)
                    # print("sending data: " + str(len(data)) + " bytes")
                    # self._outputCallback(data)

                session.Stop()
            except RuntimeError as e:
                print(e)
                state.value = RenderState.INTERRUPT.value
        print("Render Thread killed")

    def __init__(self, callback):
        self._state = Value('i', RenderState.WAITING.value)
        self._notify = Event()
        self._renderProcess = None
        self._outputCallback = callback

    def _updateRenderProcess(self):
        if not self._renderProcess or not self._renderProcess.is_alive():

            self._renderProcess = Thread(target=self._luxRender,
                                         args=(self._notify,
                                               self._state))
            self._renderProcess.start()
        if self._state.value == RenderState.WAITING.value:
            self._notify.set()
        else:
            self._state.value = RenderState.INTERRUPT.value


class Renderer():

    def __init__(self):
        self.state = Value('i', RenderState.WAITING.value)
        self.samples = Value('i', 2)
        self.notify = Event()
        self.renderProcess = None

    def render(self, ies, peakintensity=100,
               position=[0.0, 0.5, 3.0], rotation=[0, 0, 0], samples=2):
        self.setNewIes(ies, peakintensity)
        self.setLightTransform(position, rotation)
        if not self.renderProcess or not self.renderProcess.is_alive():
            if not os.path.exists('img/render'):
                os.makedirs('img/render')
            self.renderProcess = Process(target=luxRender,
                                         args=(self.notify,
                                               self.samples,
                                               self.state))
            self.renderProcess.start()
        self.samples.value = samples
        if self.state.value == RenderState.WAITING.value:
            self.notify.set()
        else:
            self.state.value = RenderState.INTERRUPT.value

    def setNewIes(self, ies, peakintensity):
        f = open("scenes/basicIES/render.ies", "w")
        f.write(ies.getIesOutput(peakintensity))
        f.close()

    def setLightTransform(self, position, rotation):
        fin = open("scenes/basicIES/basicIES.scn.preformat", 'r')
        preformat = fin.read()
        fin.close()

        rot = Rotation.from_euler('xyz', rotation, degrees=True).as_matrix()

        trans = "{0:.2f} {1:.2f} {2:.2f} 0.0 {3:.2f} {4:.2f} {5:.2f} 0.0 "
        trans += "{6:.2f} {7:.2f} {8:.2f} 0.0 {9:.2f} {10:.2f} {11:.2f} 1.0"
        trans = trans.format(rot[0][0],
                             rot[0][1],
                             rot[0][2],
                             rot[1][0],
                             rot[1][1],
                             rot[1][2],
                             rot[2][0],
                             rot[2][1],
                             rot[2][2],
                             position[0], position[1], position[2])

        fout = open("scenes/basicIES/basicIES.scn", 'w')
        fout.write(preformat.format(trans))
        fout.close()
