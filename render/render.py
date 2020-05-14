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
import time
from array import array

from multiprocessing import Value, Event
from threading import Thread

from enum import Enum

from scipy.spatial.transform import Rotation

import pyluxcore as lux


class RenderState(Enum):
    WAITING = 1
    RENDERING = 2
    ERROR = 3
    FORCE = 4
    TIMEOUT = 5


class Renderer():

    def __init__(self, update_method):
        self.state = Value('i', RenderState.WAITING.value)
        self.samples = 3
        self.notify = Event()
        self.update_method = update_method
        self.renderThread = None

    def render(self, ies, force, peakintensity=100,
               position=[0.0, 0.5, 3.0], rotation=[0, 0, 0]):
        self.setNewIes(ies, peakintensity)
        self.setLightTransform(position, rotation)
        if not self.renderThread or not self.renderThread.is_alive():
            if not os.path.exists('img/render'):
                os.makedirs('img/render')
            self.renderThread = Thread(target=self.luxRender,
                                       args=(self.notify, self.state))
            self.renderThread.start()

        if self.state.value == RenderState.WAITING.value:
            self.notify.set()

        if force:
            self.state.value = RenderState.FORCE.value

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

    def luxRender(self, notify, state):
        last = 0
        while(True):
            if state.value != RenderState.ERROR.value:
                if state.value != RenderState.TIMEOUT.value:
                    state.value = RenderState.WAITING.value
                    wasNotified = notify.wait(3)
                    if not wasNotified:
                        break
                    notify.clear()

                if time.perf_counter() < last + 1:
                    if state.value != RenderState.FORCE.value:
                        state.value = RenderState.TIMEOUT.value
                        continue
                last = time.perf_counter()

            state.value = RenderState.RENDERING.value

            try:
                props = lux.Properties("scenes/basicIES/basicIES.cfg")
                config = lux.RenderConfig(props)
                session = lux.RenderSession(config)
                session.Start()
                film = session.GetFilm()
                imageBufferFloat = array('f', [0.0] * (film.GetWidth() *
                                                       film.GetHeight() * 3))
                film.GetOutputFloat(lux.FilmOutputType.RGB_IMAGEPIPELINE,
                                    imageBufferFloat)
                imageBufferUChar = array('B', [max(0, min(255,
                                         int(v * 255.0 + 0.5)))
                                         for v in imageBufferFloat])
                size = (film.GetWidth(), film.GetHeight())

                self.update_method(imageBufferUChar, size)

                session.Stop()
            except RuntimeError:
                state.value = RenderState.ERROR.value
            finally:
                if session:
                    session.Stop()
