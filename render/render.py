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


from multiprocessing import Value, Event
from threading import Thread
from array import array
from enum import Enum
from PIL import Image

import pyluxcore as lux


class RenderState(Enum):
    WAITING = 1
    RENDERING = 2
    INTERRUPT = 3


class Renderer():

    def _luxRender(self, notify, state):

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

    def render(self, ies, peakIntensity):
        f = open("scenes/render.ies", "w")
        f.write(ies.getIesOutput(peakIntensity))
        f.close()
        self._updateRenderProcess()
