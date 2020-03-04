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


from multiprocessing import Process, Value, Event

from enum import Enum

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

                elapsed = stats.Get("stats.renderengine.time").GetFloat()
                currentPass = stats.Get("stats.renderengine.pass").GetInt()

                if currentPass > previousPass:
                    session.GetFilm().Save()
                    previousPass = currentPass
                if currentPass >= samples.value or elapsed > 3:
                    break

            session.Stop()
        except RuntimeError:
            state.value = RenderState.INTERRUPT.value
        finally:
            if session:
                session.Stop()


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
        f = open("scenes/render.ies", "w")
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
